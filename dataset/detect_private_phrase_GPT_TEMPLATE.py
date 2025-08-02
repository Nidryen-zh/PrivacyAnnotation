# baselines - direct extract
DETECT_PRIVATE_PHRASE_TEMPLATE_EN_BASELINE = '''Given a user's query 

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

# STEP 3-1 - privacy phrase extraction
DETECT_PRIVATE_PHRASE_WITH_CATEGORY_TEMPLATE_EN = '''A user poses a query
"<|QUERY|>" 
to you. 

Extract informative phrases from the query that definitely reveal the privacy-sensitive information of the user, or user related people or things. 
The phrases must be included exactly as they appear in the query's content. Do not alter the format or wording of the phrases. For example, spelling errors, number of spaces, capitalization, etc., must all be preserved exactly same as the query's content.

Give your think steps. The reasoning must depend on the direct evidences contained in the query and cannot be based on assumption.

Then, match each extracted phase with the most appropriate privacy category in the following pre-defined list, and also note if the extracted phrase is not matched with any given privacy category, it should be excluded.

Privacy Categories: <|CATEGORIES|>

The result output should be in json format with the following format:
{
    "phrase 1" : "privacy category 3",
    "phrase 2" : "privacy category 4"
}

Here are some examples
User's Query: "I'm a teacher in China, majoring in computer science. I will go back home to London."
Privacy Categories: ["Name", "Age", "Gender", "Job", "Subject", "Location"]
JSON Output:
```json
{
    "teacher": "Job",
    "computer science": "Subject",
    "China": "Location",
    "London": "Location"
}
```

User's Query: "We are happy today and plan to play football."
Privacy Categories: ["Emotion", "Location", "Intention"]
JSON Output:
```json
{
    "happy": "Emotion",
    "plan to play football": "Intention"
}
```

User's Query: "How to go from Shanghai to London?"
Privacy Categories: ["Name", "Age", "Gender", "Job", "Location"]
JSON Output:
```json
{
}
```

User's Query: "Tell me some of Hamlet's works."
Privacy Categories: ["Name", "Age", "Gender", "Job", "Art", "Activity"]
JSON Output:
```json
{
}
```

'''

DETECT_PRIVATE_PHRASE_WITH_CATEGORY_TEMPLATE_ZH = '''用户向你提出一个请求（Query）
"<|QUERY|>"

从请求的内容中提取短语，该短语明确揭示用户的，或与用户相关的人或事物的隐私敏感信息。
短语必须与请求内容中出现的完全一致。不要更改短语的格式或措辞，即拼写错误、空格数量、大小写等，都必须与请求内容完全相同。

给出你的思考步骤（Think Step by Step）。推理必须依赖于请求中包含的直接证据，不能基于假设。
然后，将每个提取的短语与以下预定义列表中最合适的隐私类别匹配，并且如果提取的短语未与任何给定的隐私类别匹配，则应将其排除。

隐私类别：<|CATEGORIES|>

结果输出应为json格式，格式如下：
{
    "短语1" : "隐私类别3",
    "短语2" : "隐私类别4"
}

以下是一些示例
用户的请求（Query）："我是中国的一名教师，主修计算机科学。我将回家到伦敦。"
隐私类别：["姓名", "年龄", "性别", "职业", "专业", "地点"]
JSON输出：
```json
{
    "教师": "职业",
    "计算机科学": "专业",
    "中国": "地点",
    "伦敦": "地点"
}
```

用户的请求（Query）："我们今天很开心，计划去踢足球。"
隐私类别：["情感", "地点", "意图"]
JSON输出：
```json
{
    "开心": "情感",
    "计划去踢足球": "意图"
}
```

用户的请求（Query）："如何从上海到伦敦？"
隐私类别：["姓名", "年龄", "性别", "职业", "地点"]
JSON输出：
```json
{
}
```

用户的请求（Query）："告诉我一些哈姆雷特的作品。"
隐私类别：["姓名", "年龄", "性别", "职业", "艺术", "活动"]
JSON输出：
```json
{
}
```

'''

# STEP 3-2 - privacy phrase deduplication
MERGE_PRIVATE_PHRASE_TEMPLATE_EN = '''Given a user's query and privacy phrases extracted from the query, 

Query: "<|QUERY|>"
Privacy Phrases: <|ENTITIES|>

Think step by step to deduplicate the privacy phrases by strictly following the given rules:

[Rule 1] If privacy phrase A and privacy phrase B have the same meaning, keep phrase which is more concise and clear. 
[Rule 2] If privacy phrase A is part of privacy phrase B, keep phrase which has more information and is clear. 

Give your think steps. Then output the new privacy phrases after deduplication in the format of a list in json, for example:
```json
[new privacy phrase 1, new privacy phrase 2, ]
```

Here is a examples:
Query: "We are happy and plan to play football."
Privacy Phrases: ['happy', 'We are happy', 'plan to play football', 'football', 'play football']
JSON output:
```json
["happy", "play football"]
```
'''

MERGE_PRIVATE_PHRASE_TEMPLATE_ZH = '''给定一个用户请求（Query）和从请求中提取的隐私短语（Phrase），

用户请求："<|QUERY|> "
隐私短语：<|ENTITIES|>

一步一步地思考（Think Step by Step），严格按照给定的规则对隐私短语进行去重：

[规则1] 如果隐私短语A和隐私短语B具有相同的含义，保留更简洁明了的短语。
[规则2] 如果隐私短语A是隐私短语B的一部分，保留信息量更大且清晰的短语。

给出你的思考步骤。然后以json列表格式输出去重后的新隐私短语，例如：
```json
[新隐私短语1, 新隐私短语2, ]
```

以下是一个示例：
用户的请求（Query）："我们很开心，计划去踢足球。"
隐私短语：['开心', '我们很开心', '计划去踢足球', '足球', '踢足球']
JSON输出：
```json
["开心", "踢足球"]
```
'''

# STEP 3-3 - filtering privacy phrase with rule 1
CLEAN_PRIVATE_ONE_PHRASE_RULE1_TEMPLATE_EN = '''A user poses a query 

"<|QUERY|>"

to you with a real unique identifier. 

Given a phrase extracted from the query as follows:
Phrase: "<|PHRASE|>"

think step by step to reason about whether the phrase satisfies the following rule:

[Rule] the phrase directly links to the user or user's related people or things in the context of the user's query. 

Give your think steps. The reasoning must depend on the direct evidences contained in the query and cannot be based on assumption.

Then, output a json as follows:
```json
{
    "reason" : reason for your judgement,
    "judgement" : true or false
}
```

Here are some examples:
User's Query: "We plan to play football with Ross."
Phrase: "play football with Ross"
JSON Output:
```json
{
    "reason" : "Playing football is the user's plan that related to the user. Ross is also related to the user.",
    "judgement" : true
}
```

User's Query: "Tom is an English teacher."
Phrases: "English teacher"
JSON Output:
```json
{
    "reason" : "English teacher is the job of Tom, but there no evidence to indicate that Tom relate to the user.",
    "judgement" : false
}
```

User's Query: "Where will the 2026 World Cup be held?"
Phrases: "World Cup"
JSON Output:
```json
{
    "reason" : "Where the 2026 World Cup will be held is an established fact and has nothing to do with users.",
    "judgement" : false
} 
```

'''

CLEAN_PRIVATE_ONE_PHRASE_RULE1_TEMPLATE_ZH = '''用户向你提出一个请求（Query）

"<|QUERY|>"

并给定用户的真实的身份标识。

给定从请求中提取出短语如下：
短语：" <|PHRASE|> "

一步一步地思考（Think Step by Step），判断该短语是否满足以下规则：

[规则] 该短语在用户请求的上下文中直接与用户或与用户相关的人或事物相关联。

给出你的思考步骤。推理必须依赖于请求中包含的直接证据，不能基于假设。

然后，输出如下格式的json：
```json
{
    "reason" : 你判断的理由,
    "judgement" : true 或 false
}
```

以下是一些示例：
用户的请求（Query）："我们计划和罗斯一起踢足球。"
短语："和罗斯一起踢足球"
JSON输出：
```json
{
    "reason" : "踢足球是用户的计划，与用户相关。罗斯也与用户相关。",
    "judgement" : true
}
```

用户的请求（Query）："汤姆是一名英语老师。"
短语："英语老师"
JSON输出：
```json
{
    "reason" : "英语老师是汤姆的职业，但没有证据表明汤姆与用户有关。",
    "judgement" : false
}
```

用户的请求（Query）："2026年世界杯将在何处举行？"
短语："世界杯"
JSON输出：
```json
{
    "reason" : "2026年世界杯的举办地点是一个既定事实，与用户无关。",
    "judgement" : false
}
```

'''

# STEP 3-3 - filtering privacy phrase with rule 2
CLEAN_PRIVATE_ONE_PHRASE_RULE2_TEMPLATE_EN = '''A user poses a query 
"<|QUERY|>"
to you with a real unique identifier. 

Given a phrase extracted from the query as follows:
Phrase: "<|PHRASE|>"

think step by step to reason about whether the phrase satisfies the following rule:

[Rule] the phrase should not be a general phrase that provide NO information related to the user based on the context of the user's query.

Give your think steps. The reasoning must depend on the direct evidences contained in the query and cannot be based on assumption.

Then, output a json as follows:
```json
{
    "reason" : reason for your judgement,
    "judgement" : true or false
}
```

Here are some examples:
User's Query: "I want to go a place."
Phrases: "place"
JSON Output:
```json
{
    "reason" : "The 'place' term has no clear reference.",
    "judgement" : false
}
```

User's Query: "I want to go school."
Phrases: "school"
JSON Output:
```json
{
    "reason" : "The 'school' term exposes where the user want to go.",
    "judgement" : true
}
```

User's Query: "We are happy today."
Phrases: "happy"
JSON Output:
```json
{
    "reason" : "The 'happy' term is a general term, but it exposes the emotion of the user and user's releated people.",
    "judgement" : true
}
```

User's Query: "I know how to configure settings."
Phrases: "settings"
JSON Output:
```json
{
    "reason" : "The 'settings' term has no clear reference.",
    "judgement" : false
}
```

'''

CLEAN_PRIVATE_ONE_PHRASE_RULE2_TEMPLATE_ZH = '''用户向你提出一个请求（Query）

"<|QUERY|>"

并给定用户的真实的身份标识。

给定从请求中提取出短语如下：
短语：" <|PHRASE|> "

一步一步地思考（Think Step by Step），判断该短语是否满足以下规则：

[规则] 该短语不应是一个在用户请求上下文中不提供与用户相关信息的一般短语。

给出你的思考步骤。推理必须依赖于查询中包含的直接证据，不能基于假设。

然后，输出如下格式的json：
```json
{
    "reason" : 你判断的理由,
    "judgement" : true 或 false
}
```

以下是一些示例：
用户的请求（Query）："我想去一个地方。"
短语："地方"
JSON输出：
```json
{
    "reason" : "'地方'一词没有明确的指代。",
    "judgement" : false
}
```

用户的请求（Query）："我想去学校。"
短语："学校"
JSON输出：
```json
{
    "reason" : "'学校'一词揭示了用户想去的地方。",
    "judgement" : true
}
```

用户的请求（Query）："我们今天很开心。"
短语："开心"
JSON输出：
```json
{
    "reason" : "'开心'一词是一个通用术语，但它揭示了用户及其相关人的情感。",
    "judgement" : true
}
```

用户的请求（Query）："我知道如何配置设置。"
短语："设置"
JSON输出：
```json
{
    "reason" : "'设置'一词没有明确的指代。",
    "judgement" : false
}
```

'''