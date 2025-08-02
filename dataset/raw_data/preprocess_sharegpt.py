import json 
import os 
from tqdm import tqdm
import argparse

'''
Covert All the data into the format as below:
{
    "id": "ShareGPT_AzsVtVQ",
    "conversation": [
        {
            "user": "Are you busy?",
            "assistant": "I am a computer program and do not have the ability to be busy. I am always ready to assist you with any questions or information you may need. How can I help you today?"
        },
    ]
}
'''
'''
Here is an example to preprocess shareGPT corpus
'''
def preprocess_shareGPT(file_path="raw_data/shareGPT/common_en_70k.jsonl", file_path_output = "preprocess_data/shareGPT/common_en_70k.json"):
    with open(file_path, encoding='utf-8') as f:
        lines = f.readlines()

    preprocessed_data = []
    for line in tqdm(lines):
        raw_data = json.loads(line)
        data = {"id": "ShareGPT_{}".format(raw_data['conversation_id']), "conversation": []}
        for conv in raw_data["conversation"]:
            text = conv['human']
            data['conversation'].append({"user": text, "assistant": conv['assistant']})
        preprocessed_data.append(data)
    
    os.makedirs(os.path.split(file_path_output)[0], exist_ok=True)
    json.dump(preprocessed_data, open(file_path_output, "w", encoding='utf-8'), ensure_ascii=False, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='private filter')
    parser.add_argument('--file_path', '-f', type=str,  default="shareGPT/common_en_70k_example.jsonl")
    parser.add_argument('--file_path_output', '-o', type=str, default="../preprocess_data/shareGPT/common_en_70k_example.json")
    args = parser.parse_args()

    file_path = args.file_path
    file_path_output = args.file_path_output
    file_path_output_dir = os.path.split(file_path_output)[0]
    os.makedirs(file_path_output_dir, exist_ok=True)
    preprocess_shareGPT(file_path=file_path, file_path_output=file_path_output)