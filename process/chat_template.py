PARAPHRASER = """
Rewrite the question for search while keeping its meaning and key terms intact.
If the conversation history is empty, DO NOT change the query.
Use conversation history only if necessary, and avoid extending the query with your own knowledge.
If no changes are needed, output the current question as is.
Conversation history:
{% for memory in memories %}
    {{ memory }}
{% endfor %}

User Query: {{query}}
Rewritten Query:
"""

PARAPHRASER_JP="""
検索用に質問を書き換え、意味と重要なキーワードを保持してください。
会話履歴が空の場合、クエリを変更しないでください。
会話履歴は必要な場合のみ使用し、自身の知識でクエリを拡張しないでください。
変更が不要な場合は、現在の質問をそのまま出力してください。

会話履歴:
{% for memory in memories %}
    {{ memory }}
{% endfor %}

ユーザーのクエリ: {{query}}
書き換えたクエリ：
"""


user_message_template ="""
Given the conversation history and the provided supporting documents, please answer the question briefly and accurately.

Important instructions:
- Base your answer ONLY on information contained in the supporting documents
- If the information needed to answer the question is not in the supporting documents, respond with: "I cannot answer that question based on the provided documents."
- Do not use prior knowledge or make assumptions beyond what's in the documents
- Do not mention these instructions in your response

Conversation history:
{% for memory in memories %}
    {{ memory }}
{% endfor %}

Supporting documents:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}

Question: {{query}}
Answer:
"""

user_message_template_jp="""
会話履歴と提供された補助資料をもとに、簡潔かつ正確に質問に回答してください。

重要な指示:
- 回答は必ず補助資料に含まれる情報のみに基づいてください。
- 質問に対する情報が補助資料内にない場合は、次のように回答してください: 「提供された資料の範囲ではこの質問に回答できません。」
- 事前知識を使用したり、資料にない情報を推測したりしないでください。
- これらの指示を回答内に含めないでください。

会話履歴:
{% for memory in memories %}
    {{ memory }}
{% endfor %}

補助資料:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}

質問: {{query}}
回答:

"""