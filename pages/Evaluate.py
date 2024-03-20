import streamlit as st
import pandas as pd
import numpy as np
import re
from newtonmetrics.vegazero.VegaZero2VegaLite import VegaZero2VegaLite 
from newtonmetrics.newton.newton import Newton 
from st_supabase_connection import SupabaseConnection
from streamlit_extras.switch_page_button import switch_page 
import altair_viewer
import altair as alt
import json
import os
n = Newton()
import random
import uuid

next = False
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
conn = st.connection("supabase",type=SupabaseConnection)

if st.button("Home", type="secondary"):
    switch_page("Landing")

rows = conn.query("*", table="dataset" ,ttl="0").execute()
tmp_dataset = pd.DataFrame(rows.data)

answers = conn.query("*", table="evaluation" ,ttl="0").execute()
tmp = pd.DataFrame(answers.data)
st.info('The system will prompt you the first question twice. Don\' worry keep the same score and push again on next!', icon="ℹ️")

if(len(tmp)>0):
# Perform left join
    df_joined = tmp_dataset.merge(
        tmp.groupby('index_vis').size().reset_index(name='num_evaluations'),
        how='left',
        left_on='id',
        right_on='index_vis'
    )

    # Apply conditions
    df_eval_newton_cot = df_joined[(df_joined['num_evaluations'] < 3) | (df_joined['num_evaluations'].isnull())]
    df_eval_newton_cot.reset_index(inplace=True)
else:
    df_eval_newton_cot = tmp_dataset

# df_eval_newton_cot = df_eval_newton_cot.sample(frac=1).reset_index(drop=True) #DA RIATTIVARE è LO SHUFFLE
# df_eval_newton_cot = pd.DataFrame(rows.data)
index = 0
radio_index = None

st.dataframe(df_eval_newton_cot)


if 'index' not in st.session_state:
    st.session_state.index = 0
   

if 'start' not in st.session_state:
	st.session_state.start = True

if 'user' not in st.session_state:
    st.session_state.user = uuid.uuid4()

with st.sidebar:
    st.title('Newton webapp')
    st.write('The current user is', st.session_state.user)
    st.write(len(df_eval_newton_cot))

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


pred_vis_ = get_nl(df_eval_newton_cot.at[st.session_state.index, 'prediction'], pattern=r"Step 1\. Vegazero visualization:(.+?)Step 2\.").strip()
groundtruth_vis_ = get_nl(df_eval_newton_cot.at[st.session_state.index, 'groundtruth'], pattern=r"Step 1\. Vegazero visualization:(.+?)Step 2\.").strip()
pred_vis_gpt = json.loads(extract_text_between_backticks(df_eval_newton_cot.at[st.session_state.index,'prediction_gpt']))#df_eval_newton_cot.at[st.session_state.index, 'prediction_gpt'].strip()
pred_vis_gpt['$schema'] = "https://vega.github.io/schema/vega-lite/v5.json"

utterance = get_nl(df_eval_newton_cot.at[st.session_state.index, 'request'], pattern=r"## Request:(.+?)## Dataset:")
dataset = get_nl(df_eval_newton_cot.at[st.session_state.index, 'request'], pattern=r"## Dataset:(.+?)## Reasoning process:").strip()

groundtruth_vis = insert_substring_before_encoding(groundtruth_vis_, " data dataset ")
pred_vis = insert_substring_before_encoding(pred_vis_, " data dataset ")

pred_gpt = df_eval_newton_cot.at[st.session_state.index,'prediction_gpt']#df_eval_newton_cot.at[st.session_state.index, 'prediction_gpt'].split('Output 3. ADDITIONAL QUESTIONS')[1]
try:
    pred_gpt = pred_gpt.split('Step 5: ')[1]
except Exception as e:
    try:
        pred_gpt = pred_gpt.split('Step 5. ')[1]
    except Exception as e:
        pred_gpt = pred_gpt.split('Step 5 ')[1]

pred_gpt = pred_gpt.replace('Step 6. ', '')
pred_gpt = pred_gpt.replace('Step 6.', '')
pred_gpt = pred_gpt.replace('Step 6: ', '')
pred_gpt = pred_gpt.replace('Step 6:', '')
pred_gpt = pred_gpt.replace('Step 7:', '')
pred_gpt = pred_gpt.replace('Step 7: ', '')
pred_gpt = pred_gpt.replace('Step 7.', '')
pred_gpt = pred_gpt.replace('Step 7. ', '')
pred_gpt = re.sub(r'\n\s+', '\n', pred_gpt)

pred = df_eval_newton_cot.at[st.session_state.index, 'prediction'].replace(f"Step 1. Vegazero visualization: {pred_vis_}", '')
pred = get_nl(pred, pattern=r"## Response:(.+)")
pred = pred.replace("Step 3.", "\n Step 3.")
pred = pred.replace("Step 2.", "\n Step 2.")
pred = pred.replace("  ", "")
pred = pred.split('Step 2. Visualization explanation:')[1]
pred = pred.replace('Step 3. Insights suggestions:', 'Other instructions to generate other data visualizations, based on the generated one, could include:')
pred = re.sub(r'\n\s+', '\n', pred)


radio_options = [
    "1 - Completely Meaningless",
    "2 - Mostly Meaningless",
    "3 - Beginning to Inform",
    "4 - Mostly Meaningful",
    "5 - Completely Meaningful"
]
radio_captions = [
    "Indicates utter insignificance or lack of importance.",
    "Implies minimal significance or relevance.",
    "Signifies the start of providing some information or significance.",
    "Suggests considerable importance or relevance.",
    "Signifies utmost significance or profound relevance."
]        

st.write('Labeled', st.session_state.index+1, 'out of 20')

def col2_content():
    st.write('## Response')
    col11, col22, col33 = st.columns(3)
    
    try: 
        with col22:
            pred_vis_vl,_ = n.vz.to_VegaLite(pred_vis)
            # st.write(pred_vis_vl)
            # st.write(df_data)
            st.vega_lite_chart(df_data, pred_vis_vl)
    except Exception:
        st.write('Error to load')
        pass
    
    questions = detect_questions(pred)
    # Format questions as bullet list
    bullet_list = format_as_bullet_list(questions)
    text_without_questions = remove_questions(pred, questions)
    st.write(text_without_questions.strip(), unsafe_allow_html=True)
    st.write(bullet_list)

    value2 =  st.radio(
        "Score the answer",
        radio_options, 
        captions = radio_captions, 
        key="2")
    return value2

def col3_content():
    st.write('## Response')
    # st.write(pred_vis_gpt)
    del pred_vis_gpt['data']
    # st.write(pred_vis_gpt)
    col111, col222, col333 = st.columns(3)
    try: 
        with col222:
            # for i in range (len(pred_llama_vis)):
            st.vega_lite_chart(df_data,pred_vis_gpt)
    except Exception:
        st.write('Error to load')

    st.write(pred_gpt.strip(), unsafe_allow_html=True)

    value3 =  st.radio(
        "Score the answer",
        radio_options, 
        captions = radio_captions, 
        key="3")
    return value3

st.markdown(
    """
    <style>
    .stButton>button {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


if(st.session_state.index < 20):
    
    with st.form("my_form"):
        
        
        st.write('User request')
        st.code(utterance)
        st.write('Dataset')
        st.code(dataset)
        
        df_data = pd.read_csv(os.path.join('https://nvbenchdatasets.s3.eu-north-1.amazonaws.com/datasets',  df_eval_newton_cot.at[st.session_state.index, 'nvBench_id'].strip() + '.csv'))
        df_data = df_data.rename(columns=lambda x: x.lower())

        
        col1, col3 = st.columns(2)

        columns_order = [col1, col3]
        # columns_order = [col1, col2, col3]
        random.shuffle(columns_order)
        col1, col3 = columns_order

        with col1:
            # v1 = col1_contsent()
            v1 = col2_content()

        # with col2:
        #     v2 = col2_content()

        with col3:
            v3 = col3_content()
        
        submitted = st.form_submit_button("Confirm and Next", type="primary")
        
        if submitted:
            
            col1.empty()
            col3.empty()

            # st.write(df_eval_newton_cot.at[st.session_state.index, 'nvBench_id'].strip())
            if(not st.session_state.start):
            
                conn.table("evaluation").insert(
                    [{"score_response1": '', 
                    'index_vis':  df_eval_newton_cot.at[st.session_state.index -1,'id'], 
                    'index_nvbench': df_eval_newton_cot.at[st.session_state.index -1, 'nvBench_id'].strip(), 
                    'user': str(st.session_state.user),
                    'score_response2': v1,
                    'score_response3': v3
                    }], count="None"
                ).execute()
            st.session_state.index += 1
                
    
        
            if(st.session_state.index>len(df_eval_newton_cot)):
                st.session_state.index = 0
            # st.write(st.session_state.index)
            st.session_state.start = False
            
            # st.write(df_eval_newton_cot.at[st.session_state.index, 'nvBench_id'].strip())
            # st.write(st.session_state.start)
else:
    st.write("""
            ### Thank you 👏
            """)




    