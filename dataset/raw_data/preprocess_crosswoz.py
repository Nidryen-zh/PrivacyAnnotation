import json 
import os 
from tqdm import tqdm
import argparse

'''
Covert All the data into the format as below:
{
    "id": "CrossWOZ_76551",
    "conversation": [
        {
            "user": "你好，麻烦帮我推荐一个门票免费的景点。",
            "assistant": "你好，您可以选择故宫，八达岭长城，颐和园或者红砖美术馆。"
        }
    ]
}
'''
def preprocess_crosswoz(file_path="crosswoz/train.json", file_path_output = "../preprocess_data/CrossWOZ/train.json"):
    preprocessed_data = []
    with open(file_path, encoding='utf-8') as f:
        data_raw = json.load(f)
    
    for i, id in enumerate(tqdm(data_raw)):
        item = data_raw[id]
        data = {"id": "CrossWOZ_{}{}".format(id, i), "conversation": []}
        conv_one = {}
        for j, conv in enumerate(item["messages"]):
            if conv['role'] == 'usr':
                role = "user" 
            elif conv['role'] == 'sys':
                role = "assistant"
            else:
                print("ERROR")
            assert role not in conv_one, conv_one
            conv_one[role] = conv['content']
            if role == "assistant":
                assert len(conv_one) == 2
                data['conversation'].append(conv_one)
                conv_one = {}
        preprocessed_data.append(data)
        
    os.makedirs(os.path.split(file_path_output)[0], exist_ok=True)
    json.dump(preprocessed_data, open(file_path_output, "w", encoding='utf-8'), ensure_ascii=False, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='private filter')
    parser.add_argument('--file_path', '-f', type=str,  default="CrossWOZ/train_example.json")
    parser.add_argument('--file_path_output', '-o', type=str, default="../preprocess_data/CrossWOZ/train_example.json")
    args = parser.parse_args()

    file_path = args.file_path
    file_path_output = args.file_path_output
    file_path_output_dir = os.path.split(file_path_output)[0]
    os.makedirs(file_path_output_dir, exist_ok=True)
    preprocess_crosswoz(file_path, file_path_output)