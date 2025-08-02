from GPTAPI import safe_chatgpt, safe_chatgpt_for_json, safe_chatgpt_for_bool
from detect_private_leakage_GPT_TEMPLATE import *

import json 
import os
from tqdm import tqdm
import concurrent.futures
import logging
from random import shuffle
import argparse
import math
import copy
import openai
import time

os.makedirs("logs", exist_ok=True)
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - [%(levelname)s]: %(message)s' 
                    )
# Disable openai logger
logging.getLogger("requsets").setLevel(logging.ERROR)
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

MAX_WORKERS = 8

class PrivateDataFilter:
    def __init__(self, file_path, file_path_output, start_idx=0, end_idx=None, language='en', debug=False):
        self.file_path = file_path
        self.file_path_output = file_path_output
        # load preprocessed data
        logging.info("The input file is {}".format(file_path))
        logging.info("The output file is {}".format(file_path_output))
        with open(file_path, encoding='utf-8') as f:
            self.data = json.load(f)[start_idx:end_idx]
        logging.info("The length of input file: {}".format(len(self.data)))

        self.language = language
        # if debug, the original response from LLM will be recorded
        self.debug = debug
        self.gpt_error_count = 0

    def _detect_for_one_text(self, input_text):
        system = ""
        if self.language == 'en':
            template = DATASET_PRIVACY_FILTER_TEMPLATE_EN
        else:
            template = DATASET_PRIVACY_FILTER_TEMPLATE_ZH
        message = template.replace("<|QUERY|>", input_text)

        detailed_informations = []
        # pose requests to LLM API
        if self.debug:
            result, raw_result = safe_chatgpt_for_json(message=message, system=system, debug=True)
            detailed_information = {"system": system, "message": message, "GPT_output": raw_result}
            detailed_informations.append(detailed_information)
        else:
            result = safe_chatgpt_for_json(message=message, system=system, debug=False)

        if result == "<|GPT_ERROR|>" or "judgement" not in result:
            self.gpt_error_count += 1
            result = {"reason": "<|GPT_ERROR_IN_CODE|>", "judgement": False}
        
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
            "privacy": {
                "reason": xxx,
                "result": true or false
            } 
        }
        '''
        # multi-thread
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            all_tasks = []
            count = 0
            for item in self.data:
                count += len(item["conversation"])
            process_bar = tqdm(total=count)
            
            for item in self.data:
                for conv in item["conversation"]:
                    input_text = conv["user"]
                    # pose requests to LLM API
                    future = executor.submit(self._detect_for_one_text, input_text)
                    future.add_done_callback(lambda p: process_bar.update(1))
                    all_tasks.append(future)

            output = [t.result() for t in all_tasks]
            process_bar.close()

        # merge the final output
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

    def save(self):
        os.makedirs(os.path.split(self.file_path_output)[0], exist_ok=True)
        json.dump(self.data_output, open(self.file_path_output, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

    def save_detailed_information(self):
        output_path = self.file_path_output.replace(".json", "_detailed_info.json")
        os.makedirs(os.path.split(output_path)[0], exist_ok=True)
        json.dump(self.deltail_informations, open(output_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='private filter')
    parser.add_argument('--file_path', '-f', type=str, default="preprocess_data/shareGPT/common_en_70k_example.json")
    parser.add_argument('--file_path_output', '-o', type=str, default="privacy_data/shareGPT/privacy_leaked/common_en_70k_example.json")
    parser.add_argument('--language', '-l', type=str, default="en", choices=['en', 'zh']) # en: English & zh: Chinese
    parser.add_argument('--start_idx', '-s', type=int, default=0)
    parser.add_argument('--end_idx', '-e', type=int, default=None)
    args = parser.parse_args()

    # Since the raw data is often too long, it is recommended to split it into smaller segments using the predefined parameters start_idx and end_idx.
    start_idx = args.start_idx
    end_idx = args.end_idx
    logging.info("Start detece private leakage: start idx {} - end idx {}".format(start_idx, end_idx))
    file_path = args.file_path
    file_path_output = args.file_path_output.replace(".json", f"{start_idx}_{end_idx}.json")
    private_category_detector = PrivateDataFilter(file_path, file_path_output, start_idx=0, end_idx=None, language=args.language, debug=True)
    # detect privacy leakage
    private_category_detector.detect()
    # save the result
    private_category_detector.save()
    private_category_detector.save_detailed_information()