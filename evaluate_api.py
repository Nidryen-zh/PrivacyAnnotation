import json
import os 
import argparse
from generation_api import *
import copy
from tqdm import tqdm
import re
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from template import *
import concurrent.futures
import random

MAX_WORKERS = 8

def load_data(file_path, start_idx=0, end_idx=None):
    '''
    {
        "id": "ShareGPT_qQq2J4G",
        "conversation": [
            {
                "user": "YES, I WAS THINKING WE COULD INCREASE THE PERCENTAGE OF IMAGE RECOGNITION BY ADDING CERTAIN PARTICLES/VARIABLES THAT CAN BE LATER INTERPRETED BY OBJSERVER USING A TAG/ NOTE",
                "assistant": "That's an interesting idea! Can you elaborate on what you mean by \"particles/variables\" and how they would be used to increase image recognition?"
            }
        ]
    }
    '''
    with open(file_path) as f:
        data = json.load(f)
    return data[start_idx:end_idx]

def query_rewriting_prompt(query, few_shot=False, training_mode='all', language='en'):
    shot = "zero-shot" if not few_shot else "few-shot"
    msg_dict_en = {
        "zero-shot": {
            "all": DETECT_MSG_TEMPLATE_EN,
            "phrase_only": DETECT_MSG_PHRASE_ONLY_TEMPLATE_EN,
            "leakage_only": DETECT_MSG_LEAKAGE_ONLY_TEMPLATE_EN
        },
        "few-shot": {
            "all": DETECT_FEW_SHOT_MSG_TEMPLATE_EN,
            "phrase_only": DETECT_FEW_SHOT_MSG_PHRASE_ONLY_TEMPLATE_EN,
            "leakage_only": DETECT_FEW_SHOT_MSG_LEAKAGE_ONLY_TEMPLATE_EN
        }
    }
    msg_dict_zh = {
        "zero-shot": {
            "all": DETECT_MSG_TEMPLATE_ZH,
            "phrase_only": DETECT_MSG_PHRASE_ONLY_TEMPLATE_ZH,
            "leakage_only": DETECT_MSG_LEAKAGE_ONLY_TEMPLATE_ZH
        },
        "few-shot": {
            "all": DETECT_FEW_SHOT_MSG_TEMPLATE_ZH,
            "phrase_only": DETECT_FEW_SHOT_MSG_PHRASE_ONLY_TEMPLATE_ZH,
            "leakage_only": DETECT_FEW_SHOT_MSG_LEAKAGE_ONLY_TEMPLATE_ZH
        }
    }

    if language == "en":
        template = msg_dict_en[shot][training_mode]
    else:
        template = msg_dict_zh[shot][training_mode]
    message = template.replace("<|QUERY|>", query)
    return message

class TextDataset(Dataset):
    def __init__(self, raw_data, raw_data_train, few_shot=False, language='en', phrase_only=False, leakage_only=False):
        training_mode = "all"
        if phrase_only:
            training_mode = "phrase_only"
        if leakage_only:
            training_mode = "leakage_only"
        self.training_mode = training_mode
        shot = "zero-shot" if not few_shot else "few-shot"
        sys_dict_en = {
            "zero-shot": {
                "all": DETECT_SYS_TEMPLATE_EN,
                "phrase_only": DETECT_SYS_PHRASE_ONLY_TEMPLATE_EN,
                "leakage_only": DETECT_SYS_LEAKAGE_ONLY_TEMPLATE_EN
            },
            "few-shot": {
                "all": DETECT_FEW_SHOT_SYS_TEMPLATE_EN,
                "phrase_only": DETECT_FEW_SHOT_SYS_PHRASE_ONLY_TEMPLATE_EN,
                "leakage_only": DETECT_FEW_SHOT_SYS_LEAKAGE_ONLY_TEMPLATE_EN
            }
        }
        sys_dict_zh = {
            "zero-shot": {
                "all": DETECT_SYS_TEMPLATE_ZH,
                "phrase_only": DETECT_SYS_PHRASE_ONLY_TEMPLATE_ZH,
                "leakage_only": DETECT_SYS_LEAKAGE_ONLY_TEMPLATE_ZH
            },
            "few-shot": {
                "all": DETECT_FEW_SHOT_SYS_TEMPLATE_ZH,
                "phrase_only": DETECT_FEW_SHOT_SYS_PHRASE_ONLY_TEMPLATE_ZH,
                "leakage_only": DETECT_FEW_SHOT_SYS_LEAKAGE_ONLY_TEMPLATE_ZH
            }
        }

        if language == 'en':
            self.system = sys_dict_en[shot][training_mode]
        else:
            self.system = sys_dict_zh[shot][training_mode]
        self.few_shot = few_shot
        self.language = language
        self.data = self.preprocess(raw_data, raw_data_train, self.few_shot, self.training_mode, self.language)

    def get_few_shot_cases(self, all_pos_conversations, all_neg_conversations, training_mode, language):
        '''
        Few shot case:

        user's Query: "I am board. Tell me a joke."
        JSON Output:
        ```json
        [
            {
                "phrase": "board",
                "privacy information": "The user is board."
            }
        ]
        ```
        '''
        conversations = copy.deepcopy(random.sample(all_pos_conversations, 2)) + copy.deepcopy(random.sample(all_neg_conversations, 3))
        cases = ""
        for conv in conversations:
            if training_mode == "leakage_only":
                privacy = {"judgment": True if len(conv['privacy']) > 0 else False}
            else:
                privacy = []
                for p in conv['privacy']:
                    if "privacy leakage score" not in p:
                        print(conversations)
                    p.pop("privacy leakage score")
                    if training_mode == "all":
                        privacy.append(p)
                    elif training_mode == "phrase_only":
                        privacy.append(p['phrase'])
                    else:
                        assert training_mode in ['all', 'phrase_only']
            if language == "en":
                case_one = "user's Query: \"{}\"\nJSON Output:\n```json\n{}\n```".format(conv['user'], json.dumps(privacy, ensure_ascii=False, indent=4))
            else:
                case_one = "用户的请求: \"{}\"\nJSON输出:\n```json\n{}\n```".format(conv['user'], json.dumps(privacy, ensure_ascii=False, indent=4))
            cases += case_one + "\n\n"
        return cases
        
    def preprocess(self, raw_data, raw_data_train, few_shot=False, training_mode="all", language="en"):
        print(training_mode)
        data = []
        ## only for few-shot
        all_conversations = []
        for item in raw_data_train:
            all_conversations += copy.deepcopy(item['conversation'])
        all_pos_conversations = []
        all_neg_conversations = []
        for conv in all_conversations:
            if len(conv['privacy']) > 0:
                all_pos_conversations.append(conv)
            else:
                all_neg_conversations.append(conv)
        
        for item in raw_data:
            id = item['id']
            for i, conv in enumerate(item['conversation']):
                msg = query_rewriting_prompt(conv['user'], few_shot, training_mode, language)
                if few_shot:
                    cases = self.get_few_shot_cases(all_pos_conversations, all_neg_conversations, training_mode, language)
                    msg = msg.replace("<|CASE|>", cases)
                data.append({"id": "{}_part{}".format(id, i), "msg": msg, "sys": self.system})

        ## DEBUG
        # data = [{"id": "id"+str(i+1), "msg": str(i+1), "sys": self.system} for i in range(100)]
        return data

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)

def generate_for_one(msg, sys, ids, model_name):
    response, details = safe_chatgpt_for_json(msg, sys, model_name, debug=True)
    return {"id": ids, "system": sys, "message": msg, "response": details, "response_json": response}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='argparse')
    parser.add_argument('--model_name', '-m', type=str, default="qwen2.5-7b-instruct", help="a model's name")
    parser.add_argument('--data_path', '-d', type=str, default="Nidhogg-zh/Interaction_Dialogue_with_Privacy", help="data path")
    parser.add_argument('--output_path', '-o', type=str, default="output/shareGPT/Qwen_few-shot/Qwen2.5-7B-Instruct/privacy_information_dev.json", help="output path")
    parser.add_argument('--few-shot', '-f', action='store_true', help="whether use few shot")
    parser.add_argument('--phrase_only', type=bool, default=False, help="whether the model is tuned to predict only phrase")
    parser.add_argument('--leakage_only', type=bool, default=False, help="whether the model is tuned to predict only leakage")
    parser.add_argument('--start_idx', '-s', type=int, default=0)
    parser.add_argument('--end_idx', '-e', type=int, default=None)
    parser.add_argument('--language', '-l', type=str, default="en")
    args = parser.parse_args()
    args.output_path = args.output_path.replace(".json", f"_rank_{args.start_idx}_{args.end_idx}.json")

    data_path = args.data_path
    output_path = args.output_path
    
    # load local data
    if os.path.exists(data_path):
        data = load_data(data_path, args.start_idx, args.end_idx)
        data_path_train = os.path.join(os.path.split(data_path)[0], "privacy_information_train.json")
        data_train = load_data(data_path_train)
    # load from hugging face
    else:
        import datasets 
        dataset = datasets.load_dataset(data_path, args.language)
        data = dataset['test']
        data_train = dataset['train']

    text_dataset = TextDataset(data, data_train, few_shot=args.few_shot, language=args.language, phrase_only=args.phrase_only, leakage_only=args.leakage_only)
    print("========================= DATA INFO ==========================")
    print("DATA PATH: {}".format(data_path))
    print("OUTPUT PATH: {}".format(output_path))
    print("DATASET LEN:", len(text_dataset))
    print("LANGUAGE:", args.language)
    print("FEW SHOT:", args.few_shot)
    print("==============================================================")
    
    results = []
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            all_tasks = []
            process_bar = tqdm(total=len(text_dataset))

            for inputs in text_dataset:
                msg = inputs['msg']
                sys = inputs['sys']
                ids = inputs['id']
                future = executor.submit(generate_for_one, msg, sys, ids, args.model_name)
                future.add_done_callback(lambda p: process_bar.update(1))
                all_tasks.append(future)
               
            output = [t.result() for t in all_tasks]
            process_bar.close()
            os.makedirs(os.path.split(args.output_path)[0], exist_ok=True)
            json.dump(output, open(args.output_path, 'w'), ensure_ascii=False, indent=4)
    except:
        pass    

    ## merge result
    # os.makedirs(os.path.split(output_path)[0], exist_ok=True)
    # json.dump(results, open(output_path, 'w'), ensure_ascii=False, indent=4)
    