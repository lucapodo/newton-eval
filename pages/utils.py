

import re
import json
import streamlit as st

def extract_text_between_backticks(text):
    pattern = r"```(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    if(len(matches)> 0):
        res = matches[0].replace('json', '')
        # print(res)
        res = res.replace('vega', '')
        # print(res)
    else: 
        res = None
    return res

def parse_json_garbage(s):
    s = s[next(idx for idx, c in enumerate(s) if c in "{["):]
    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        return json.loads(s[:e.pos])

def get_nl(text, pattern):
    try:
        match = re.search(pattern, text, flags=re.DOTALL)
        return match.group(1).strip()
    except:
        return False

def insert_substring_before_encoding(main_string, substring):
    index = main_string.find("encoding")
    if index == -1:
        return main_string + substring
    else:
        return main_string[:index] + substring + main_string[index:]

def detect_questions(text):
    # Regular expression to detect questions
    pattern = r'\b[A-Z][\w\s,]+\?'

    # Find all matches
    questions = re.findall(pattern, text)

    return questions

def format_as_bullet_list(questions):
    # Format questions as bullet list
    bullet_list = '\n'.join([f'- {question}' for question in questions])
    return bullet_list

def remove_questions(text, questions):
    # Remove detected questions from the original text
    for question in questions:
        text = text.replace(question, '')
    # Remove any extra semicolons and whitespaces
    text = text.strip('; ')
    return text
   
