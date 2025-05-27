import os
import json
from rouge import Rouge
import argparse
import pickle

DEBUG_RECALL = False  
DEBUG_PRECISION = False

def load_data(file_path):
    data = []
    if type(file_path) == str:
        file_path = [file_path]
    assert type(file_path) == list, "type of file path should be list or str."
    for fp in file_path:
        with open(fp, 'r', encoding='utf-8') as f:
            data += json.load(f)
    return data

def get_phrase(privacy, phrase_only=False):
    phrases = []
    if phrase_only:
        return privacy
    for item in privacy:
        if "phrase" in item:
            phrases.append(item['phrase'])
    return phrases

def phrase_judge(phrase1, phrase2, language="en"):
    ## match rule 1
    rouge = Rouge()
    ## English
    if language == "en":
        rouge_l = rouge.get_scores([phrase2], [phrase1])[0]['rouge-l']['f']
    ## Chinese
    else:
        rouge_l = rouge.get_scores([" ".join(list(phrase2))], [" ".join(list(phrase1))])[0]['rouge-l']['f']
    if rouge_l > 0.5:
        return True

    ## match rule 2    
    phrase1 = phrase1.replace(" ", "").replace("\n", "").replace(",", "").lower()
    phrase2 = phrase2.replace(" ", "").replace("\n", "").replace(",", "").lower()
    if phrase1 in phrase2 or phrase2 in phrase1:
        return True

    return False

def count_phrase_num(prediction, phrase_only=False):
    count_phrase = 0
    count_conversation_num = 0
    count_query_num = 0
    for item_pred in prediction:
        for conv_pred in item_pred['conversation']:
            phrases_pred = get_phrase(conv_pred['privacy'], phrase_only)
            count_phrase += len(phrases_pred)
            count_query_num += 1
        count_conversation_num += 1
    return count_phrase, count_conversation_num, count_query_num

def recall_score_one(phrase_gt, phrase_pred, input_text, language="en"):
    if len(phrase_gt) == 0:
        return -1
    count = 0
    for e in phrase_gt:
        for e_p in phrase_pred:
            if phrase_judge(e, e_p, language):
                count += 1
                break
    result = count / len(phrase_gt)
    if result < 1 and DEBUG_RECALL:
        print("=============================================================", result)
        print(input_text)
        print(phrase_gt)
        print(phrase_pred)
    return result

def precision_score_one(phrase_gt, phrase_pred, input_text, language="en"):
    if len(phrase_pred) == 0:
        return -1
    count = 0
    for e_p in phrase_pred:
        for e in phrase_gt:
            if phrase_judge(e, e_p, language):
                count += 1
                break
    result = count / len(phrase_pred)
    if result < 1 and DEBUG_PRECISION:
        print("=============================================================", result)
        print(input_text)
        print(phrase_gt)
        print(phrase_pred)
    return result

def recall_score(ground_truth, prediction, phrase_only=False, language="en"):
    recall_score_list = []
    for item_gt, item_pred in zip(ground_truth, prediction):
        for conv_gt, conv_pred in zip(item_gt['conversation'], item_pred['conversation']):
            phrases_gt = get_phrase(conv_gt['privacy'])
            phrases_pred = get_phrase(conv_pred['privacy'], phrase_only)
            input_text = conv_gt['user']
            score = recall_score_one(phrases_gt, phrases_pred, input_text, language)
            if score != -1:
                recall_score_list.append(score)
    print("recall len", len(recall_score_list))
    return sum(recall_score_list) / len(recall_score_list), recall_score_list

def precision_score(ground_truth, prediction, phrase_only=False, language="en"):
    precision_score_list = []
    for item_gt, item_pred in zip(ground_truth, prediction):
        for conv_gt, conv_pred in zip(item_gt['conversation'], item_pred['conversation']):
            phrases_gt = get_phrase(conv_gt['privacy'])
            phrases_pred = get_phrase(conv_pred['privacy'], phrase_only)
            input_text = conv_gt['user']
            score = precision_score_one(phrases_gt, phrases_pred, input_text, language)
            if score != -1:
                precision_score_list.append(score)
    print("precision len", len(precision_score_list))
    return sum(precision_score_list) / len(precision_score_list), precision_score_list

def get_idphrase(item):
    idphrase = item['id']
    for conv in item["conversation"]:
        idphrase += conv['user']
    return idphrase 

def get_intersection(ground_truth, prediction):
    print("length of ground truth: {} prediction: {}".format(len(ground_truth), len(prediction)))
    idphrases = [get_idphrase(item) for item in ground_truth]
    data_sub = []
    for item in prediction:
        if get_idphrase(item) in idphrases:
            data_sub.append(item)
    # assert len(data_sub) == len(ground_truth), "prediction_sub {} != ground truth {}, there is some item in ground truth but not in prediction.".format(len(data_sub), len(ground_truth))
    return data_sub

def reform_data_order(ground_truth, prediction):
    data_new = []
    idphrases = [get_idphrase(item) for item in ground_truth]
    id2item = {get_idphrase(item): item for item in prediction}
    for id in idphrases:
        data_new.append(id2item[id])
    return data_new

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='argparse')
    parser.add_argument('--label_file_path', '-l', type=str, default='dataset/privacy_data/shareGPT/privacy_information_dev.json', help="raw data")
    parser.add_argument('--pred_file_path', '-p', type=str, default="output/shareGPT/Qwen_zero-shot/Qwen2.5-72B-Instruct/privacy_information_dev.json", help="output dir")
    parser.add_argument('--language', type=str, default="en", help="")

    args = parser.parse_args()
    phrase_only = True
    print(args.pred_file_path)
    if not os.path.exists(args.pred_file_path):
        print("Not Exist")
        exit()

    label_file_path = args.label_file_path
    ground_truth = load_data(label_file_path)

    pred_file_path = args.pred_file_path
    prediction = load_data(pred_file_path) 
    prediction = get_intersection(ground_truth, prediction)
    prediction = reform_data_order(ground_truth, prediction)

    print(count_phrase_num(ground_truth))
    print(count_phrase_num(prediction, phrase_only=phrase_only))
    rs, rs_list = recall_score(ground_truth, prediction, phrase_only=phrase_only, language=args.language)
    ps, ps_list = precision_score(ground_truth, prediction, phrase_only=phrase_only, language=args.language)
    print("Recall {:.4f}  Precision {:.4f}".format(rs, ps))
    
    ## save result
    output_dir = os.path.split(pred_file_path)[0]
    result_path = os.path.join(output_dir, "result.json")
    if os.path.exists(result_path):
        results = json.load(open(result_path))
    else:
        results = {}
    results['Recall_P'] = rs 
    results['Precision_P'] = ps 
    results['F1_P'] = 2*rs*ps / (rs+ps)
    json.dump(results, open(result_path, 'w'), ensure_ascii=False, indent=4)

    ## pickle result
    output_dir = os.path.split(pred_file_path)[0]
    result_score_path = os.path.join(output_dir, "result_score.pkl")
    if os.path.exists(result_score_path):
        with open(result_score_path, "rb") as f:
            score_list = pickle.load(f)
    else:
        score_list = {}
    score_list["recall_P"] = rs_list
    score_list["precision_P"] = ps_list
    score_list["F1_P"] = 2*rs*ps / (rs+ps)
    with open(result_score_path, "wb") as f:
        pickle.dump(score_list, f)
