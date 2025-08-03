import json 
import argparse
import os
import copy
import re
 
def merge_result(output_dir):
    exist_str = []
    results = []
    for file in os.listdir(output_dir):
        if "rank" in file:
            with open(os.path.join(output_dir, file)) as f:
                data = json.load(f)
            for item in data:
                if item['id'] not in exist_str:
                    results.append(item)
                    exist_str.append(item['id'])
    print("RESULT LEN", len(results))
    json.dump(results, open(os.path.join(output_dir, "privacy_information_merged_dev.json"), 'w'), ensure_ascii=False, indent=4)
    return results

def get_json_from_response(response):
        try:
            result = json.loads(response)
        except:
            pattern = re.compile(r'```json\n(.*?)```', re.DOTALL)
            match = re.findall(pattern, response)
            
            if len(match) > 0:
                result = match[-1]
                try:
                    result = json.loads(result)
                except:
                    result = None
            else:
                result = None
        return result

def merge_raw_data(output_results, raw_data, output_dir):
    error_count = 0

    id2result = {item['id']: item for item in output_results}
    assert len(id2result) == len(output_results), "Output id is repeated."
    
    new_data = copy.copy(raw_data)
    for item in new_data:
        id = item['id']
        for i, conv in enumerate(item['conversation']):
            identity = f"{id}_part{i}"
            response = id2result[identity]['response']
            json_output = get_json_from_response(response)
            if json_output is None:
                json_output = {"judgement": "true" in response}
                error_count += 1
            conv['privacy'] = json_output
    print("Generation Error Count:", error_count)
    json.dump(new_data, open(os.path.join(output_dir, "privacy_information_dev.json"), 'w'), ensure_ascii=False, indent=4)
    return new_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='argparse')
    parser.add_argument('--raw_data', '-d', type=str, default="dataset/privacy_data/shareGPT/privacy_information_dev.json", help="raw data")
    parser.add_argument('--output_dir', '-o', type=str, default="output/shareGPT_leakage_only/Qwen_zero-shot/Qwen2.5-72B-Instruct", help="output dir")
    args = parser.parse_args()

    with open(args.raw_data) as f:
        raw_data = json.load(f)
    conv_num = 0
    for item in raw_data:
        conv_num += len(item['conversation'])
    print("CONV_NUM", conv_num)

    output_dir = args.output_dir
    output_results = merge_result(output_dir)
    new_data = merge_raw_data(output_results, raw_data, output_dir)
    print(len(new_data))