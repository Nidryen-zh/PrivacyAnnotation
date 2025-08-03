from GPTAPI import safe_chatgpt, safe_chatgpt_for_json
from detect_private_phrase_GPT_TEMPLATE import *

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

class PrivatePhraseDetector_WithCategory(PrivateDetector):
    def __init__(self, file_path, file_path_output, private_categories_file_path, shot=None, language="en", debug=False):
        super().__init__(file_path, file_path_output, shot, language, debug)
        logging.info("The input file is {}".format(file_path))
        logging.info("The output file is {}".format(file_path_output))
        self.private_categories_file_path = private_categories_file_path
        with open(private_categories_file_path, 'r', encoding='utf-8') as f:
            self.private_categories = json.load(f)
        logging.info("Total num of private categories: {}".format(len(self.private_categories)))

    def _detect_for_one_text(self, input_text, privacy_leak):
        private_categories_list = list(self.private_categories.keys())
        block_size = 50

        detailed_informations = []
        output = {}
        if privacy_leak:
            for i in range(math.ceil(len(private_categories_list) / block_size)):
                start_index = i * block_size
                end_index = (i+1) * block_size
                private_categories_block = private_categories_list[start_index:end_index]
                categories = str(private_categories_block)

                # system = "You are an expert in privacy detection."
                # system = "You are a helpful assistant."
                system = ""
                if self.language == "en":
                    template = DETECT_PRIVATE_PHRASE_WITH_CATEGORY_TEMPLATE_EN
                else:
                    template = DETECT_PRIVATE_PHRASE_WITH_CATEGORY_TEMPLATE_ZH
                message = template.replace("<|QUERY|>", input_text).replace("<|CATEGORIES|>", categories)
            
                if self.debug:
                    result, raw_result = safe_chatgpt_for_json(message=message, system=system, debug=True)
                    detailed_information = {"system": system, "message": message, "GPT_output": raw_result}
                    detailed_informations.append(detailed_information)
                else:
                    result = safe_chatgpt_for_json(message=message, system=system, debug=False)

                if result == "<|GPT_ERROR|>" or type(result) != dict:
                    self.gpt_error_count += 1
                    result = {}
                for phrase in result:
                    if phrase not in input_text:
                        logging.debug("The phrase should be a part of the input_text.")
                        continue 
                    if phrase in output:
                        output[phrase].append(result[phrase])
                        output[phrase] = list(set(output[phrase]))
                    else:
                        output[phrase] = [result[phrase]]
        if self.debug:
            return input_text, output, detailed_informations
        else:
            return input_text, output
    
    def detect(self):
        '''
        output form:
        {
            "user": xxx
            "assistant": xxx
            "privacy": {
                "phrase 1" : "privacy category 3",
                "phrase 2" : "privacy category 4"
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
                    privacy_leak = conv["privacy"]["judgment"]
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
                conv["privacy"] = output[index][1]
                if self.debug:
                    self.deltail_informations += output[index][2]
                index += 1

class PrivatePhraseMerger:
    def __init__(self, file_path, file_path_output, shot=None, language="en", debug=False) -> None:
        self.file_path = file_path
        self.file_path_output = file_path_output
        with open(file_path, encoding='utf-8') as f:
            self.data = json.load(f)[:shot]
        self.debug = debug
        self.gpt_error_count = 0
        self.language = language

    def _merge_phrases_with_rules(self, phrases):
        def _contained(phrase1, phrase2):
            if phrase1 in phrase2:
                return True
            else:
                return False

        contain_matrix = [[0 for _ in range(len(phrases))] for _ in range(len(phrases))]
        for i, phrase1 in enumerate(phrases):
            for j, phrase2 in enumerate(phrases):
                if _contained(phrase1, phrase2):
                    contain_matrix[i][j] = 1
        
        phrases_new = []
        for i in range(len(phrases)):
            if sum(contain_matrix[i]) <= 1:
                phrases_new.append(phrases[i])
        return phrases_new

    def _merge_phrases_for_one_text(self, input_text, phrases, skip=False):
        phrases = self._merge_phrases_with_rules(phrases)

        system = ""
        # system = "You are a helpful assistant."
        if self.language == "en":
            template = MERGE_PRIVATE_PHRASE_TEMPLATE_EN
        else:
            template = MERGE_PRIVATE_PHRASE_TEMPLATE_ZH
        message = template.replace("<|QUERY|>", input_text).replace("<|PHRASES|>", str(phrases))
        
        detailed_informations = []
        if not skip and len(phrases) > 0:
            if self.debug:
                result, raw_result = safe_chatgpt_for_json(message=message, system=system, debug=True)
                detailed_information = {"system": system, "message": message, "GPT_output": raw_result}
                detailed_informations.append(detailed_information)
            else:
                result = safe_chatgpt_for_json(message=message, system=system, debug=False)
        elif len(phrases) == 0:
            result = []
        else:
            result = "<|GPT_ERROR|>" ## debug skip this step

        if result == "<|GPT_ERROR|>":
            self.gpt_error_count += 1
            result = phrases
        if self.debug:
            return input_text, result, detailed_informations
        else:
            return input_text, result
    
    def merge_phrases(self, skip=False):
        '''
        input form: 
        {
            "user": xxx
            "assistant": xxx
            "privacy": {
                phrase 1: [category 1]
            }
        }
        output form:
        {
            "user": xxx
            "assistant": xxx
            "privacy": {
                "phrase": []
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
                    phrases = list(conv['privacy'].keys())
                    future = executor.submit(self._merge_phrases_for_one_text, input_text, phrases, skip)
                    future.add_done_callback(lambda p: process_bar.update(1))
                    all_tasks.append(future)

            output = [t.result() for t in all_tasks]
            process_bar.close()

        self.postpreprocess_output(output)
        logging.info("End Dectection with GPT ERROT: {}".format(self.gpt_error_count))

    def postpreprocess_output(self, output):
        self.data_output = self.data
        index = 0
        self.deltail_informations = []
        for item in self.data_output:
            for conv in item["conversation"]:
                assert conv["user"] == output[index][0], "Something wrong with the multithread, the data order is changed"
                conv["privacy"] = {"phrase": output[index][1]}
                if self.debug:
                    self.deltail_informations += output[index][2]
                index += 1

    def save(self):
        os.makedirs(os.path.split(self.file_path_output)[0], exist_ok=True)
        json.dump(self.data_output, open(self.file_path_output, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

    def save_detailed_information(self):
        output_path = self.file_path_output.replace(".json", "_detailed_info.json")
        os.makedirs(os.path.split(output_path)[0], exist_ok=True)
        json.dump(self.deltail_informations, open(output_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

class PrivatePhraseCleaner:
    def __init__(self, file_path, file_path_output, template, debug=False):
        self.file_path = file_path
        self.file_path_output = file_path_output
        logging.info("The input file is {}".format(file_path))
        logging.info("The output file is {}".format(file_path_output))
        with open(file_path, encoding='utf-8') as f:
            self.data = json.load(f)
        self.debug = debug
        self.gpt_error_count = 0
        self.template = template

    def _detect_for_one_text(self, input_text, phrases, template):
        result = {"judgment": True, "reason": ""}
        # system = "You are an expert in privacy detection."
        # system = "You are a helpful assistant."
        system = ""

        detailed_informations = []
        output_phrases = []
            
        for phrase in phrases:
            message = template.replace("<|QUERY|>", input_text).replace("<|PHRASE|>", str(phrase))
        
            if self.debug:
                result, raw_result = safe_chatgpt_for_json(message=message, system=system, debug=True)
                detailed_information = {"system": system, "message": message, "GPT_output": raw_result}
                detailed_informations.append(detailed_information)
            else:
                result = safe_chatgpt_for_json(message=message, system=system, debug=False)

            if result == "<|GPT_ERROR|>" or type(result) != dict or "judgment" not in result:
                self.gpt_error_count += 1
                result = {"judgment": True, "reason": ""}
            if result['judgment']:
                output_phrases.append(phrase)

        if self.debug:
            return input_text, output_phrases, detailed_informations
        else:
            return input_text, output_phrases

    def detect(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            all_tasks = []
            count = 0
            for item in self.data:
                count += len(item["conversation"])
            process_bar = tqdm(total=count)
            
            for item in self.data:
                for conv in item["conversation"]:
                    input_text = conv["user"]
                    phrases = conv['privacy']['phrase']
                    future = executor.submit(self._detect_for_one_text, input_text, phrases, self.template)
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
                conv["privacy"]['phrase'] = output[index][1]
                if self.debug:
                    self.deltail_informations += output[index][2]
                index += 1 

    def save(self):
        os.makedirs(os.path.split(self.file_path_output)[0], exist_ok=True)
        json.dump(self.data_output, open(self.file_path_output, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

    def save_detailed_information(self):
        output_path = self.file_path_output.replace(".json", "_detailed_info.json")
        os.makedirs(os.path.split(output_path)[0], exist_ok=True)
        json.dump(self.deltail_informations, open(output_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='private filter')
    parser.add_argument('--file_path', '-f', type=str, default="privacy_data/shareGPT/privacy_leaked/common_en_70k_example_0_10.json")
    parser.add_argument('--file_category_path', '-c', type=str, default="privacy_data/shareGPT/privacy_category/private_categories_merged.json")
    parser.add_argument('--file_output_dir', '-o', type=str, default="privacy_data/shareGPT/privacy_phrase/data_split_0_10")
    parser.add_argument('--language', '-l', type=str, default="en", choices=['en', 'zh']) # en: English & zh: Chinese
    args = parser.parse_args()

    ## [STEP 3-1] fine-grained detect private with given private categories
    file_path = args.file_path
    file_output_dir = args.file_output_dir
    file_path_output = os.path.join(file_output_dir, "finegrained.json")
    private_categories_file_path = args.file_category_path
    private_phrase_detector = PrivatePhraseDetector_WithCategory(file_path, file_path_output, private_categories_file_path, shot=None, debug=DEBUG, language=args.language)
    private_phrase_detector.detect()
    private_phrase_detector.save()
    private_phrase_detector.save_detailed_information()

    ## [STEP 3-2] remove similar phrases
    file_path = os.path.join(file_output_dir, "finegrained.json")
    file_path_output = os.path.join(file_output_dir, "finegrained_merge_phrase.json")
    private_phrase_merger = PrivatePhraseMerger(file_path, file_path_output, shot=None, debug=DEBUG, language=args.language)
    private_phrase_merger.merge_phrases(skip=False)
    private_phrase_merger.save()
    private_phrase_merger.save_detailed_information()

    ## [STEP 3-3] clean the phrases with rules - rule 1
    file_path = os.path.join(file_output_dir, "finegrained_merge_phrase.json")
    file_path_output = os.path.join(file_output_dir, "finegrained_merge_phrase_after_rule1.json")
    if args.language == "en":
        template = CLEAN_PRIVATE_ONE_PHRASE_RULE1_TEMPLATE_EN
    else:
        template = CLEAN_PRIVATE_ONE_PHRASE_RULE1_TEMPLATE_ZH
    private_phrase_cleaner = PrivatePhraseCleaner(file_path, file_path_output, template=template, debug=DEBUG)
    private_phrase_cleaner.detect()
    private_phrase_cleaner.save()
    private_phrase_cleaner.save_detailed_information()

    ## [STEP 3-4] clean the phrases with rules - rule 2
    file_path = os.path.join(file_output_dir, "finegrained_merge_phrase_after_rule1.json")
    file_path_output = os.path.join(file_output_dir, "finegrained_merge_phrase_final.json")
    if args.language == "en":
        template = CLEAN_PRIVATE_ONE_PHRASE_RULE2_TEMPLATE_EN
    else:
        template = CLEAN_PRIVATE_ONE_PHRASE_RULE2_TEMPLATE_ZH
    private_phrase_cleaner = PrivatePhraseCleaner(file_path, file_path_output, template=template, debug=DEBUG)
    private_phrase_cleaner.detect()
    private_phrase_cleaner.save()
    private_phrase_cleaner.save_detailed_information()
