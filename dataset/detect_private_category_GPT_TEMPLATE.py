# baselines - direct extract
DETECT_PRIVATE_CATEGORY_TEMPLATE_EN_BASELINE = '''Given a user's query 

"<|QUERY|>"

identify which phrases in the query leak the user's privacy information.
Let's think step by step and output a json finally.
The result output should be in json format with the following format:
```json
[phrase 1, phrase 2, ...]
```

Here is an example
"Query": "I'm a teacher in China, majoring in computer science. I will go back home to London."
Output:
```json
["teacher", "computer science", "China", "London"]
```
'''

# STEP 2 - extract categories
DETECT_PRIVATE_CATEGORY_TEMPLATE_EN = '''Given a user's query 

"<|QUERY|>"

identify which phrases in the query leak the user's privacy information and the correponding categories of privacy information.
Let's think step by step and output a json finally.
The result output should be in json format with the following format:
```json
{
    privacy information category 1: [phrase 1, phrase 3, ...], 
    privacy information category 2: [phrase 2, phrase 4, ...]
}
```

Here is an example
"Query": "I'm a teacher in China, majoring in computer science. I will go back home to London."
Output:
```json
{
    "Job": ["teacher"],
    "Subject": ["computer science"],
    "Location": ["China", "London"]
 }
 ```
'''

DETECT_PRIVATE_CATEGORY_TEMPLATE_ZH = '''用户向你提出一个请求（Query）

"<|QUERY|>"

提取请求中泄露用户隐私信息的短语，并将其分类为相应的隐私信息类别。
让我们一步一步地思考，最后输出一个json，格式如下：
```json
{
    "隐私信息类别1": ["短语1", "短语3", ...],
    "隐私信息类别2": ["短语2", "短语4", ...]
}
```

以下是一个示例：
用户的请求（Query）："我是中国的一名教师，主修计算机科学。我将回家到伦敦。"
JSON输出：
```json
{
    "职业": ["教师"],
    "专业": ["计算机科学"],
    "地点": ["中国", "伦敦"]
}
```
'''

# STEP 2-1 - categories deduplication
MERGE_PRIVATE_CATEGORY_BYBLOCK_TEMPLATE_EN = '''Given the following <BLOCK_SIZE> privacy categories and the list of example phrases belong to each privacy category:

<|CATEGORY_INPUT|>

if privacy category A and privacy category B have the same meaning, just keep category A.
Let's think step by step and output a json list finally. 
Output the new privacy categories after deduplication in the format of a list in json, for example:
[privacy category 1, privacy category 2, ... ]
'''

MERGE_PRIVATE_CATEGORY_BYBLOCK_TEMPLATE_ZH = '''给定以下<BLOCK_SIZE>个隐私类别（privacy category）及每个隐私类别对应的示例短语（phrase）列表：

<|CATEGORY_INPUT|>

对隐私类别进行去重，如果隐私类别A和隐私类别B具有相同的含义，只保留类别A。
让我们一步一步地思考，最后输出一个json列表。
以列表格式输出去重后的新的隐私类别，例如：
[隐私类别1, 隐私类别2, ... ]
'''

# STEP 2-2 - whole categories deduplication
MERGE_PRIVATE_CATEGORY_BYBLOCK_TOTAL_TEMPLATE_EN = '''Given the following privacy categories:

<|ALL_CATEGORY|>

if privacy category A and privacy category B have the same meaning, just keep category A.
Let's think step by step and output a json list finally. 
Output the new privacy categories after deduplication in the format of a list in json, for example:
[privacy category 1, privacy category 2, ... ]
'''

MERGE_PRIVATE_CATEGORY_BYBLOCK_TOTAL_TEMPLATE_ZH = '''给定以下隐私类别（privacy category）：

<|ALL_CATEGORY|>

对隐私类别进行去重，如果隐私类别A和隐私类别B具有相同的含义，只保留类别A。
让我们一步一步地思考，最后输出一个json列表。
以列表格式输出去重后的新的隐私类别，例如：
[隐私类别1, 隐私类别2, ... ]
'''
