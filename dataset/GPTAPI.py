import requests
import json
import openai
from openai import OpenAI
import concurrent.futures
from tqdm import tqdm
import time
import re
import os
import logging
from detect_private_leakage_GPT_TEMPLATE import *

os.makedirs("logs", exist_ok=True)
logging.basicConfig(level=logging.INFO, 
                    # filename='logs/detect_GPT.log',
                    # filemode='a',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - [%(levelname)s]: %(message)s' 
                    )
logging.getLogger("requsets").setLevel(logging.ERROR)
logging.getLogger("_trace.py").setLevel(logging.ERROR)
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)


def chatgpt(message, system="You are a helpful assistant."):
    '''
    res = chatgpt("Who are you?")
    response = res.content.decode()
    response = json.loads(response)
    print(response['data']['choices'][0]['message']['content'])
    '''

    openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    model_name = "gpt-4o-2024-08-06"
    client = OpenAI(api_key=openai_api_key)
    messages = [
                {"role": "system", "content": system},
                {"role": "user", "content":  message},
    ]
    chat_response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                timeout=60,
                temperature=0
    )
    return chat_response


def safe_chatgpt(message, system="You are a helpful assistant."):
    retry_count = 10
    retry_interval = 1
    for _ in range(retry_count):
        try:
            chat_response = chatgpt(message, system)
            response = chat_response.choices[0].message.content
            return response
        except openai.PermissionDeniedError as e:
            logging.info("Permission Denied openai api")
            logging.debug('Retry....')
            retry_count += 1
            retry_interval *= 2  
            time.sleep(retry_interval)
        except openai.RateLimitError as e:
            logging.info("Excess openai api Rate")
            logging.debug('Retry....')
            retry_count += 1
            retry_interval *= 2  
            time.sleep(retry_interval)
        except openai.InternalServerError as e:
            print("OpenAI error: http 400")
            break
        except Exception as e:
            logging.info("Something Wrong with the task: {}".format(e))
            logging.debug('Retry....')
            retry_count += 1
            retry_interval += 1
            time.sleep(retry_interval)
    return "<|GPT_ERROR|>"

def safe_chatgpt_for_json(message, system="You are a helpful assistant.", debug=False):
    def _get_json_from_response(response):
        try:
            result = json.loads(response)
        except:
            pattern = re.compile(r'```json\n(.*?)```', re.DOTALL)
            match = pattern.search(response)
            
            if match:
                result = match.group(1)
                result = json.loads(result)
            else:
                result = None
        return result

    retry_count = 0
    retry_count_max = 10
    retry_interval = 1
    while retry_count < retry_count_max:
        try:
            chat_response = chatgpt(message, system)
            response_raw = chat_response.choices[0].message.content
            response = _get_json_from_response(response_raw)
            assert response != None, "response is None."
            if debug:
                return response, response_raw
            else:
                return response
        except openai.PermissionDeniedError as e:
            logging.debug("PermissionDeniedError: {}".format(e))
            logging.debug("Permission Denied openai api - count {}".format(retry_count))
            logging.debug('Retry....')
            retry_count += 1
            retry_interval *= 2  
            time.sleep(retry_interval)
        except openai.RateLimitError as e:
            logging.debug("Excess openai api Rate")
            logging.debug('Retry....')
            retry_count += 1
            retry_interval *= 2  
            time.sleep(retry_interval)
        except json.decoder.JSONDecodeError as e:
            logging.info("JSON DECODE ERROR")
            logging.debug('Retry....')
            retry_count += 1
            retry_interval += 1  
            time.sleep(retry_interval)
        except openai.InternalServerError as e:
            logging.info("OpenAI error: http 400")
            # print(message)
            retry_count += 10
            retry_interval += 1  
            time.sleep(retry_interval)
        except Exception as e:
            logging.info("Something Wrong with the task: {}".format(e))
            logging.debug('Retry....')
            retry_count += 1
            retry_interval += 1 
            time.sleep(retry_interval)
    if debug:
        return "<|GPT_ERROR|>", "<|GPT_ERROR|>"
    else:
        return "<|GPT_ERROR|>"

def safe_chatgpt_for_bool(message, system="You are a helpful assistant."):
    retry_count = 10
    retry_interval = 1
    for _ in range(retry_count):
        try:
            chat_response = chatgpt(message, system)
            response = chat_response.choices[0].message.content
            response = response.replace("\"", "").replace("\'", "")
            assert response in ["True", "False"], "GPT Response {} not in [True, False].".format(response)
            response = response == "True"
            return response
        except openai.PermissionDeniedError as e:
            logging.debug("Permission Denied openai api")
            logging.debug('Retry....')
            retry_count += 1
            retry_interval *= 2  
            time.sleep(retry_interval)
        except openai.RateLimitError as e:
            logging.debug("Excess openai api Rate")
            logging.debug('Retry....')
            retry_count += 1
            retry_interval *= 2  
            time.sleep(retry_interval)
        except json.decoder.JSONDecodeError as e:
            logging.debug("JSON DECODE ERROR")
            logging.debug('Retry....')
            retry_count += 1
            retry_interval += 1  
            time.sleep(retry_interval)
        except openai.InternalServerError as e:
            print("OpenAI error: http 400")
            break
        except Exception as e:
            logging.debug("Something Wrong with the task: {}".format(e))
            logging.debug('Retry....')
            retry_count += 1
            retry_interval += 1 
            time.sleep(retry_interval)
    return "<|GPT_ERROR|>"


if __name__ == "__main__":
    # system = "You are a helpful assistant."
    system = ""
    message = '''who are you. 
output your result in following format:
```json
{
    "response": xxx
}
```
'''

    print(message)
    print("======================")
    result, result_raw = safe_chatgpt_for_json(message=message, system=system, debug=True)
    print(result_raw)
    print("======================")
    print(result)
