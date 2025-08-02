# Automated Privacy Annotation Pipeline

> You can put our dataset into the `privacy_data` folder

## Step 0: set your environment
Export your OpenAI API key to the environment:
```bash
export OPENAI_API_KEY=<your own key>
```

Set your python environment:
```bash
pip install openai 
```

## Step 1: Privacy Leakage or Not Classification  
The first step is to label the preprocessed data based on whether it contains any privacy information.
Since raw datasets are often large, it is recommended to divide them into smaller segments using the predefined parameters start_idx and end_idx.

Here is an example to run the privacy leakage classification script:
```bash
python detect_private_leakage_GPT.py --file_path preprocess_data/shareGPT/common_en_70k_example.json --file_path_output privacy_data/shareGPT/privacy_leaked/common_en_70k_example.json --start_idx 0 --end_idx 10
```
The whole parameter set of this script:  
- file_path: the path of the preprocessed data
- file_path_output: the output path of labeled data
- language: the language of the dataset, support English ("en") and Chinese ("zh")
- start_idx: the starting index of the raw dataset list for current processing
- end_idx: the ending index of the raw dataset list for current processing

We also provide a simple script for merge different segments:
```bash
cd privacy_data/shareGPT/privacy_leaked
python merge_labeled_data.py
```

## Step 2: Extensive Privacy Categories Extraction
The second step is to extract extensive privacy categories set for the dataset. 
If you divided the data into small segments in the first step, simply concatenate them together. Then you can extract privacy categories for them. 

Here is an example to run the privacy categories extraction script:
```bash
python detect_private_category_GPT.py --file_path privacy_data/shareGPT/privacy_leaked/common_en_70k_example.json --file_output_dir privacy_data/shareGPT/privacy_category
```
The whole parameter set of this script:
- file_path: the path to the data labeled with privacy leakage
- file_output_dir: the output directory for the extracted categories, the final results will be saved at file_output_dir/private_categories_merged.json.
- language: the language of the dataset, support English ("en") and Chinese ("zh")


## Step 3: Privacy Phrase Extraction
The third step is to extract privacy phrase for the dataset. We also recommend processing the divided smaller segments. 
This step takes the results from both Step 1 and Step 2 as input and outputs the extracted privacy phrase for each sample.

Here is an example to run the privacy phrase extraction script:
```bash
python detect_private_phrase_GPT.py --file_path privacy_data/shareGPT/privacy_leaked/common_en_70k_example_0_10.json --file_category_path privacy_data/shareGPT/privacy_category/private_categories_merged.json --file_output_dir privacy_data/shareGPT/privacy_phrase/data_split_0_10 --language en
``` 
The whole parameter set of this script:
- file_path: the path to the data labeled with privacy leakage
- file_category_path: the path to the extensive categories set extracted by step 2 
- file_output_dir: the output directory for the extracted privacy phrases, the final results will be saved at file_output_dir/finegrained_merge_phrase_final.json.
- language: the language of the dataset, support English ("en") and Chinese ("zh")


## Step 4: Privacy Information Annotation
The fourth step is to annotate privacy information for each phrase. This step takes the results from Step 3 as input and otuputs the annotated privacy information for each extracted phrase.

Here is an example to run the privacy inforamtion annotation script:
```bash
python detect_private_information_GPT.py --file_path privacy_data/shareGPT/privacy_phrase/data_split_0_10/finegrained_merge_phrase_final.json --file_path_output privacy_data/shareGPT/privacy_information/data_split_0_10/privacy_information.json --language en
```
The whole parameter set of this script:  
- file_path: the path of the data with extracted privacy phrases
- file_path_output: the output path of the annotation results
- language: the language of the dataset, support English ("en") and Chinese ("zh")
