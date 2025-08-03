
import transformers
from typing import Dict, Optional, List
import json
import torch
from transformers.trainer_pt_utils import LabelSmoother

IGNORE_TOKEN_ID = LabelSmoother.ignore_index

def add_pad_token(tokenizer):
    model_name_or_path = tokenizer.name_or_path.lower()
    if "qwen" in model_name_or_path:
        assert tokenizer.pad_token is not None, "Something wrong and tokenizer of Qwen's pad token is None"
    if "llama" in model_name_or_path:
        tokenizer.pad_token = "<|end_of_text|>"
        tokenizer.pad_token_id = tokenizer("<|end_of_text|>").input_ids[1:][0]
    return tokenizer

def preprocess_qwen(
    sources,
    tokenizer: transformers.PreTrainedTokenizer,
    max_len: int,
    system_message: str = "You are a helpful assistant."
) -> Dict:
    roles = {"user": f"<|im_start|>user", "assistant": f"<|im_start|>assistant"}

    im_start = tokenizer("<|im_start|>").input_ids
    im_end = tokenizer("<|im_end|>").input_ids
    nl_tokens = tokenizer('\n').input_ids
    pad_token_id = tokenizer("<|endoftext|>").input_ids[0]
    _system = tokenizer('system').input_ids + nl_tokens

    # Apply prompt templates
    input_ids, targets = [], []
    for i, source in enumerate(sources):
        if roles[source[0]["from"]] != roles["user"]:
            source = source[1:]

        input_id, target = [], []
        system = im_start + _system + tokenizer(system_message).input_ids + im_end + nl_tokens
        input_id += system
        target += im_start + [IGNORE_TOKEN_ID] * (len(system)-3) + im_end + nl_tokens
        assert len(input_id) == len(target)
        for j, sentence in enumerate(source):
            role = roles[sentence["from"]]
            _input_id = tokenizer(role).input_ids + nl_tokens + tokenizer(sentence["value"]).input_ids + im_end + nl_tokens
            input_id += _input_id
            if role == f"<|im_start|>user":
                _target = im_start + [IGNORE_TOKEN_ID] * (len(_input_id)-3) + im_end + nl_tokens
            elif role == f"<|im_start|>assistant":
                _target = im_start + [IGNORE_TOKEN_ID] * (len(tokenizer(role).input_ids) - 1) + _input_id[len(tokenizer(role).input_ids):-2] + im_end + nl_tokens
            else:
                raise NotImplementedError
            target += _target
        assert len(input_id) == len(target)
        input_id += [pad_token_id] * (max_len - len(input_id))
        target += [IGNORE_TOKEN_ID] * (max_len - len(target))
        input_ids.append(input_id[:max_len])
        targets.append(target[:max_len])
    input_ids = torch.tensor(input_ids, dtype=torch.int)
    targets = torch.tensor(targets, dtype=torch.int)

    # print(tokenizer.batch_decode(input_ids, skip_special_tokens=False)[0])

    return dict(
        input_ids=input_ids,
        labels=targets,
        attention_mask=input_ids.ne(pad_token_id),
    )

def preprocess_llama(
    sources,
    tokenizer: transformers.PreTrainedTokenizer,
    max_len: int,
    system_message: str = "You are a helpful assistant."
) -> Dict:
    roles = {"user": f"<|start_header_id|>user<|end_header_id|>\n", "assistant": f"<|start_header_id|>assistant<|end_header_id|>\n"}

    im_start = tokenizer("<|begin_of_text|>").input_ids[1:]
    im_end = tokenizer("<|eot_id|>").input_ids[1:]
    nl_tokens = tokenizer('\n').input_ids[1:]
    pad_token_id = tokenizer("<|end_of_text|>").input_ids[1:][0]
    _system = tokenizer('<|start_header_id|>system<|end_header_id|>\n').input_ids[1:]

    # Apply prompt templates
    input_ids, targets = [], []
    for i, source in enumerate(sources):
        if roles[source[0]["from"]] != roles["user"]:
            source = source[1:]

        input_id, target = [], []
        system = im_start + _system + nl_tokens + tokenizer(system_message).input_ids[1:] + im_end
        input_id += system
        target += im_start + [IGNORE_TOKEN_ID] * (len(system)-2) + im_end
        assert len(input_id) == len(target)
        for j, sentence in enumerate(source):
            role = roles[sentence["from"]]
            _input_id = tokenizer(role).input_ids[1:] + nl_tokens + tokenizer(sentence["value"]).input_ids[1:] + im_end
            input_id += _input_id
            if role == f"<|start_header_id|>user<|end_header_id|>\n":
                _target = [IGNORE_TOKEN_ID] * (len(_input_id)-1) + im_end
            elif role == f"<|start_header_id|>assistant<|end_header_id|>\n":
                _target = [IGNORE_TOKEN_ID] * len(tokenizer(role).input_ids[1:]) + _input_id[len(tokenizer(role).input_ids[1:]):-1] + im_end
            else:
                raise NotImplementedError
            target += _target
        assert len(input_id) == len(target)
        input_id += [pad_token_id] * (max_len - len(input_id))
        target += [IGNORE_TOKEN_ID] * (max_len - len(target))
        input_ids.append(input_id[:max_len])
        targets.append(target[:max_len])
    input_ids = torch.tensor(input_ids, dtype=torch.int)
    targets = torch.tensor(targets, dtype=torch.int)

    # print(tokenizer.batch_decode(input_ids, skip_special_tokens=False)[0])

    return dict(
        input_ids=input_ids,
        labels=targets,
        attention_mask=input_ids.ne(pad_token_id),
    )
