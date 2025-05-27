import numpy as np 
import os
from scipy import stats
import pandas as pd
import pickle

result_list = {}

## Chinese - information
# result_list['Zero_Llama-3.2-1B-Instruct'] = "/mnt/SSD1/zenghang/QueryRewriting/output/Chinese/Llama_zero-shot/Llama-3.2-1B-Instruct/result_score.pkl"
# result_list['Zero_Llama-3.2-3B-Instruct'] = "/mnt/SSD1/zenghang/QueryRewriting/output/Chinese/Llama_zero-shot/Llama-3.2-3B-Instruct/result_score.pkl"
# result_list['Zero_Llama-3.1-8B-Instruct'] = "/mnt/SSD1/zenghang/QueryRewriting/output/Chinese/Llama_zero-shot/Llama-3.1-8B-Instruct/result_score.pkl"
# result_list['Zero_Qwen2.5-1.5B-Instruct'] = "/mnt/SSD1/zenghang/QueryRewriting/output/Chinese/Qwen_zero-shot_013115/Qwen2.5-1.5B-Instruct/result_score.pkl"
# result_list['Zero_Qwen2.5-3B-Instruct']   = "/mnt/SSD1/zenghang/QueryRewriting/output/Chinese/Qwen_zero-shot/Qwen2.5-3B-Instruct/result_score.pkl"
# result_list['Tune_Llama-3.2-1B-Instruct'] = "/mnt/SSD1/zenghang/QueryRewriting/output/Chinese/meta-llama/Llama-3.2-1B-Instruct/checkpoint-800_merged/evaluate_result/result_score.pkl"
# result_list['Tune_Llama-3.2-3B-Instruct'] = "/mnt/SSD1/zenghang/QueryRewriting/output/Chinese/meta-llama/Llama-3.2-3B-Instruct/checkpoint-300_merged/evaluate_result/result_score.pkl"
# result_list['Tune_Qwen2.5-1.5B-Instruct'] = "/mnt/SSD1/zenghang/QueryRewriting/output/Chinese/Qwen/Qwen2.5-1.5B-Instruct/checkpoint-2400_merged/evaluate_result/result_score.pkl"
# result_list['Tune_Qwen2.5-3B-Instruct']   = "/mnt/SSD1/zenghang/QueryRewriting/output/Chinese/Qwen/Qwen2.5-3B-Instruct/checkpoint-1200_merged/evaluate_result/result_score.pkl"
# result_list['Tune_Qwen2.5-7B-Instruct']   = "/mnt/SSD1/zenghang/QueryRewriting/output/Chinese/Qwen/Qwen2.5-7B-Instruct/checkpoint-1200_merged/evaluate_result/result_score.pkl"

## English - information
result_list['Zero_Llama-3.2-1B-Instruct'] = "/mnt/SSD1/zenghang/QueryRewriting/output/shareGPT/Llama_zero-shot/Llama-3.2-1B-Instruct/result_score.pkl"
result_list['Zero_Llama-3.2-3B-Instruct'] = "/mnt/SSD1/zenghang/QueryRewriting/output/shareGPT/Llama_zero-shot/Llama-3.2-3B-Instruct/result_score.pkl"
result_list['Zero_Llama-3.1-8B-Instruct'] = "/mnt/SSD1/zenghang/QueryRewriting/output/shareGPT/Llama_zero-shot/Llama-3.1-8B-Instruct/result_score.pkl"
result_list['Zero_Qwen2.5-1.5B-Instruct'] = "/mnt/SSD1/zenghang/QueryRewriting/output/shareGPT/Qwen_zero-shot/Qwen2.5-1.5B-Instruct/result_score.pkl"
result_list['Zero_Qwen2.5-3B-Instruct']   = "/mnt/SSD1/zenghang/QueryRewriting/output/shareGPT/Qwen_zero-shot/Qwen2.5-3B-Instruct/result_score.pkl"
result_list['Zero_Qwen2.5-7B-Instruct']   = "/mnt/SSD1/zenghang/QueryRewriting/output/shareGPT/Qwen_zero-shot/Qwen2.5-7B-Instruct/result_score.pkl"
result_list['Tune_Llama-3.2-1B-Instruct'] = "/mnt/SSD1/zenghang/QueryRewriting/output/shareGPT/meta-llama/Llama-3.2-1B-Instruct/checkpoint-700_merged/evaluate_result/result_score.pkl"
result_list['Tune_Llama-3.2-3B-Instruct'] = "/mnt/SSD1/zenghang/QueryRewriting/output/shareGPT/meta-llama/Llama-3.2-3B-Instruct/checkpoint-500_merged/evaluate_result/result_score.pkl"
result_list['Tune_Qwen2.5-1.5B-Instruct'] = "/mnt/SSD1/zenghang/QueryRewriting/output/shareGPT/Qwen/Qwen2.5-1.5B-Instruct/checkpoint-600_merged/evaluate_result/result_score.pkl"
result_list['Tune_Qwen2.5-3B-Instruct']   = "/mnt/SSD1/zenghang/QueryRewriting/output/shareGPT/Qwen/Qwen2.5-3B-Instruct/checkpoint-650_merged/evaluate_result/result_score.pkl"
result_list['Tune_Qwen2.5-7B-Instruct']   = "/mnt/SSD1/zenghang/QueryRewriting/output/shareGPT/Qwen/Qwen2.5-7B-Instruct/checkpoint-800_merged/evaluate_result/result_score.pkl"



def get_ttest(compared, baseline, alpha=0.05):
    ttest_score = stats.ttest_ind(compared, baseline, axis=0, nan_policy='propagate')[1] / 2
    return ttest_score < alpha

for result_name in result_list:
    baseline_name = result_name
    baseline_path = result_list[baseline_name]
    if not os.path.exists(baseline_path): continue
    compared_name = "Tune_" + result_name.split("_", 1)[1]
    if compared_name not in result_list: continue
    compared_path = result_list[compared_name]
    if not os.path.exists(compared_path): continue

    with open(baseline_path, "rb") as f:
        baseline_score_list = pickle.load(f)
    with open(compared_path, "rb") as f:
        compared_score_list = pickle.load(f)
    baseline_score_list['ttest_recall_P'] = get_ttest(compared_score_list['recall_P'], baseline_score_list['recall_P'])
    baseline_score_list['ttest_precision_P'] = get_ttest(compared_score_list['precision_P'], baseline_score_list['precision_P'])
    baseline_score_list['ttest_recall_I'] = get_ttest(compared_score_list['recall_I'], baseline_score_list['recall_I'])
    baseline_score_list['ttest_precision_I'] = get_ttest(compared_score_list['precision_I'], baseline_score_list['precision_I'])
    print(baseline_path)
    with open(baseline_path, "wb") as f:
        pickle.dump(baseline_score_list, f)

