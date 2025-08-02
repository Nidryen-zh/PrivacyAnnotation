'''
Merge extracted privacy phrase 
'''
import json 

window_size = 10
data = []
for start_idx in range(0, 10, window_size):
    data_path = f"data_split_{start_idx}_{start_idx+window_size}/finegrained_merge_phrase_final.json"
    data += json.load(open(data_path))

json.dump(data, open("finegrained_merge_phrase_final.json", "w"), ensure_ascii=False, indent=4)