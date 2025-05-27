## How to run

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