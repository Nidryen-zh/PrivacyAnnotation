DATASET_PRIVACY_FILTER_TEMPLATE_EN = '''A user poses a queryjudgment

"<|QUERY|>"

to you. 

Before the user poses the query, you only know the real unique identifier of the user, and do not know any other privacy-sensitive information of the user. 
After receiving the query with the user's real unique identifier, think step by step to judge whether the query reveals any new privacy-sensitive information of the user or the user's related people or things to you. 

The privacy-sensitive information should be relevant to the user or the user's related people or things based on the context of the query.
The privacy-sensitive information includes any opinions, concerns, preferences, activities, intentions, or any other information that could be considered private or sensitive based on the context of the query.

Give your think steps. Your reasoning must depend on the direct evidences contained in the query and cannot be based on assumption.

Then, output a json as follows:
```json
{
    "reason": reason for your judgment,
    "judgment": true or false
}
```

Here are some examples:
User's query: We want to play football today.
JSON Output:
```json
{
    "reason": "This query exposes the activity of the user and people related to the user intend to do.",
    "judgment": true
}
```

User's query: Tell me some of Hamlet's works.
JSON Output:
```json
{
    "reason": "This query may contain the user's interest, but there is no direct evidence that the user is interested in Hamlet.",
    "judgment": false
}
```

User's query: Write me a story about Jane.  
JSON Output:
```json
{
    "reason": "There is no direct evidence that Jane is related to the user.",
    "judgment": false
}
```

User's query: I love football over basketball. I am worried about the development of football in China.
JSON Output:
```json
{
    "reason": "This query exposes the preference, concern and opinion of the user.",
    "judgment": true
}
```

'''

DATASET_PRIVACY_FILTER_TEMPLATE_ZH = '''用户向你提出一个请求（Query）

"<|QUERY|>"

在用户提出请求之前，你只知道用户的真实的唯一标识符，并且不知道用户的任何其他的隐私敏感信息。
在收到带有用户真实的唯一标识符的请求后，请你进行逐步的思考（Think Step By Step）来判断该请求是否向你透露了任何新的关于用户或与用户相关的人或事的隐私敏感信息。

隐私敏感信息应与用户或与用户相关的人或事相关，该相关性体现在用户请求的上下文中。
隐私敏感信息包括任何观点、担忧、偏好、活动、意图或任何其他根据查询上下文可被视为私密或敏感的信息。

给出你的思考与分析步骤。你的推理必须依赖于查询中包含的直接证据，不能基于假设。

最后，输出如下格式的json：
```json
{
    "reason": 你判断的理由,
    "judgment": true 或 false
}
```

以下是一些示例：
用户的请求（Query）：我们今天想踢足球。
JSON输出：
```json
{
    "reason": "该请求透露了用户及与用户相关的人打算进行的活动。",
    "judgment": true
}
```

用户的请求（Query）：告诉我一些哈姆雷特的作品。
JSON输出：
```json
{
    "reason": "该请求可能包含用户的兴趣，但没有直接证据表明用户对哈姆雷特感兴趣。",
    "judgment": false
}
```

用户的请求（Query）：为我写一个关于简的故事。
JSON输出：
```json
{
    "reason": "请求中没有直接证据表明简与用户有关。",
    "judgment": false
}
```

用户的请求（Query）：我喜欢足球胜过篮球。我担心中国足球的发展。
JSON输出：
```json
{
    "reason": "该请求透露了用户的偏好、担忧和意见。",
    "judgment": true
}
```

'''
