#pip install -q huggingface_hub
from huggingface_hub import InferenceClient, login
import json
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import argparse
import copy
import os
import openai
from google import genai

MODEL_NAME = os.environ.get("MODEL_NAME")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def load_jsonl(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def save_jsonl(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def model_calling(prompt, model_name):
    if model_name == "gpt-4o-mini":
        messages = [{"role":"system","content":"You are an author of an NLP conference paper and trying to write rebuttal for a specific review."}]
        messages = [{"role":"user","content":prompt}]
        try:
            response = openai.chat.completions.create(
                model=model_name,
                messages=messages
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return "Error"
    elif model_name == "gemini-2.0-flash":
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text.strip()
    else:
        print("Model not found")
        print(MODEL_NAME)
