# Automated Privacy Information Annotation in Large Language Model Interactions

<div align="center">
  <figure>
    <img src="https://huggingface.co/datasets/Nidhogg-zh/Interaction_Dialogue_with_Privacy/resolve/main/asserts/pipeline.png" alt="category_count_en" width="1000"/>
    <figcaption>Overview of our automated pipeline to extract privacy phrase and annotate privacy information over dialogue datasets</figcaption>
  </figure>
</div>

<p align="center">
       🤗 <a href="https://huggingface.co/datasets/Nidhogg-zh/Interaction_Dialogue_with_Privacy">Hugging Face</a> &nbsp&nbsp📑 <a href="https://arxiv.org/abs/2505.20910">Paper</a>&nbsp&nbsp
</p>

This work supports the development and evaluation of privacy detection models for real-name large language model (LLM) interactions, with a particular focus on solutions that are deployable on local user devices. We claim that traditional personally identifiable information (PII) detection in anonymous content is insufficient in real-name interaction scenarios with LLMs. By authenticating through user login, queries posed to LLMs have been linked to a specific user’s real identifier.  The target application scenario of this work is to detect any newly leaked private data related to the user after a query is made, extending beyond PII.

We present an automated annotation pipeline that leverages LLMs to extract privacy-related phrases and annotate privacy information in dialogue datasets. This approach yields a large-scale, multilingual dataset comprising over 249K user queries and 154K annotated privacy phrases with corresponding privacy information.

In addition to the dataset, we propose a set of evaluation metrics that assess privacy risks at three levels: (1) privacy query-level metric for leakage classification task, (2) privacy phrase-level metrics for phrase extraction task, and (3) privacy information-level metrics for information summarization task.

We further implement and benchmark a series of baseline methods using light-weight LLMs, including both tuning-free and tuning-based approaches.

## 📥 Load the Dataset
We provide the data in two formats: one that retains the contextual relationships between the original queries within each dialogue, and another that organizes each query individually.
The dataset is available on <a href="https://huggingface.co/datasets/Nidhogg-zh/Interaction_Dialogue_with_Privacy">Hugging Face</a>. The English and Chinese dataset are divided into different subsets. 

You can load the dataset that retains queries' contextual relationships using the following code:
```python
## English dataset
import datasets 
en_dataset = datasets.load_dataset("Nidhogg-zh/Interaction_Dialogue_with_Privacy", "en")

## Chinese dataset
import datasets 
zh_dataset = datasets.load_dataset("Nidhogg-zh/Interaction_Dialogue_with_Privacy", "zh")
```

Then you will get data in format like the following:
```json
[
    {
        "id": "ShareGPT_pKNQqpRRE1",
        "conversation": [
            {
                "user": "Can you please list the operators know to work for ArcelorMittal in the world and who are not OBS?",
                "assistant": "As an AI language model, I don't have access to up-to-date information about every operator that works with ArcelorMittal. However, based on my knowledge cutoff in September 2021, ...",
                "privacy": []
            },
            {
                "user": "David Glijer is a key target for us. How would you recommand to engage him?",
                "assistant": "When engaging with David Glijer, it's important to understand his role and responsibilities within ArcelorMittal. Based on the information you provided earlier, ...",
                "privacy": [
                    {
                        "phrase": "David Glijer",
                        "privacy information": "David Glijer is identified as a key target of interest, suggesting a strategic focus in a business context."
                    },
                    {
                        "phrase": "key target for us",
                        "privacy information": "David Glijer is an important person of interest or focus for the user's objectives, implying a strategic or professional engagement."
                    },
                    {
                        "phrase": "engage him",
                        "privacy information": "The user has plans to strategically engage or interact with David Glijer, indicating he is a subject of interest."
                    }
                ]
            }
        ]
    },
    ...
]
```

You can also load the dataset where all samples are organized into one list using the following code:
```python
## English dataset
import datasets 
en_dataset = datasets.load_dataset("Nidhogg-zh/Interaction_Dialogue_with_Privacy", "en_query")

## Chinese dataset
import datasets 
zh_dataset = datasets.load_dataset("Nidhogg-zh/Interaction_Dialogue_with_Privacy", "zh_query")
```

Then you will get data in format like the following:
```json
[
    {
        "id": "ShareGPT_pKNQqpRRE1_part1",
        "user": "David Glijer is a key target for us. How would you recommand to engage him?",
        "assistant": "When engaging with David Glijer, it's important to understand his role and responsibilities within ArcelorMittal. Based on the information you provided earlier, ...",
        "privacy": [
            {
                "phrase": "David Glijer",
                "privacy information": "David Glijer is identified as a key target of interest, suggesting a strategic focus in a business context."
            },
            {
                "phrase": "key target for us",
                "privacy information": "David Glijer is an important person of interest or focus for the user's objectives, implying a strategic or professional engagement."
            },
            {
                "phrase": "engage him",
                "privacy information": "The user has plans to strategically engage or interact with David Glijer, indicating he is a subject of interest."
            }
        ]
    },
    ...
]
```

## ✒️ Annotate for Your Own Corpora

### Set the environment
Export your OpenAI API key to the environment:
```bash
export OPENAI_API_KEY=<your own key>
```

Set your python environment:
```bash
conda create -n annotator python=3.9
conda activate annotator

pip install openai 
pip install requests
```

### Preprocess your own corpora
Convert all the source data into the format as below:
```json
{
    "id": "ShareGPT_AzsVtVQ",
    "conversation": [
        {
            "user": "Are you busy?",
            "assistant": "I am a computer program and do not have the ability to be busy. I am always ready to assist you with any questions or information you may need. How can I help you today?"
        },
    ]
}
```
- id: the id for current conversation
- conversation: the content of the dialogue between the user and the assistant. It may contain multiple turns.

### Run scripts
There are four steps to obtain the final annotated results.   

- [detect_private_information_GPT.py](https://github.com/Nidryen-zh/PrivacyAnnotation/blob/master/dataset/detect_private_leakage_GPT.py) provides code for step 1: privacy leakage or not classification
- [detect_private_category_GPT.py](https://github.com/Nidryen-zh/PrivacyAnnotation/blob/master/dataset/detect_private_category_GPT.py) provides code for step 2: extensive privacy categories extraction
- [detect_private_phrase_GPT.py](https://github.com/Nidryen-zh/PrivacyAnnotation/blob/master/dataset/detect_private_phrase_GPT.py) provides code for step 3: privacy phrase extraction
- [detect_private_information_GPT.py](https://github.com/Nidryen-zh/PrivacyAnnotation/blob/master/dataset/detect_private_information_GPT.py) provides code for step 4: privacy information annotation

Please enter the `dataset` folder and run the provided scripts. More details can be found [here](https://github.com/Nidryen-zh/PrivacyAnnotation/blob/master/dataset/Readme.md).

We also provide examples of preprocess data in `dataset/preprocess_data` and examples of annotated results in `dataset/privacy_data`.


## 🛠️ Train & Evaluate Local Privacy Detection Model

### Train
You can simply run the tuning script to get a model with supervised fine-tuning after setting the model name and the training data path.
```bash
bash finetune/finetune_lora_ds.sh
```
In the script, environment variable `MODEL` is the model name used for fine-tuning and `DATA` is the training data path. 
Please change `language` parameter to "en" for English dataset or to "zh" for Chinese dataset. 
Please change `tuning_mode` parameter to _all_, _phrase_only_, or _leakage_only_ for privacy information summarization, privacy phrase extraction, and privacy leakage classification task, respectively.

### Evaluate 
#### Get results of local privacy detection methods
We provide evaluation scripts for local models with vLLM, and cloud-based models with API. You can run following python files to get prediction resutls. 
```bash
# for local model
python evaluate_vllm.py -m <model name> -d <test data path> -o <output path> -t <is fine-tuned> -f <is few shot> -l <language>
```
```bash
# for cloud-based API
python evaluate_api.py -m <model name> -d <test data path> -o <output path> -f <is few shot> -l <language>
```
Please set `phrase_only` to true for phrase extraction task or `leakage_only` to true for leakage classification task 

#### Get evaluation resutls
To merge the prediction resutls from different local ranks (only for multi-gpu prediction), you can run following python file. 
```bash
python output/get_pred_results_information.py -d <test data path> -o <model prediction path> # for information summarization task
python output/get_pred_results_phrase.py -d <test data path> -o <model prediction path>      # for phrase extraction task
python output/get_pred_results_leakage.py -d <test data path> -o <model prediction path>     # for leakage classification task
```

To get evaluation results based on test set, you can run following python files.
```bash
python output/evaluate_information.py -l <test data path> -p <model prediction path> --language <dataset language> # for information summarization task
python output/evaluate_phrase.py -l <test data path> -p <model prediction path> --language <dataset language>      # for phrase extraction task
python output/evaluate_leakage.py -l <test data path> -p <model prediction path> --language <dataset language>     # for leakage classification task
```

## Citation

### Bib