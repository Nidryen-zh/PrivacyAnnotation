## Raw data links

> All dialogue data used in this study are publicly available and you can find them in links below. 

| Corpus | Source Link |
| --- | --- |
| ShareGPT (shareGPT, 2023) | https://huggingface.co/datasets/shareAI/ShareGPT-Chinese-English-90k | 
| CrossWOZ (Zhu et al., CL 2020) |  https://github.com/thu-coai/CrossWOZ |
| DuConv (Wu et al., CoRR 2019)  | https://aistudio.baidu.com/aistudio/datasetdetail/177164 |
| LCCC-base (Wang et al., NLPCC 2020) | https://github.com/thu-coai/CDial-GPT |

## To Preprocess Raw Data - Annotate your own data

Please process your custom dialog data into a shareGPT-like format, for example:
```json
{
    "id": "id_xxx",
    "conversation": [
        {
            "user": "xxx",
            "assistant": "xxx"
        },
        {
            "user": "xxx",
            "assistant": "xxx"
        },
    ]
}
```

We also provide a `preprocess.py` script to preprocess examples from ShareGPT and CrossWOZ. Please run this script to generate the preprocessed data required for further annotation.
```bash
# preproceess shareGPT source data
python preprocess_sharegpt.py --file_path shareGPT/common_en_70k_example.jsonl --file_path_output ../preprocess_data/shareGPT/common_en_70k_example.json
```
```bash
# preprocess crosswoz source data
python preprocess_crosswoz.py --file_path CrossWOZ/train_example.json --file_path_output ../preprocess_data/CrossWOZ/train_example.json
```
The preprocessed data can then be used for privacy annotation.