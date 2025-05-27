from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
import torch

hf_token = "<YOUR_TOKEN>"

sampling_params = SamplingParams(temperature=0, top_p=0.95, max_tokens=512)

def rank0_print(*arg):
    if not torch.distributed.is_initialized() or torch.distributed.get_rank() == 0:
        print(*arg)

def generate_batch(model, tokenizer, message, system, ids):
    if type(message) == str:
        message = [message]
    if type(system) == str:
        system = [system]
    assert len(message) == len(system), "Number of messages and systems are not equal."

    texts = []
    for i, (msg, sys) in enumerate(zip(message, system)):   
        msg_form = []
        msg_form.append({"role": "system", "content": sys})
        msg_form.append({"role": "user", "content": msg})
        text = tokenizer.apply_chat_template(
            msg_form,
            tokenize=False,
            add_generation_prompt=True
        )
        text = text.replace("Cutting Knowledge Date: December 2023\nToday Date: 06 Feb 2025\n\n", "")
        # print(text)
        texts.append(text)

    outputs = model.generate(texts, sampling_params)
    responses = []
    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        responses.append(generated_text)

    results = [{"id": id, "system": sys, "message": msg, "response": res} for id, sys, msg, res in zip(ids, system, message, responses)]
    return results
    

def load_model_and_tokenizer(model_name, torch_dtype=torch.float32):
    model = LLM(model=model_name, dtype=torch_dtype, tensor_parallel_size=2, pipeline_parallel_size=1, max_model_len=8192)
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side='left', truncation_side='left', max_legth=8192, token=hf_token)
    return model, tokenizer


if __name__ == "__main__":
    prompts = [
        "Hello, my name is",
        "The president of the United States is",
        "The capital of France is",
        "The future of AI is",
    ] * 400000
    sampling_params = SamplingParams(temperature=0, top_p=0.95, max_tokens=512)

    model, tokenizer = load_model_and_tokenizer("Qwen/Qwen2.5-7B-Instruct")

    outputs = model.generate(prompts, sampling_params)
    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        # print(f"Prompt: {prompt}, Generated text: {generated_text}")
