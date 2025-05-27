from openai import OpenAI
import json 
import re
import openai 
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s[line:%(lineno)d] - [%(levelname)s]: %(message)s')
logging.getLogger("requsets").setLevel(logging.ERROR)
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

def generate(message, system, model_name):
    api_base = "<YOUR_API_BASE>"
    api_key = "<YOUR_API_KEY>"

    client = OpenAI(api_key=api_key, base_url=api_base)
    messages = [
                {"role": "system", "content": system},
                {"role": "user", "content":  message},
    ]
    chat_response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                timeout=600,
                temperature=0
    )
    return chat_response

def safe_chatgpt_for_json(message, system, model_name, debug=False):
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
            chat_response = generate(message, system, model_name)
            response_raw = chat_response.choices[0].message.content
            response = _get_json_from_response(response_raw)
            assert response != None, "response is None."
            if debug:
                return response, response_raw
            else:
                return response
        except openai.PermissionDeniedError as e:
            logging.info("PermissionDeniedError: {}".format(e))
            logging.info("Permission Denied openai api - count {}".format(retry_count))
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
        except json.decoder.JSONDecodeError as e:
            logging.info("JSON DECODE ERROR")
            logging.debug('Retry....')
            retry_count += 1
            retry_interval += 1  
            time.sleep(retry_interval)
        except openai.InternalServerError as e:
            logging.info("OpenAI error: http 400")
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
        return "<|API_ERROR|>", "<|API_ERROR|>"
    else:
        return "<|API_ERROR|>"

if __name__ == "__main__":
    system = ""
    message = "how far？"
    model_name = "qwen2.5-72b-instruct"
    response = generate(message, system, model_name)
    print(response.choices[0].message.content)