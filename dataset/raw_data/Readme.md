## Raw data links

> All dialogue data used in this study are publicly available and you can find them in links below. 

| Corpus | Source Link |
| --- | --- |
| ShareGPT (shareGPT, 2023) | https://huggingface.co/datasets/shareAI/ShareGPT-Chinese-English-90k | 
| CrossWOZ (Zhu et al., CL 2020) |  https://github.com/thu-coai/CrossWOZ |
| DuConv (Wu et al., CoRR 2019)  | https://aistudio.baidu.com/aistudio/datasetdetail/177164 |
| LCCC-base (Wang et al., NLPCC 2020) | https://github.com/thu-coai/CDial-GPT |

### To Preprocess Raw Data

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