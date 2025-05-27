import json 
import os 
from tqdm import tqdm

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
    file_path="raw_data/shareGPT/common_en_70k.jsonl"
    file_path_output = "preprocess_data/shareGPT/common_en_70k.json"
    preprocess_shareGPT()