DETECT_SYS_TEMPLATE_EN = ''''''
DETECT_MSG_TEMPLATE_EN = '''Extract informative phrases from the query that reveal the privacy information of the user, or user related people or things.
The privacy information includes any opinions, concerns, preferences, activities, intentions, or any other information that could
be considered private or sensitive based on the context of the query.
The phrase should be relevant to the user or the user’s related people or things based on the context of the query.
Then for each extracted phrase, summarize the specific privacy information the phrase has leaked.
You should think step-by-step.
Finally, output your answer in JSON. If there is no phrase extracted, the output JSON list should be empty.
Here is the format:
```json
[
    {
        "phrase": PHRASE_1,
        "privacy information": PRIVACY_INFORMATION_1
    }
]
```

The user's QUERY is 
"<|QUERY|>"
'''

DETECT_SYS_TEMPLATE_ZH = ''''''
DETECT_MSG_TEMPLATE_ZH = '''提取用户请求中，揭示了用户、用户相关人员或事物的隐私敏感信息的短语。
隐私敏感信息包括用户的观点、偏好、活动、意图或根据请求上下文可能被认为是私人或敏感的信息。
提取的短语应当在请求的上下文中体现出与用户或用户相关的人员或事物的相关性。
然后，对于每个提取的短语，总结该短语泄露的具体隐私信息。
请一步一步思考（Think step-by-step）。
给出理由并在最后，以JSON格式输出答案。如果没有提取到任何短语，则输出的JSON列表应为空。
以下是格式：  
```json
[
    {
        "phrase": "短语",
        "privacy information": "具体的隐私信息"
    }
]
```

用户的请求是：
"<|QUERY|>"
'''

DETECT_FEW_SHOT_SYS_TEMPLATE_EN = ''''''
DETECT_FEW_SHOT_MSG_TEMPLATE_EN = '''Extract informative phrases from the query that reveal the privacy information of the user, or user related people or things.
The privacy information includes any opinions, concerns, preferences, activities, intentions, or any other information that could
be considered private or sensitive based on the context of the query.
The phrase should be relevant to the user or the user’s related people or things based on the context of the query.
Then for each extracted phrase, summarize the specific privacy information the phrase has leaked.
You should think step-by-step.
Finally, output your answer in JSON. If there is no phrase extracted, the output JSON list should be empty.

Here are some examples:
<|CASE|>End of examples.

The user's current Query is 
"<|QUERY|>"
'''

DETECT_FEW_SHOT_SYS_TEMPLATE_ZH = ''''''
DETECT_FEW_SHOT_MSG_TEMPLATE_ZH = '''提取用户请求中，揭示了用户、用户相关人员或事物的隐私敏感信息的短语。
隐私敏感信息包括用户的观点、偏好、活动、意图或根据请求上下文可能被认为是私人或敏感的信息。
提取的短语应当在请求的上下文中体现出与用户或用户相关的人员或事物的相关性。
然后，对于每个提取的短语，总结该短语泄露的具体隐私信息。
请一步一步思考（Think step-by-step）。
给出理由并在最后，以JSON格式输出答案。如果没有提取到任何短语，则输出的JSON列表应为空。

以下是一些例子：
<|CASE|>例子结束。

用户当前的请求是：
"<|QUERY|>"
'''


DETECT_SYS_PHRASE_ONLY_TEMPLATE_EN = ''''''
DETECT_MSG_PHRASE_ONLY_TEMPLATE_EN = '''Extract informative phrases from the query that reveal the privacy information of the user, or user related people or things.
The privacy information includes any opinions, concerns, preferences, activities, intentions, or any other information that could
be considered private or sensitive based on the context of the query.
The phrase should be relevant to the user or the user’s related people or things based on the context of the query.
The phrase should not be a general term.
You should think step-by-step.
Finally, output your answer in JSON. If there is no phrase extracted, the output JSON list should be empty.
Here is the format:
```json
["phrase1", "phrase2", ...]
```

The user's QUERY is 
"<|QUERY|>"
'''

DETECT_SYS_PHRASE_ONLY_TEMPLATE_ZH = ''''''
DETECT_MSG_PHRASE_ONLY_TEMPLATE_ZH = '''提取用户请求中，揭示了用户、用户相关人员或事物的隐私敏感信息的短语。
隐私敏感信息包括用户的观点、偏好、活动、意图或根据请求上下文可能被认为是私人或敏感的信息。
提取的短语应当在请求的上下文中体现出与用户或用户相关的人员或事物的相关性。
隐私短语应当有具体的指代，而不是一个泛指的词汇。
请一步一步思考（Think step-by-step）。
给出理由并在最后，以JSON格式输出答案。如果没有提取到任何短语，则输出的JSON列表应为空。
以下是格式：  
```json
["短语1", "短语2", ...]
```

用户的请求是：
"<|QUERY|>"
'''

DETECT_FEW_SHOT_SYS_PHRASE_ONLY_TEMPLATE_EN = ''''''
DETECT_FEW_SHOT_MSG_PHRASE_ONLY_TEMPLATE_EN = '''Extract informative phrases from the query that reveal the privacy information of the user, or user related people or things.
The privacy information includes any opinions, concerns, preferences, activities, intentions, or any other information that could
be considered private or sensitive based on the context of the query.
The phrase should be relevant to the user or the user’s related people or things based on the context of the query. 
The phrase should not be a general term.
You should think step-by-step.
Finally, output your answer in JSON. If there is no phrase extracted, the output JSON list should be empty.

Here are some examples:
<|CASE|>End of examples.

The user's current Query is 
"<|QUERY|>"
'''

DETECT_FEW_SHOT_SYS_PHRASE_ONLY_TEMPLATE_ZH = ''''''
DETECT_FEW_SHOT_MSG_PHRASE_ONLY_TEMPLATE_ZH = '''提取用户请求中，揭示了用户、用户相关人员或事物的隐私敏感信息的短语。
隐私敏感信息包括用户的观点、偏好、活动、意图或根据请求上下文可能被认为是私人或敏感的信息。
提取的短语应当在请求的上下文中体现出与用户或用户相关的人员或事物的相关性。
隐私短语应当有具体的指代，而不是一个泛指的词汇。
请一步一步思考（Think step-by-step）。
给出理由并在最后，以JSON格式输出答案。如果没有提取到任何短语，则输出的JSON列表应为空。

以下是一些例子：
<|CASE|>例子结束。

用户当前的请求是：
"<|QUERY|>"
'''

DETECT_SYS_LEAKAGE_ONLY_TEMPLATE_EN = ''''''
DETECT_MSG_LEAKAGE_ONLY_TEMPLATE_EN = '''Determine whether the query leaks the privacy information of the user, or user related people or things.
The privacy information includes any opinions, concerns, preferences, activities, intentions, or any other information that could
be considered private or sensitive based on the context of the query.
Finally, output your answer in JSON. 
Here is the format:
```json
{
    "judgment": true or false
}
```

The user's QUERY is 
"<|QUERY|>"
'''

DETECT_SYS_LEAKAGE_ONLY_TEMPLATE_ZH = ''''''
DETECT_MSG_LEAKAGE_ONLY_TEMPLATE_ZH = '''判断用户请求是否泄露了用户、用户相关人员或事物的隐私敏感信息。
隐私敏感信息包括用户的观点、偏好、活动、意图或根据请求上下文可能被认为是私人或敏感的信息。
请一步一步思考（Think step-by-step）。
给出理由并在最后，以JSON格式输出答案。
以下是格式：  
```json
{
    "judgment": true or false
}
```

用户的请求是：
"<|QUERY|>"
'''

DETECT_FEW_SHOT_SYS_LEAKAGE_ONLY_TEMPLATE_EN = ''''''
DETECT_FEW_SHOT_MSG_LEAKAGE_ONLY_TEMPLATE_EN = '''Determine whether the query leaks the privacy information of the user, or user related people or things.
The privacy information includes any opinions, concerns, preferences, activities, intentions, or any other information that could
be considered private or sensitive based on the context of the query.
Finally, output your answer in JSON. 

Here are some examples:
<|CASE|>End of examples.

The user's current Query is 
"<|QUERY|>"
'''

DETECT_FEW_SHOT_SYS_LEAKAGE_ONLY_TEMPLATE_ZH = ''''''
DETECT_FEW_SHOT_MSG_LEAKAGE_ONLY_TEMPLATE_ZH = '''判断用户请求是否泄露了用户、用户相关人员或事物的隐私敏感信息。
隐私敏感信息包括用户的观点、偏好、活动、意图或根据请求上下文可能被认为是私人或敏感的信息。
请一步一步思考（Think step-by-step）。
给出理由并在最后，以JSON格式输出答案。

以下是一些例子：
<|CASE|>例子结束。

用户当前的请求是：
"<|QUERY|>"
'''


DETECT_TRAIN_SYS_LEAKAGE_ONLY_TEMPLATE_EN = '''Judge whether the query that reveal any privacy-sensitive information of the user, or user related people or things.
'''
DETECT_TRAIN_SYS_PHRASE_ONLY_TEMPLATE_EN = '''Extract informative phrases from the query that reveal the privacy-sensitive information of the user, or user related people or things.
'''
DETECT_TRAIN_SYS_TEMPLATE_EN = '''Extract informative phrases from the query that reveal the privacy-sensitive information of the user, or user related people or things.
Then for each extracted phrase, summarize the specific privacy information the phrase has leaked. 
'''
DETECT_TRAIN_MSG_TEMPLATE_EN = '''Query: "<|QUERY|>"'''

DETECT_TRAIN_SYS_LEAKAGE_ONLY_TEMPLATE_ZH = '''判断Query是否泄漏了用户、用户相关人员或事物的隐私敏感信息。
'''
DETECT_TRAIN_SYS_PHRASE_ONLY_TEMPLATE_ZH = '''从Query中提取出能够揭示用户、用户相关人员或事物的隐私敏感信息的短语。
'''
DETECT_TRAIN_SYS_TEMPLATE_ZH = '''从Query中提取出能够揭示用户、用户相关人员或事物的隐私敏感信息的短语。
然后，针对每个提取的短语，总结该短语泄露的具体隐私信息。 
'''
DETECT_TRAIN_MSG_TEMPLATE_ZH = '''Query: "<|QUERY|>"'''

