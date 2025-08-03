# This code is based on the revised code from fastchat based on QwenLM/Qwen

from dataclasses import dataclass, field
import json
import math
import logging
import os
from typing import Dict, Optional, List
import torch
from torch.utils.data import Dataset
from deepspeed import zero
from deepspeed.runtime.zero.partition_parameters import ZeroParamStatus
import transformers
from transformers.integrations import deepspeed
from transformers import Trainer, GPTQConfig
from transformers.trainer_pt_utils import LabelSmoother
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from accelerate.utils import DistributedType
from template import *
from tokenizer_preprocess import *

IGNORE_TOKEN_ID = LabelSmoother.ignore_index

@dataclass
class ModelArguments:
    model_name_or_path: Optional[str] = field(default="Qwen/Qwen-7B")


@dataclass
class DataArguments:
    data_path: str = field(
        default=None, metadata={"help": "Path to the training data."}
    )
    eval_data_path: str = field(
        default=None, metadata={"help": "Path to the evaluation data."}
    )
    lazy_preprocess: bool = False
    language: str = field(
        default=None, metadata={"help": "en or zh"}
    )
    tuning_mode: str = field(
        default="all", metadata={"help": "all or phrase_only or leakage_only"}
    )

@dataclass
class TrainingArguments(transformers.TrainingArguments):
    cache_dir: Optional[str] = field(default=None)
    optim: str = field(default="adamw_torch")
    model_max_length: int = field(
        default=8192,
        metadata={
            "help": "Maximum sequence length. Sequences will be right padded (and possibly truncated)."
        },
    )
    use_lora: bool = False


@dataclass
class LoraArguments:
    lora_r: int = 16
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = field(
        default_factory=lambda: ["q_proj", "k_proj", "v_proj", "o_proj", "up_proj", "gate_proj", "down_proj"]
    )
    lora_weight_path: str = ""
    lora_bias: str = "none"
    q_lora: bool = False


def maybe_zero_3(param):
    if hasattr(param, "ds_id"):
        assert param.ds_status == ZeroParamStatus.NOT_AVAILABLE
        with zero.GatheredParameters([param]):
            param = param.data.detach().cpu().clone()
    else:
        param = param.detach().cpu().clone()
    return param


# Borrowed from peft.utils.get_peft_model_state_dict
def get_peft_state_maybe_zero_3(named_params, bias):
    if bias == "none":
        to_return = {k: t for k, t in named_params if "lora_" in k}
    elif bias == "all":
        to_return = {k: t for k, t in named_params if "lora_" in k or "bias" in k}
    elif bias == "lora_only":
        to_return = {}
        maybe_lora_bias = {}
        lora_bias_names = set()
        for k, t in named_params:
            if "lora_" in k:
                to_return[k] = t
                bias_name = k.split("lora_")[0] + "bias"
                lora_bias_names.add(bias_name)
            elif "bias" in k:
                maybe_lora_bias[k] = t
        for k, t in maybe_lora_bias:
            if bias_name in lora_bias_names:
                to_return[bias_name] = t
    else:
        raise NotImplementedError
    to_return = {k: maybe_zero_3(v) for k, v in to_return.items()}
    return to_return


local_rank = None

def rank0_print(*args):
    if local_rank == 0:
        print(*args)


def safe_save_model_for_hf_trainer(trainer: transformers.Trainer, output_dir: str, bias="none"):
    """Collects the state dict and dump to disk."""
    # check if zero3 mode enabled
    if deepspeed.is_deepspeed_zero3_enabled():
        state_dict = trainer.model_wrapped._zero3_consolidated_16bit_state_dict()
    else:
        if trainer.args.use_lora:
            state_dict = get_peft_state_maybe_zero_3(
                trainer.model.named_parameters(), bias
            )
        else:
            state_dict = trainer.model.state_dict()
    if trainer.args.should_save and trainer.args.local_rank == 0:
        trainer._save(output_dir, state_dict=state_dict)


def preprocess(
    sources,
    tokenizer: transformers.PreTrainedTokenizer,
    max_len: int,
    system_message: str = "You are a helpful assistant."
) -> Dict:
    model_name_or_path = tokenizer.name_or_path.lower()
    if "qwen" in model_name_or_path:
        return preprocess_qwen(sources, tokenizer, max_len, system_message)
    if "llama" in model_name_or_path:
        return preprocess_llama(sources, tokenizer, max_len, system_message)
    raise Exception('Do not support the tokenizer: {}'.format(model_name_or_path))
    
class LazySupervisedDataset(Dataset):
    """Dataset for supervised fine-tuning."""

    def __init__(self, raw_data, tokenizer: transformers.PreTrainedTokenizer, max_len: int, language: str, tuning_mode: str = "all"):
        super(LazySupervisedDataset, self).__init__()
        self.tokenizer = tokenizer
        self.max_len = max_len

        system_message_dict = {
            "en": {
                "all": DETECT_TRAIN_SYS_TEMPLATE_EN,
                "phrase_only": DETECT_TRAIN_SYS_PHRASE_ONLY_TEMPLATE_EN,
                "leakage_only": DETECT_TRAIN_SYS_LEAKAGE_ONLY_TEMPLATE_EN
            },
            "zh":{
                "all": DETECT_TRAIN_SYS_TEMPLATE_ZH,
                "phrase_only": DETECT_TRAIN_SYS_PHRASE_ONLY_TEMPLATE_ZH,
                "leakage_only": DETECT_TRAIN_SYS_LEAKAGE_ONLY_TEMPLATE_ZH
            }
        }

        rank0_print("Formatting inputs...Skip in lazy mode")
        self.tokenizer = tokenizer
        if language == "en":
            self.template = DETECT_TRAIN_MSG_TEMPLATE_EN
            self.system_message = system_message_dict['en'][tuning_mode]
        else:
            self.template = DETECT_TRAIN_MSG_TEMPLATE_ZH
            self.system_message = system_message_dict['zh'][tuning_mode]
        self.raw_data = self.preprocess_data(raw_data, tuning_mode)
        self.language = language
        self.tuning_mode = tuning_mode

        self.cached_data_dict = {}
        rank0_print("============================================= DATA INFO =============================================")
        rank0_print("Data loaded len: {}".format(len(self.raw_data)))
        rank0_print("=====================================================================================================")

    def __len__(self):
        return len(self.raw_data)

    def __getitem__(self, i) -> Dict[str, torch.Tensor]:
        if i in self.cached_data_dict:
            return self.cached_data_dict[i]

        ret = preprocess([self.raw_data[i]["conversations"]], self.tokenizer, self.max_len, self.system_message)
        ret = dict(
            input_ids=ret["input_ids"][0],
            labels=ret["labels"][0],
            attention_mask=ret["attention_mask"][0],
        )
        self.cached_data_dict[i] = ret

        return ret

    def preprocess_data(self, raw_data, tuning_mode):
        data = []
        for item in raw_data:
            id = item['id']
            for i, conv in enumerate(item['conversation']):
                if tuning_mode == "leakage_only":
                    privacy_info = {"judgement": False if len(conv['privacy']) == 0 else True}
                else:
                    privacy_info = []
                    for p in conv['privacy']:
                        if tuning_mode == "phrase_only":
                            privacy_info.append(p['phrase'])
                        else:
                            privacy_info.append({
                                "privacy information": p['privacy information'],
                                "phrase": p['phrase']
                            })
                data.append({
                    "id": f"{id}_part{i}", 
                    "conversations": [
                        {"from": "user", "value": self.template.replace('<|QUERY|>', conv['user'])}, 
                        {"from": "assistant", "value": "```json\n{}\n```".format(json.dumps(privacy_info, ensure_ascii=False, indent=4))}
                ]})
        return data

def make_supervised_data_module(
    tokenizer: transformers.PreTrainedTokenizer, data_args, max_len,
) -> Dict:
    """Make dataset and collator for supervised fine-tuning."""
    dataset_cls = LazySupervisedDataset
    rank0_print("Loading data...")

    # load local data
    if os.path.exists(data_args.data_path):
         train_json = json.load(open(data_args.data_path, "r"))
    # load from hugging face
    else:
        import datasets 
        dataset = datasets.load_dataset(data_args.data_path, data_args.language)
        train_json = dataset['train']

    train_dataset = dataset_cls(train_json, tokenizer=tokenizer, max_len=max_len, language=data_args.language, tuning_mode=data_args.tuning_mode)

    if data_args.eval_data_path:
        # load local data
        if os.path.exists(data_args.eval_data_path):
            eval_json = json.load(open(data_args.eval_data_path, "r"))
        # load from hugging face
        else:
            import datasets 
            dataset = datasets.load_dataset(data_args.eval_data_path, data_args.language)
            eval_json = dataset['test']
        eval_dataset = dataset_cls(eval_json, tokenizer=tokenizer, max_len=max_len, language=data_args.language, tuning_mode=data_args.tuning_mode)
    else:
        eval_dataset = None

    return dict(train_dataset=train_dataset, eval_dataset=eval_dataset)


def train():
    global local_rank

    parser = transformers.HfArgumentParser(
        (ModelArguments, DataArguments, TrainingArguments, LoraArguments)
    )
    (
        model_args,
        data_args,
        training_args,
        lora_args,
    ) = parser.parse_args_into_dataclasses()

    # This serves for single-gpu qlora.
    if getattr(training_args, 'deepspeed', None) and int(os.environ.get("WORLD_SIZE", 1))==1:
        training_args.distributed_state.distributed_type = DistributedType.DEEPSPEED

    local_rank = training_args.local_rank

    device_map = None
    world_size = int(os.environ.get("WORLD_SIZE", 1))
    ddp = world_size != 1
    if lora_args.q_lora:
        device_map = {"": int(os.environ.get("LOCAL_RANK") or 0)} if ddp else "auto"
        if len(training_args.fsdp) > 0 or deepspeed.is_deepspeed_zero3_enabled():
            logging.warning(
                "FSDP or ZeRO3 are incompatible with QLoRA."
            )

    compute_dtype = (
        torch.float16
        if training_args.fp16
        else (torch.bfloat16 if training_args.bf16 else torch.float32)
    )

    # Set RoPE scaling factor
    config = transformers.AutoConfig.from_pretrained(
        model_args.model_name_or_path,
        cache_dir=training_args.cache_dir,
        trust_remote_code=True,
    )
    config.use_cache = False

    # Load model and tokenizer
    model = transformers.AutoModelForCausalLM.from_pretrained(
            model_args.model_name_or_path,
            config=config,
            torch_dtype=compute_dtype,
            cache_dir=training_args.cache_dir,
            device_map=device_map
        )
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        model_args.model_name_or_path,
        cache_dir=training_args.cache_dir,
        model_max_length=training_args.model_max_length,
        padding_side="right",
        use_fast=False,
        trust_remote_code=True,
    )
    tokenizer = add_pad_token(tokenizer)

    if training_args.use_lora:
        if lora_args.q_lora or 'chat' in model_args.model_name_or_path.lower() or 'instruct' in model_args.model_name_or_path.lower():
            modules_to_save = None
        else:
            modules_to_save = ["embed_tokens", "lm_head"]
        lora_config = LoraConfig(
            r=lora_args.lora_r,
            lora_alpha=lora_args.lora_alpha,
            target_modules=lora_args.lora_target_modules,
            lora_dropout=lora_args.lora_dropout,
            bias=lora_args.lora_bias,
            task_type="CAUSAL_LM",
            modules_to_save=modules_to_save  # This argument serves for adding new tokens.
        )
        if lora_args.q_lora:
            model = prepare_model_for_kbit_training(
                model, use_gradient_checkpointing=training_args.gradient_checkpointing
            )

        model = get_peft_model(model, lora_config)

        # Print peft trainable params
        model.print_trainable_parameters()

        if training_args.gradient_checkpointing:
            model.enable_input_require_grads()
    
    # Load data
    data_module = make_supervised_data_module(
        tokenizer=tokenizer, data_args=data_args, max_len=training_args.model_max_length
    )

    # Start trainner
    trainer = Trainer(
        model=model, tokenizer=tokenizer, args=training_args, **data_module
    )

    trainer.train()
    trainer.save_state()

    safe_save_model_for_hf_trainer(trainer=trainer, output_dir=training_args.output_dir, bias=lora_args.lora_bias)


if __name__ == "__main__":
    train()