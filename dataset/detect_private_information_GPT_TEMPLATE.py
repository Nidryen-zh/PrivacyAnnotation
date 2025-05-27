DETECT_PRIVATE_INFO_TEMPLATE = '''Please determine whether the user's Query has leaked the user's private information. If private information is leaked, extract the leaked private information as much as possible and express it in one or several short sentences, and return a list with elements being the short sentences. If no private information is leaked, return an empty list.
The short sentences should briefly describe what private information of the user has been leaked.

Here is an example:
Input:
Query: "I am preparing to go home, back to London."
Output:
["The user's home is in London.", "The user is preparing to go home.", "The user is preparing to go to London."]

Now please determine:
Input:
Query: "<|INPUT_TEXT|>"
Output:

'''

DETECT_PRIVATE_PHRASE_AND_INFO_TEMPLATE = '''Please determine whether the user's Query has leaked the user's private information. If private information is leaked, extract the leaked entities from the user's Query as much as possible and express specifically what privacy has been leaked in one or several short sentences. Return a dictionary containing two keys: "private_entities", which is a list of entities that have leaked privacy, and "private_sentences", which is a list of short sentences. If no private information is leaked, the values in the returned dictionary should be empty lists.
The private entities should be extracted from the user's Query, and the short sentences should briefly describe what private information of the user has been leaked.
Here is an example:
Input:
Query: "I am preparing to go home, back to London."
Output:
{
    "private_entities": ["home", "London"],
    "private_sentences": ["The user's home is in London.", "The user is preparing to go home.", "The user is preparing to go to London."]
}
s
Now please determine:
Input:
Query: "<|INPUT_TEXT|>"
Output:

'''

DETECT_PRIVATE_INFO_WITH_PHRASE_TEMPLATE_EN = '''A user poses a query 
"<|QUERY|>"
to you with a real unique identifier. 

Given a phrase extracted from the query as follows:
Phrase: "<|PHRASE|>"
The phrase reveals new privacy-sensitive information of the user, or user related people or things to you.

think step by step. 
Summarize the specific privacy information the phrase has leaked. 

Then, output a json as follows:
{
    "phrase": PHRASE,
    "privacy information": PRIVACY_INFORMATION
}

Here are some examples:
User's Query: "I am preparing to go back home to No. 800, Dongchuan Road, Minhang District, Shanghai."
Phrase: "No. 800, Dongchuan Road, Minhang District, Shanghai"
JSON Output:
```json
{
    "phrase": "No. 800, Dongchuan Road, Minhang District, Shanghai",
    "privacy information": "The user's home address is No. 800, Dongchuan Road, Minhang District, Shanghai."
}
```

User's Query: "I need to go school."
Phrases: "school"
JSON Output:
```json
{
    "phrase": "school",
    "privacy information": "The user need to go to school."
}
```

'''

DETECT_PRIVATE_INFO_WITH_PHRASE_TEMPLATE_ZH = '''用户向你提出一个请求（Query）

"<|QUERY|>"

并给定用户的真实的身份标识。

给定从请求中提取出短语如下：
短语：" <|PHRASE|> "
该短语向你揭示了用户或与用户相关的人或事物的，新的隐私敏感信息。

一步一步地思考（Think Step by Step。
并总结短语泄露的具体隐私敏感信息。

然后，输出如下格式的JSON：
```json
{
    "phrase": 短语,
    "privacy information": 隐私信息
}
```

以下是一些示例：
用户的请求（Query）："我正在准备回家，地址是上海市闵行区东川路800号。"
短语："上海市闵行区东川路800号"
JSON输出：
```json
{
    "phrase": "上海市闵行区东川路800号",
    "privacy information": "用户的家庭地址是上海市闵行区东川路800号。"
}
```

用户的请求（Query）："我要去学校。"
短语："学校"
JSON输出：
```json
{
    "phrase": "学校",
    "privacy information": "用户需要去学校。"
}
```
'''

COMPARE_TWO_PRIVACY_INFO = '''Given two privacy information sentences of the user ANL, please determine whether these two privacy information sentences express the same meaning. 

"privacy information sentence 1": <|PRIVACY_INFO_1|>, 
"privacy information sentence 2": <|PRIVACY_INFO_2|>

Think step by step and output a json finally.

[Rule 1] If one of the privacy information sentence indicates that no user privacy information has been disclosed, the answer should be None. 
[Rule 2] If two privacy information sentences express the same meaning, the answer should be true; otherwise, the answer should be false. 
[Rule 3] If one of the privacy information sentence is empty, the answer should be None. 

The result output should be in json format with the following format:
{
    "answer": The answer should be true, false or none.
    "reason": short reason of your answer. 
}

'''











