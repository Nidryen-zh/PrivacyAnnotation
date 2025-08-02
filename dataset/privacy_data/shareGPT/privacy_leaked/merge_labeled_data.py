'''
Merge the labeled data
'''
import json 

window_size = 10
data = []
for start_idx in range(0, 10, window_size):
    data_path = f"common_en_70k_example_{start_idx}_{start_idx+window_size}.json"
    data += json.load(open(data_path))

json.dump(data, open("common_en_70k_example.json", "w"), ensure_ascii=False, indent=4)