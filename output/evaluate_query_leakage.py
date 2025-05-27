import os
import json
import argparse
import pickle

DEBUG_ACC = False 

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

def get_leakage(privacy):
    leakage = False
    if "judgement" in privacy:
        leakage = privacy['judgement']
        if type(leakage) != bool:
            leakage = False 
    return leakage

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

def accuracy_score_one(phrase_gt, leakage_pred, input_text):
    leakage_gt = len(phrase_gt) != 0
    result = int(leakage_pred == leakage_gt)
    if DEBUG_ACC and result == 0:
        print("===================================================")
        print(input_text)
        print(phrase_gt)
        print(leakage_pred)
        print("===================================================")
    return result


def accuracy_score(ground_truth, prediction):
    acc_score_list = []
    for item_gt, item_pred in zip(ground_truth, prediction):
        for conv_gt, conv_pred in zip(item_gt['conversation'], item_pred['conversation']):
            phrases_gt = get_phrase(conv_gt['privacy'])
            leakage_pred = get_leakage(conv_pred['privacy'])
            input_text = conv_gt['user']
            score = accuracy_score_one(phrases_gt, leakage_pred, input_text)
            acc_score_list.append(score)
    print("accuracy len", len(acc_score_list))
    return sum(acc_score_list) / len(acc_score_list), acc_score_list

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

    args = parser.parse_args()
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
    acc, acc_list = accuracy_score(ground_truth, prediction)
    print("Accuracy {:.4f}".format(acc))
    
    ## save result
    output_dir = os.path.split(pred_file_path)[0]
    result_path = os.path.join(output_dir, "result.json")
    if os.path.exists(result_path):
        results = json.load(open(result_path))
    else:
        results = {}
    results['Accuracy'] = acc 
    json.dump(results, open(result_path, 'w'), ensure_ascii=False, indent=4)

    ## numpy
    output_dir = os.path.split(pred_file_path)[0]
    result_score_path = os.path.join(output_dir, "acc_score.pkl")
    if os.path.exists(result_score_path):
        with open(result_score_path, "rb") as f:
            score_list = pickle.load(f)
            if type(score_list) != dict:
                score_list = {}
    else:
        score_list = {}
    score_list['acc'] = acc_list
    with open(result_score_path, "wb") as f:
        pickle.dump(score_list, f)
