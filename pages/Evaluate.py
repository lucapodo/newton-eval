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


st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
conn = st.connection("supabase",type=SupabaseConnection)

if st.button("Home", type="secondary"):
    switch_page("Landing")

rows = conn.query("*", table="dataset" ,ttl="0").execute()
tmp_dataset = pd.DataFrame(rows.data)

answers = conn.query("*", table="evaluation" ,ttl="0").execute()
tmp = pd.DataFrame(answers.data)

if(len(tmp)>0):
# Perform left join
    df_joined = tmp_dataset.merge(
        tmp.groupby('index_vis').size().reset_index(name='num_evaluations'),
        how='left',
        left_on='id',
        right_on='index_vis'
    )

    # Apply conditions
    df_eval_newton_cot = df_joined[(df_joined['num_evaluations'] < 1) | (df_joined['num_evaluations'].isnull())]
    df_eval_newton_cot.reset_index(inplace=True)
else:
    df_eval_newton_cot = tmp_dataset

df_eval_newton_cot = df_eval_newton_cot.sample(frac=1).reset_index(drop=True)
# df_eval_newton_cot = pd.DataFrame(rows.data)
index = 0
radio_index = None

if 'index' not in st.session_state:
	st.session_state.index = 0

if 'start' not in st.session_state:
	st.session_state.start = True

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

pred_vis_ = get_nl(df_eval_newton_cot.at[st.session_state.index, 'prediction'], pattern=r"Step 1\. Vegazero visualization:(.+?)Step 2\.").strip()
groundtruth_vis_ = get_nl(df_eval_newton_cot.at[st.session_state.index, 'groundtruth'], pattern=r"Step 1\. Vegazero visualization:(.+?)Step 2\.").strip()
pred_vis_gpt = json.loads(extract_text_between_backticks(df_eval_newton_cot.at[st.session_state.index,'prediction_gpt']))#df_eval_newton_cot.at[st.session_state.index, 'prediction_gpt'].strip()
pred_vis_gpt['$schema'] = "https://vega.github.io/schema/vega-lite/v5.json"


# pred_llama_1 = json.loads(extract_text_between_backticks(df_eval_newton_cot.at[st.session_state.index,'prediction_gpt']))#df_eval_newton_cot.at[st.session_state.index, 'prediction_gpt'].strip()
# pred_llama = df_eval_newton_cot.at[st.session_state.index,'prediction_gpt']#df_eval_newton_cot.at[st.session_state.index, 'prediction_gpt'].split('Output 3. ADDITIONAL QUESTIONS')[1]

# try:
#     pred_llama_vis = parse_json_garbage (pred_llama)
#     y = json.dumps(pred_llama_vis)
#     pred_llama_ = pred_llama.replace(pred_llama_vis, "")
# except Exception as e:
#     pred_llama_ = pred_llama

utterance = get_nl(df_eval_newton_cot.at[st.session_state.index, 'request'], pattern=r"## Request:(.+?)## Dataset:")
dataset = get_nl(df_eval_newton_cot.at[st.session_state.index, 'request'], pattern=r"## Dataset:(.+?)## Reasoning process:").strip()

groundtruth_vis = insert_substring_before_encoding(groundtruth_vis_, " data dataset ")
pred_vis = insert_substring_before_encoding(pred_vis_, " data dataset ")


pred_gpt = df_eval_newton_cot.at[st.session_state.index,'prediction_gpt']#df_eval_newton_cot.at[st.session_state.index, 'prediction_gpt'].split('Output 3. ADDITIONAL QUESTIONS')[1]
pred_gpt = pred_gpt.split('Step 5:')[1]
pred_gpt = pred_gpt.replace('Step 6:', '')


pred = df_eval_newton_cot.at[st.session_state.index, 'prediction'].replace(f"Step 1. Vegazero visualization: {pred_vis_}", '')
pred = get_nl(pred, pattern=r"## Response:(.+)")
pred = pred.replace("Step 3.", "\n Step 3.")
pred = pred.replace("Step 2.", "\n Step 2.")
pred = pred.replace("  ", "")
pred = pred.split('Step 2. Visualization explanation:')[1]
pred = pred.replace('Step 3. Insights suggestions:', '')

# ground = df_eval_newton_cot.at[st.session_state.index, 'groundtruth'].replace(f"Step 1. Vegazero visualization: {groundtruth_vis_}", '')
# ground = get_nl(ground, pattern=r"## Response:(.+)")
# ground = ground.replace("Step 3.", "\n **Step 3.**")
# ground = ground.replace("Step 2.", "\n **Step 2.**")
# ground = ground.replace("  ", "")

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

# def col1_content():
#     st.write('## Response 1')
#     groundtruth_vis_vl, _ = n.vz.to_VegaLite(groundtruth_vis)
#     st.vega_lite_chart(df_data, groundtruth_vis_vl)
#     st.write(ground)
#     value1 = st.radio(
#         "Score the answer",
#         radio_options,
#         captions = radio_captions,
#         key="1")
#     return value1
    
def col2_content():
    st.write('## Response 2')
    
    try: 
        pred_vis_vl,_ = n.vz.to_VegaLite(pred_vis)
        # st.write(pred_vis_vl)
        # st.write(df_data)
        st.vega_lite_chart(df_data, pred_vis_vl)
    except Exception:
        pass
    st.write(pred)
    value2 =  st.radio(
        "Score the answer",
        radio_options, 
        captions = radio_captions, 
        key="2")
    return value2

def col3_content():
    st.write('## Response 3')
    # st.write(pred_vis_gpt)
    del pred_vis_gpt['data']
    # st.write(pred_vis_gpt)
    try: 
        # for i in range (len(pred_llama_vis)):
        st.vega_lite_chart(df_data,pred_vis_gpt)
    except Exception:
        pass
    st.write(pred_gpt)
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
    start = True
    with st.form("my_form"):

        st.write('User request')
        st.code(utterance)
        st.write('Dataset')
        st.code(dataset)
        # st.write(os.path.join('https://nvbenchdatasets.s3.eu-north-1.amazonaws.com/datasets',  df_eval_newton_cot.at[st.session_state.index, 'nvBench_id'].strip()) + '.csv')
        # path = 'https://nvbenchdatasets.s3.eu-north-1.amazonaws.com/datasets/' + df_eval_newton_cot.at[st.session_state.index, 'nvBench_id'][1].strip() + '.csv'
        # st.write(path)
        df_data = pd.read_csv(os.path.join('https://nvbenchdatasets.s3.eu-north-1.amazonaws.com/datasets',  df_eval_newton_cot.at[st.session_state.index, 'nvBench_id'].strip() + '.csv'))
        df_data = df_data.rename(columns=lambda x: x.lower())
        # st.dataframe(df_data)
        # pred_vis_gpt['data']['url'] = 'https://nvbenchdatasets.s3.eu-north-1.amazonaws.com/datasets/' + df_eval_newton_cot.at[st.session_state.index, 'nvBench_id'].strip() + '.csv'
        # st.write(pred_vis_gpt['data']['url'])
        col1, col3 = st.columns(2)
        
        submitted = st.form_submit_button("Confirm and Next", type="primary")
        
        if submitted:
            columns_order = [col1, col3]
            # columns_order = [col1, col2, col3]
            random.shuffle(columns_order)
            col1, col3 = columns_order

            with col1:
                # v1 = col1_content()
                v1 = col2_content()

            # with col2:
            #     v2 = col2_content()

            with col3:
                v3 = col3_content()

            st.write(df_eval_newton_cot.at[st.session_state.index, 'nvBench_id'].strip())
            if(not st.session_state.start):
                conn.table("evaluation").insert(
                    [{"score_response1": v1, 
                    'index_vis':  df_eval_newton_cot.at[st.session_state.index,'id'], 
                    'index_nvbench': df_eval_newton_cot.at[st.session_state.index, 'nvBench_id'].strip(), 
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
        

        