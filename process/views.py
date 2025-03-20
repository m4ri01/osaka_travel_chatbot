from django.shortcuts import render
from django.http import JsonResponse
from django.apps import apps
from .chat_template import user_message_template,user_message_template_jp
from haystack.dataclasses import ChatMessage
from django.views.decorators.csrf import csrf_exempt
import json
import re

def chatPage(request):
    return render(request,"index.html")

def chatPageJP(request):
    return render(request,"index_jp.html")

def generate_memories_str(memories):    
    results = []
    
    for i in range(len(memories)//2) :
        results.append(f"Question: {memories[i*2]}\n\nAnswer: {memories[i*2+1]}")
    return results

def RAGJP(model,query, memory):
    if model=="llama":
        pipeline = apps.get_app_config('process').llama_jp()
    
    if model=="deepseek":
        pipeline = apps.get_app_config('process').deepseek_jp()

    memories_str = generate_memories_str(memory)

    messages = [
        ChatMessage.from_system("あなたは、提供されたサポート文書と会話履歴を使用して人間を支援する、役に立つAIアシスタントです")
    ]

    for i in range(len(memory)):
        if i %2 == 0:
            messages.append(ChatMessage.from_assistant(memory[i]['message']))
        else:
            messages.append(ChatMessage.from_user(memory[i]['message']))
    
    messages.append(ChatMessage.from_user(user_message_template_jp))

    response = pipeline.run({
        "rephraser_builder":{
            "memories":memories_str,
            "query":query
        },
        "builder": {"query": query,"memories":memories_str,"template": messages}
    })
    # print(response["llm"]["replies"][0]._content[0].text)

    return response["llm"]["replies"][0]._content[0].text

def RAG(model,query, memory):
    if model=="llama":
        pipeline = apps.get_app_config('process').llama()
    
    if model=="deepseek":
        pipeline = apps.get_app_config('process').deepseek()

    memories_str = generate_memories_str(memory)

    messages = [
        ChatMessage.from_system("You are a helpful AI assistant using provided supporting documents and conversation history to assist humans")
    ]

    for i in range(len(memory)):
        if i %2 == 0:
            messages.append(ChatMessage.from_assistant(memory[i]['message']))
        else:
            messages.append(ChatMessage.from_user(memory[i]['message']))
    
    messages.append(ChatMessage.from_user(user_message_template))

    response = pipeline.run({
        "rephraser_builder":{
            "memories":memories_str,
            "query":query
        },
        "builder": {"query": query,"memories":memories_str,"template": messages}
    })
    # print(response["llm"]["replies"][0]._content[0].text)

    return response["llm"]["replies"][0]._content[0].text
# Create your views here.

@csrf_exempt
def generator(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        query = data['query']
        chat_history = data['chat_history']
        model = data["model"]
        answer = RAG(model,query,chat_history)
        if model == "deepseek":
            answer = re.sub(r"<think>.*?</think>\s*", "", answer, flags=re.DOTALL)
        return JsonResponse({
            'status_code':200,
            'answer':answer
        })
    
@csrf_exempt
def generator_jp(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        query = data['query']
        chat_history = data['chat_history']
        model = data["model"]
        answer = RAGJP(model,query,chat_history)
        if model == "deepseek":
            answer = re.sub(r"<think>.*?</think>\s*", "", answer, flags=re.DOTALL)
        return JsonResponse({
            'status_code':200,
            'answer':answer
        })