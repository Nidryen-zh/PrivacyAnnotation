import json 
import os 
from rouge import Rouge
import argparse

rouge = Rouge()

def load_data(file_path):
    data = []
    if type(file_path) == str:
        file_path = [file_path]
    assert type(file_path) == list, "type of file path should be list or str."
    for fp in file_path:
        with open(fp, 'r', encoding='utf-8') as f:
            data += json.load(f)
    return data

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
    assert len(data_sub) == len(ground_truth), "prediction_sub {} != ground truth {}, there is some item in ground truth but not in prediction.".format(len(data_sub), len(ground_truth))
    return data_sub

def get_phrase(privacy):
    phrases = []
    for item in privacy:
        if "phrase" in item:
            phrases.append(item['phrase'])
    return phrases

def get_privacy_information(privacy):
    info = []
    for item in privacy:
        if "privacy information" in item:
            info.append(item['privacy information'])
    return info

def count_phrase_num(prediction):
    count_phrase = 0
    count_conversation_num = 0
    count_query_num = 0
    for item_pred in prediction:
        for conv_pred in item_pred['conversation']:
            phrases_pred = get_phrase(conv_pred['privacy'])
            count_phrase += len(phrases_pred)
            count_query_num += 1
        count_conversation_num += 1
    return count_phrase, count_conversation_num, count_query_num

def reform_data_order(ground_truth, prediction):
    data_new = []
    idphrases = [get_idphrase(item) for item in ground_truth]
    id2item = {get_idphrase(item): item for item in prediction}
    for id in idphrases:
        data_new.append(id2item[id])
    return data_new

def preprocess_privacy_info(privacy_info, language):
    if language == "en":
        return privacy_info
    privacy_info_new = []
    for info in privacy_info:
        privacy_info_new.append(" ".join(list(info)))
    return privacy_info_new

def compute_recall_rouge_for_one(privacy_info_gt, privacy_info_pred, language):
    recall_rouges = []

    privacy_info_gt = preprocess_privacy_info(privacy_info_gt, language)
    privacy_info_pred = preprocess_privacy_info(privacy_info_pred, language)

    for info_gt in privacy_info_gt:
        max_recall_rouge = 0
        for info_pred in privacy_info_pred:
            if type(info_pred) != str:
                info_pred = "Leaks privacy."
            recall_rouge = rouge.get_scores(info_gt, info_pred)[0]['rouge-l']['f']
            max_recall_rouge = max(max_recall_rouge, recall_rouge)
        recall_rouges.append(max_recall_rouge)
    
    recall_rouge = sum(recall_rouges) / len(recall_rouges)
    return recall_rouge
    

def compute_precision_rouge_for_one(privacy_info_gt, privacy_info_pred, language):
    precision_rouges = []

    privacy_info_gt = preprocess_privacy_info(privacy_info_gt, language)
    privacy_info_pred = preprocess_privacy_info(privacy_info_pred, language)

    for info_pred in privacy_info_pred:
        if type(info_pred) != str:
            info_pred = "Leaks privacy."
        max_precision_rouge = 0
        for info_gt in privacy_info_gt:
            ## English
            precision_rouge = rouge.get_scores(info_pred, info_gt)[0]['rouge-l']['f']
            ## Chinese
            max_precision_rouge = max(max_precision_rouge, precision_rouge)
        precision_rouges.append(max_precision_rouge)

    precision_rouge = sum(precision_rouges) / len(precision_rouges)
    return precision_rouge
    

def compute_precision_rouge(ground_truth, prediction, language):
    score_list = []
    for item_gt, item_pred in zip(ground_truth, prediction):
        for conv_gt, conv_pred in zip(item_gt['conversation'], item_pred['conversation']):
            privacy_info_gt = get_privacy_information(conv_gt['privacy'])
            privacy_info_pred = get_privacy_information(conv_pred['privacy'])
            if len(privacy_info_pred) == 0: continue
            input_text = conv_gt['user']
            score = compute_precision_rouge_for_one(privacy_info_gt, privacy_info_pred, language)
            score_list.append(score)
    print("score len", len(score_list))
    return sum(score_list) / len(score_list)

def compute_recall_rouge(ground_truth, prediction, language):
    score_list = []
    for item_gt, item_pred in zip(ground_truth, prediction):
        for conv_gt, conv_pred in zip(item_gt['conversation'], item_pred['conversation']):
            privacy_info_gt = get_privacy_information(conv_gt['privacy'])
            privacy_info_pred = get_privacy_information(conv_pred['privacy'])
            if len(privacy_info_gt) == 0: continue
            input_text = conv_gt['user']
            score = compute_recall_rouge_for_one(privacy_info_gt, privacy_info_pred, language)
            score_list.append(score)
    print("score len", len(score_list))
    return sum(score_list) / len(score_list)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='argparse')
    parser.add_argument('--label_file_path', '-l', type=str, default='dataset/privacy_data/shareGPT/privacy_information_dev.json', help="raw data")
    parser.add_argument('--pred_file_path', '-p', type=str, default="output/shareGPT/Qwen_zero-shot/Qwen2.5-72B-Instruct/privacy_information_dev.json", help="output dir")
    parser.add_argument('--language', type=str, default="en", help="output dir")
    args = parser.parse_args()

    label_file_path = args.label_file_path
    if type(label_file_path) == str and (not os.path.exists(label_file_path)):
        import datasets
        dataset = datasets.load_dataset(label_file_path, args.language)
        ground_truth = dataset['test']
    else:
        ground_truth = load_data(label_file_path)


    pred_file_path = args.pred_file_path
    prediction = load_data(pred_file_path) 
    prediction = get_intersection(ground_truth, prediction)
    prediction = reform_data_order(ground_truth, prediction)

    print(count_phrase_num(ground_truth))
    print(count_phrase_num(prediction))
    rs = compute_recall_rouge(ground_truth, prediction, args.language)
    ps = compute_precision_rouge(ground_truth, prediction, args.language)
    print("Recall", rs)
    print("Precision", ps)

    ## save result
    output_dir = os.path.split(pred_file_path)[0]
    result_path = os.path.join(output_dir, "result.json")
    if os.path.exists(result_path):
        with open(result_path) as f:
            results = json.load(f)
    else:
        results = {}
    results['Recall_I'] = rs 
    results['Precision_I'] = ps 
    results['F1_I'] = 2*rs*ps / (rs+ps)
    json.dump(results, open(result_path, 'w'), ensure_ascii=False, indent=4)

