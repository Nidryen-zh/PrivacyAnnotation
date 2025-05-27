> You can put our dataset into the `privacy_data` folder

## How to run
To get the annotated data from dialogue datasets, you can simply run our code. The only thing to note is to modify the path to your raw data, i.e., the data input parameter.

1. Preprocess the raw data, please refer to `preprocess.py`. 
2. Privacy Leakage Classification
```bash
python detect_privacy_leakage_GPT.py -f <raw data path> -o <output data path> -l <dataset language>
```
3. Privacy Category Extraction & Privacy Phrase Extraction
```bash
python detect_privacy_phrase_GPT.py -f <raw data path> -o <output data path> -l <dataset language> -d <dataset name>
```
4. Privacy Information Annotation
```bash
python detect_privacy_information_GPT.py -l <dataset language> -d <dataset name>
```


