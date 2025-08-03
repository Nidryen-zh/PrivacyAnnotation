from GPTAPI import safe_chatgpt, safe_chatgpt_for_json
from detect_private_information_GPT_TEMPLATE import *

import json 
import os
from tqdm import tqdm
import concurrent.futures
import logging
from random import shuffle
import math
import copy
import openai
import time
import argparse

os.makedirs("logs", exist_ok=True)
logging.basicConfig(level=logging.INFO, 
                    # filename='logs/detect_GPT.log',
                    # filemode='a',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - [%(levelname)s]: %(message)s' 
                    )
# Disable openai logger
logging.getLogger("requsets").setLevel(logging.ERROR)
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

MAX_WORKERS = 8
DEBUG = True

class PrivateDetector:
    def __init__(self, file_path, file_path_output, shot=None, language="en"):
        logging.info("The input file is {}".format(file_path))
        logging.info("The output file is {}".format(file_path_output))
        self.file_path = file_path
        self.file_path_output = file_path_output
        with open(file_path, encoding='utf-8') as f:
            self.data = json.load(f)[:shot]
        self.gpt_error_count = 0
        self.language = language

    def _detect_privacy_for_one_text(self, input_text):
        """detect private info from a text

        Args:
            input_text (str): plain text
        """
        pass
    
    def detect_privacy(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            all_tasks = []
            count = 0
            for item in self.data:
                count += len(item["conversation"])
            process_bar = tqdm(total=count)
            
            for item in self.data:
                for conv in item["conversation"]:
                    input_text = conv["user"]
                    future = executor.submit(self._detect_privacy_for_one_text, input_text)
                    future.add_done_callback(lambda p: process_bar.update(1))
                    all_tasks.append(future)

            output = [t.result() for t in all_tasks]
            process_bar.close()

        self.postpreprocess_output(output)
        logging.info("End Dectection with GPT ERROT: {}".format(self.gpt_error_count))
        
    def postpreprocess_output(self, output):
        pass

    def save(self):
        os.makedirs(os.path.split(self.file_path_output)[0], exist_ok=True)
        json.dump(self.data_output, open(self.file_path_output, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
 
        
class PrivateInfoWithPhraseDetector(PrivateDetector):
    def __init__(self, file_path, file_path_output, shot=None, language="en"):
        super().__init__(file_path, file_path_output, shot, language)

    def _detect_privacy_for_one_text(self, input_text, phrases) -> dict:
        """detect private info and phrase from a text

        Args:
            input_text (str): plain text

        {
            "phrase": PHRASE,
            "privacy information": PRIVACY_INFORMATION
        }

        Returns:
            dict: detected private info and phrase
        """

        output = {}
        detailed_informations = []
        # system = "You are an expert in privacy information detection."
        system = ""
        
        result = {}
        for e in phrases:
            if self.language == "en":
                template = DETECT_PRIVATE_INFO_WITH_PHRASE_TEMPLATE_EN
            else:
                template = DETECT_PRIVATE_INFO_WITH_PHRASE_TEMPLATE_ZH
            message = template.replace("<|QUERY|>", input_text)
            message = message.replace("<|PHRASE|>", e)
            output, raw_result = safe_chatgpt_for_json(message=message, system=system, debug=DEBUG)
            if DEBUG:
                detailed_information = {"system": system, "message": message, "GPT_output": raw_result}
                detailed_informations.append(detailed_information)
            if output == "<|GPT_ERROR|>" or type(output) != dict:
                self.gpt_error_count += 1
                output = {"phrase": e, "privacy information": "<|GPT_ERROR|>"}
            result[e] = output
        if DEBUG:
            return input_text, result, detailed_informations
        else:
            return input_text, result
        
    def postpreprocess_output(self, output):
        self.data_output = self.data
        self.deltail_informations = []
        index = 0
        for item in self.data_output:
            for conv in item["conversation"]:
                assert conv["user"] == output[index][0], "Something wrong with the multithread, the data order is changed"
                conv["privacy"] = output[index][1]
                if DEBUG:
                    self.deltail_informations += output[index][2]
                index += 1

    def detect_privacy(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            all_tasks = []
            count = 0
            for item in self.data:
                count += len(item["conversation"])
            process_bar = tqdm(total=count)
            
            for item in self.data:
                for conv in item["conversation"]:
                    input_text = conv["user"]
                    phrases = conv["privacy"]["phrase"]
                    future = executor.submit(self._detect_privacy_for_one_text, input_text, phrases)
                    future.add_done_callback(lambda p: process_bar.update(1))
                    all_tasks.append(future)

            output = [t.result() for t in all_tasks]
            process_bar.close()

        self.postpreprocess_output(output)
        logging.info("End Dectection with GPT ERROT: {}".format(self.gpt_error_count))

    def save_detailed_information(self):
        output_path = self.file_path_output.replace(".json", "_detailed_info.json")
        os.makedirs(os.path.split(output_path)[0], exist_ok=True)
        json.dump(self.deltail_informations, open(output_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='private filter')
    parser.add_argument('--file_path', '-f', type=str, default="privacy_data/shareGPT/privacy_phrase/data_split_0_10/finegrained_merge_phrase_final.json")
    parser.add_argument('--file_path_output', '-o', type=str, default="privacy_data/shareGPT/privacy_information/data_split_0_10/privacy_information.json")
    parser.add_argument('--language','-l',type=str, default="en")
    args = parser.parse_args()

    file_path = args.file_path
    file_path_output = args.file_path_output
    private_info_detector = PrivateInfoWithPhraseDetector(file_path, file_path_output, language=args.language)
    private_info_detector.detect_privacy()
    private_info_detector.save()
    private_info_detector.save_detailed_information()
