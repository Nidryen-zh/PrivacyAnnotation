from GPTAPI import safe_chatgpt, safe_chatgpt_for_json
from detect_private_category_GPT_TEMPLATE import *

import json 
import os
from tqdm import tqdm
import concurrent.futures
import logging
from random import shuffle
import math
import copy
import openai
import argparse

os.makedirs("logs", exist_ok=True)
logging.basicConfig(level=logging.DEBUG, 
                    # filename='logs/detect_GPT.log',
                    # filemode='a',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - [%(levelname)s]: %(message)s' 
                    )
# Disable openai logger
logging.getLogger("requsets").setLevel(logging.ERROR)
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

MAX_WORKERS = 10
DEBUG = True

class PrivateDetector:
    def __init__(self, file_path, file_path_output, shot=None, language="en", debug=False):
        '''
        Detect private category or phrase from the preprocessed data
        '''
        self.file_path = file_path
        self.file_path_output = file_path_output
        with open(file_path, encoding='utf-8') as f:
            self.data = json.load(f)[:shot]
        self.debug = debug
        self.language = language
        self.gpt_error_count = 0

    def _detect_for_ont_text(self, input_text):
        pass 

    def detect(self):
        pass 

    def postpreprocess_output(self, output):
        pass

    def save(self):
        os.makedirs(os.path.split(self.file_path_output)[0], exist_ok=True)
        json.dump(self.data_output, open(self.file_path_output, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

    def save_detailed_information(self):
        output_path = self.file_path_output.replace(".json", "_detailed_info.json")
        os.makedirs(os.path.split(output_path)[0], exist_ok=True)
        json.dump(self.deltail_informations, open(output_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)


class PrivateCategoryDetector(PrivateDetector):
    def __init__(self, file_path, file_path_output, shot=None, language="en", debug=False):
        super().__init__(file_path, file_path_output, shot, language, debug)

    def _detect_for_one_text(self, input_text, privacy_leak):
        '''
        input_text: "I'm a teacher at China, majoring in computer science. I will go back home to London."
        
        Output:
        {
            "Job": ["teacher"],
            "Subject": ["computer science"],
            "Location": ["China", "London"]
        }
        '''
        # system = "You are an expert in privacy detection."
        system = ""
        if self.language == 'en':
            ## normal
            template = DETECT_PRIVATE_CATEGORY_TEMPLATE_EN
            ## baseline eval
            # template = DETECT_PRIVATE_CATEGORY_TEMPLATE_EN_BASELINE
        else:
            template = DETECT_PRIVATE_CATEGORY_TEMPLATE_ZH
        message = template.replace("<|QUERY|>", input_text)

        detailed_informations = []
        result = {}
        if privacy_leak:
            if self.debug:
                result, raw_result = safe_chatgpt_for_json(message=message, system=system, debug=True)
                detailed_information = {"system": system, "message": message, "GPT_output": raw_result}
                detailed_informations.append(detailed_information)
            else:
                result = safe_chatgpt_for_json(message=message, system=system, debug=False)

            if result == "<|GPT_ERROR|>":
                self.gpt_error_count += 1
                result = {}
        
        if self.debug:
            return input_text, result, detailed_informations
        else:
            return input_text, result
    
    def detect(self):
        '''
        output form:
        {
            "user": xxx
            "assistant": xxx
            "private_category": {
                category1: [phrase1, phrase2],
                category2: [phrase3]
            }
        }
        '''
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            all_tasks = []
            count = 0
            for item in self.data:
                count += len(item["conversation"])
            process_bar = tqdm(total=count)
            
            for item in self.data:
                for conv in item["conversation"]:
                    input_text = conv["user"]
                    ## normal
                    privacy_leak = conv["privacy"]['judgment']
                    ## baseline eval
                    # privacy_leak = True
                    future = executor.submit(self._detect_for_one_text, input_text, privacy_leak)
                    future.add_done_callback(lambda p: process_bar.update(1))
                    all_tasks.append(future)
 
            output = [t.result() for t in all_tasks]
            process_bar.close()

        self.postpreprocess_output(output)
        logging.info("End Dectection with GPT ERROT: {}".format(self.gpt_error_count))

    def postpreprocess_output(self, output):
        self.data_output = self.data
        self.deltail_informations = []
        index = 0
        for item in self.data_output:
            for conv in item["conversation"]:
                assert conv["user"] == output[index][0], "Something wrong with the multithread, the data order is changed"
                ## normal
                conv["private_category"] = output[index][1]
                ## baseline eval
                # conv['privacy'] = output[index][1]
                if self.debug:
                    self.deltail_informations += output[index][2]
                index += 1

class PrivateCategoryAnalyzer:
    def __init__(self, file_path, file_path_output_dir, category_path=None, language="en"):
        self.file_path = file_path
        self.file_path_output_dir = file_path_output_dir
        with open(file_path, encoding='utf-8') as f:
            self.data = json.load(f)
        # get all private categories
        '''
        output
        {
            CATEGORY: {
                "phrase": ["PHRASE1"]
                "id": xx 
            }
        }
        '''
        self.private_categories = {}
        category_count = 0
        for item in tqdm(self.data):
            for conv in item['conversation']: 
                for category in conv['private_category']:
                    entities = conv['private_category'][category]
                    if category not in self.private_categories:
                        self.private_categories[category] = {"phrase": [], "id": category_count}
                        category_count += 1
                    for phrase in entities:
                        if phrase not in self.private_categories[category]['phrase']:
                            self.private_categories[category]['phrase'].append(phrase)

        if category_path is not None:
            self.private_categories = json.load(open(category_path, encoding='utf-8'))

        logging.info("Detect {} categories Before Merge with Rule.".format(len(self.private_categories)))
        self.merge_synonyms_with_rule() 
        self.language = language
        self.category_num = len(self.private_categories)
        self.gpt_error_count = 0
        logging.info("Detect {} categories.".format(self.category_num))

    def merge_synonyms_with_rule(self):
        '''
        mrege same or similar categories with rules
        '''
        def _two_category_match(category1, category2):
            flag = False 
            category1 = category1.lower().replace(" ", "").replace("/", "").replace(",", "").replace("_", "").replace("-", "")
            category2 = category2.lower().replace(" ", "").replace("/", "").replace(",", "").replace("_", "").replace("-", "")
            if category1 == category2:
                flag = True 
            return flag
        
        private_categories_new = {}
        categories = list(self.private_categories.keys())
        merged_categories = []
        for i in range(len(categories)):
            category1 = categories[i]
            if category1 in merged_categories:
                continue 
            private_categories_new[category1] = self.private_categories[category1]
            for j in range(i+1, len(categories)):
                category2 = categories[j]
                flag = _two_category_match(category1, category2)
                if flag:
                    private_categories_new[category1]['phrase'] += self.private_categories[category2]['phrase']
                    merged_categories.append(category2)
        self.private_categories = private_categories_new

    def save_private_categories(self):
        os.makedirs(self.file_path_output_dir, exist_ok=True)
        json.dump(self.private_categories, open(os.path.join(self.file_path_output_dir, "private_categories.json"), 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

class PrivateCategoryMerger_ByBlock(PrivateCategoryAnalyzer):
    def __init__(self, file_path, file_path_output_dir, category_path=None, language="en"):
        super().__init__(file_path, file_path_output_dir, category_path, language)

    def _merge_synonyms_for_one_block(self, private_categories_block):
        '''
        input: 
        {
            category 1: {"phrase": [], "id": xxx}
        }
        '''
        if self.language == "en":
            category_input = ['{' + '"private category {idx}": "{category}", "phrases": {entities}'.format(idx=(i+1), category=key, entities=list(private_categories_block[key]['phrase'])) + '}' for i, key in enumerate(private_categories_block)]
            category_input = "\n".join(category_input)
            # print(category_input)

            system = "You're a privacy classification expert."
            template = MERGE_PRIVATE_CATEGORY_BYBLOCK_TEMPLATE_EN
            message = template.replace('<|CATEGORY_INPUT|>', category_input).replace('<|BLOCK_SIZE|>', str(len(private_categories_block)))
        else:
            category_input = ['{' + '"隐私类别 {idx}": "{category}", "短语": {entities}'.format(idx=(i+1), category=key, entities=list(private_categories_block[key]['phrase'])) + '}' for i, key in enumerate(private_categories_block)]
            category_input = "\n".join(category_input)
            # print(category_input)

            system = "你是一位隐私分类专家。"
            template = MERGE_PRIVATE_CATEGORY_BYBLOCK_TEMPLATE_ZH
            message = template.replace('<|CATEGORY_INPUT|>', category_input).replace('<|BLOCK_SIZE|>', str(len(private_categories_block)))

        merge_result = safe_chatgpt_for_json(message=message, system=system)

        check_flag = True 
        if type(merge_result) != list:
            check_flag = False
        else:
            for key in merge_result:
                if type(key) != str or key not in private_categories_block:
                    check_flag = False 
                    break 
        if merge_result == "<|GPT_ERROR|>" or not check_flag:
            self.gpt_error_count += 1
            merge_result = list(private_categories_block.keys())

        return merge_result

    def _shuffle_dic(self, dic):
        dic_key = list(dic.keys())
        shuffle(dic_key)
        new_dic = {}
        for key in dic_key:
            new_dic[key] = dic.get(key)
        return new_dic

    def _merge_synonyms(self, private_categories, block_size=10):
        private_categories_shuffled_keys = list(private_categories.keys())
        shuffle(private_categories_shuffled_keys)
        private_categories_num = len(private_categories_shuffled_keys)

        private_categories_merged = {}
        block_num = math.ceil(private_categories_num / block_size)
        private_categories_blocks = []
        for i in range(block_num):
            start_index = i * block_size
            end_index = (i + 1) * block_size
            keys = private_categories_shuffled_keys[start_index:end_index]
            private_categories_block = {key: private_categories[key] for key in keys}
            private_categories_blocks.append(private_categories_block)

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            all_tasks = []
            block_num = math.ceil(private_categories_num / block_size)
            process_bar = tqdm(total=len(private_categories_blocks))

            for private_categories_block in private_categories_blocks:
                future = executor.submit(self._merge_synonyms_for_one_block, private_categories_block)
                future.add_done_callback(lambda p: process_bar.update(1))
                all_tasks.append(future)

            output = [t.result() for t in all_tasks]
            process_bar.close()

            # postpreprocess output
            for block, out in zip(private_categories_blocks, output):
                merged_private_categories = out ### a list
                for key in merged_private_categories:
                    private_categories_merged[key] = block[key]

        return private_categories_merged
    
    def _merge_synonyms_with_all_categories(self, private_categories):
        private_categories_shuffled_keys = list(private_categories.keys())
        shuffle(private_categories_shuffled_keys)

        category_input = str(private_categories_shuffled_keys)

        if self.language == "en":
            system = "You're a privacy classification expert."
            template = MERGE_PRIVATE_CATEGORY_BYBLOCK_TOTAL_TEMPLATE_EN
        else:
            system = "你是一位隐私分类专家。"
            template = MERGE_PRIVATE_CATEGORY_BYBLOCK_TOTAL_TEMPLATE_ZH
        message = template.replace('<|ALL_CATEGORY|>', category_input)

        merge_result = safe_chatgpt_for_json(message=message, system=system)

        check_flag = True 
        for key in merge_result:
            if key not in private_categories:
                check_flag = False 
                break
        if merge_result == "<|GPT_ERROR|>" or not check_flag:
            self.gpt_error_count += 0
            merge_result = list(private_categories.keys())

        private_categories_merged = {}
        for key in merge_result:
            private_categories_merged[key] = private_categories[key]

        return private_categories_merged

    def merge_synonyms(self):
        logging.info("Start merging...")
        private_categories = self.private_categories
        threshold = 0
        block_size = 50

        test_time = 0
        max_test_time = 2 # 5
        while test_time < max_test_time:
            private_categories_merged = self._merge_synonyms(private_categories, block_size)
            logging.info("Merged: Before {} -> After {}".format(len(private_categories), len(private_categories_merged)))
            if len(private_categories) - len(private_categories_merged) <= threshold:
                test_time += 1
            private_categories = private_categories_merged
        self.private_categories_merged = private_categories

        logging.info("Merging with all categories.")
        private_categories_merged = self._merge_synonyms_with_all_categories(private_categories)
        logging.info("Merged: Before {} -> After {}".format(len(private_categories), len(private_categories_merged)))

    def save_private_categories_merged(self):
        os.makedirs(self.file_path_output_dir, exist_ok=True)
        json.dump(self.private_categories_merged, open(os.path.join(self.file_path_output_dir, "private_categories_merged.json"), 'w', encoding='utf-8'), ensure_ascii=False, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='private filter')
    parser.add_argument('--file_path', '-f', type=str, default="privacy_data/shareGPT/privacy_leaked/common_en_70k_example.json")
    parser.add_argument('--file_output_dir', '-o', type=str, default="privacy_data/shareGPT/privacy_category")
    parser.add_argument('--language', '-l', type=str, default="en", choices=['en', 'zh']) # en: English & zh: Chinese\]
    args = parser.parse_args()

    ## [STEP 2-1] detect private categories for each text
    file_path = args.file_path
    file_path_output = os.path.join(args.file_output_dir, "private_categories.json")
    private_category_detector = PrivateCategoryDetector(file_path, file_path_output, shot=None, language=args.language)
    private_category_detector.detect()
    private_category_detector.save()

    ## [STEP 2-2] analysis private categories for whole corpus
    file_path = os.path.join(args.file_output_dir, "private_categories.json")
    file_output_dir = args.file_output_dir
    category_path = None
    private_category_analyzer = PrivateCategoryMerger_ByBlock(file_path, file_output_dir, category_path, args.language)
    private_category_analyzer.save_private_categories()
    private_category_analyzer.merge_synonyms()
    private_category_analyzer.save_private_categories_merged()