import numpy as np 
import os
from scipy import stats
import pandas as pd
import pickle

result_list = {}

## Chinese - leakage
# result_list['Zero_Llama-3.2-1B-Instruct'] = "output/Chinese_only_leakage/Llama_zero-shot/Llama-3.2-1B-Instruct/acc_score.pkl"
# result_list['Zero_Llama-3.2-3B-Instruct'] = "output/Chinese_only_leakage/Llama_zero-shot/Llama-3.2-3B-Instruct/acc_score.pkl"
# result_list['Zero_Qwen2.5-1.5B-Instruct'] = "output/Chinese_only_leakage/Qwen_zero-shot/Qwen2.5-1.5B-Instruct/acc_score.pkl"
# result_list['Zero_Qwen2.5-3B-Instruct']   = "output/Chinese_only_leakage/Qwen_zero-shot/Qwen2.5-3B-Instruct/acc_score.pkl"
# result_list['Zero_Qwen2.5-7B-Instruct']   = "output/Chinese_only_leakage/Qwen_zero-shot/Qwen2.5-7B-Instruct/acc_score.pkl"
# result_list['Zero_Qwen2.5-72B-Instruct']   = "output/Chinese_only_leakage/Qwen_zero-shot/Qwen2.5-72B-Instruct/acc_score.pkl"
# result_list['Tune_Llama-3.2-1B-Instruct'] = "output/Chinese_only_leakage/meta-llama/Llama-3.2-1B-Instruct/checkpoint-1750_merged/evaluate_result/acc_score.pkl"
# result_list['Tune_Llama-3.2-3B-Instruct'] = "output/Chinese_only_leakage/meta-llama/Llama-3.2-3B-Instruct/checkpoint-750_merged/evaluate_result/acc_score.pkl"
# result_list['Tune_Qwen2.5-1.5B-Instruct'] = "output/Chinese_only_leakage/Qwen/Qwen2.5-1.5B-Instruct/checkpoint-150_merged/evaluate_result/acc_score.pkl"
# result_list['Tune_Qwen2.5-3B-Instruct']   = "output/Chinese_only_leakage/Qwen/Qwen2.5-3B-Instruct/checkpoint-200_merged/evaluate_result/acc_score.pkl"
# result_list['Tune_Qwen2.5-7B-Instruct']   = "output/Chinese_only_leakage/Qwen/Qwen2.5-7B-Instruct/checkpoint-150_merged/evaluate_result/acc_score.pkl"

## English - leakage
result_list['Zero_Llama-3.2-1B-Instruct'] = "output/shareGPT_only_leakage/Llama_zero-shot/Llama-3.2-1B-Instruct/acc_score.pkl"
result_list['Zero_Llama-3.2-3B-Instruct'] = "output/shareGPT_only_leakage/Llama_zero-shot/Llama-3.2-3B-Instruct/acc_score.pkl"
result_list['Zero_Qwen2.5-1.5B-Instruct'] = "output/shareGPT_only_leakage/Qwen_zero-shot/Qwen2.5-1.5B-Instruct/acc_score.pkl"
result_list['Zero_Qwen2.5-3B-Instruct']   = "output/shareGPT_only_leakage/Qwen_zero-shot/Qwen2.5-3B-Instruct/acc_score.pkl"
result_list['Zero_Qwen2.5-7B-Instruct']   = "output/shareGPT_only_leakage/Qwen_zero-shot/Qwen2.5-7B-Instruct/acc_score.pkl"
result_list['Zero_Qwen2.5-72B-Instruct']  = "output/shareGPT_only_leakage/Qwen_zero-shot/Qwen2.5-72B-Instruct/acc_score.pkl"
result_list['Tune_Llama-3.2-1B-Instruct'] = "output/shareGPT_only_leakage/meta-llama/Llama-3.2-1B-Instruct/checkpoint-100_merged/evaluate_result/acc_score.pkl"
result_list['Tune_Llama-3.2-3B-Instruct'] = "output/shareGPT_only_leakage/meta-llama/Llama-3.2-3B-Instruct/checkpoint-100_merged/acc_score.pkl"
result_list['Tune_Qwen2.5-1.5B-Instruct'] = "output/shareGPT_only_leakage/Qwen/Qwen2.5-1.5B-Instruct/checkpoint-250_merged/evaluate_result/acc_score.pkl"
result_list['Tune_Qwen2.5-3B-Instruct']   = "output/shareGPT_only_leakage/Qwen/Qwen2.5-3B-Instruct/checkpoint-500_merged/evaluate_result/acc_score.pkl"
result_list['Tune_Qwen2.5-7B-Instruct']   = "output/shareGPT_only_leakage/Qwen/Qwen2.5-7B-Instruct/checkpoint-300_merged/evaluate_result/acc_score.pkl"

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
    baseline_score_list['ttest_acc'] = get_ttest(compared_score_list['acc'], baseline_score_list['acc'])
    print(baseline_path)
    print(baseline_score_list['ttest_acc'])
    with open(baseline_path, "wb") as f:
        pickle.dump(baseline_score_list, f)

