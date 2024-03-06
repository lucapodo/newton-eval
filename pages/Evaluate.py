import streamlit as st
import pandas as pd
import numpy as np
import re
from newtonmetrics.vegazero.VegaZero2VegaLite import VegaZero2VegaLite 
from newtonmetrics.newton.newton import Newton 
from st_supabase_connection import SupabaseConnection
import altair_viewer
import altair as alt
import json
import os
n = Newton()

st.set_page_config(layout="wide")
conn = st.connection("supabase",type=SupabaseConnection)

df_eval_newton_cot = st.session_state.df
index = 0

with st.sidebar:
    st.title('Newton webapp')
    st.write('The current user is', st.session_state.user)

if 'index' not in st.session_state:
	st.session_state.index = 0

def increment_counter(increment_value=0):
    conn.table("evaluation").insert(
        [{"score": "aa", 'index_vis':  st.session_state.index, 'index_nvbench': st.session_state.nvbench_id, 'user': st.session_state.username}], count="None"
    ).execute()
    st.session_state.index += increment_value
    if(st.session_state.index>len(df_eval_newton_cot)):
        st.session_state.index = 0
    

# def decrement_counter(decrement_value=0):
#     st.session_state.index -= decrement_value
#     if(st.session_state.index<0):
#         st.session_state.index = len(df_eval_newton_cot) -1

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
utterance = get_nl(df_eval_newton_cot.at[st.session_state.index, 'request'], pattern=r"## Request:(.+?)## Dataset:")
dataset = get_nl(df_eval_newton_cot.at[st.session_state.index, 'request'], pattern=r"## Dataset:(.+?)## Reasoning process:").strip()

groundtruth_vis = insert_substring_before_encoding(groundtruth_vis_, " data dataset ")
pred_vis = insert_substring_before_encoding(pred_vis_, " data dataset ")

pred = df_eval_newton_cot.at[st.session_state.index, 'prediction'].replace(f"Step 1. Vegazero visualization: {pred_vis_}", '')
pred = get_nl(pred, pattern=r"## Response:(.+)")
pred = pred.replace("Step 3.", "\n Step 3.")
pred = pred.replace("Step 2.", "\n Step 2.")
pred = pred.replace("  ", "")

ground = df_eval_newton_cot.at[st.session_state.index, 'groundtruth'].replace(f"Step 1. Vegazero visualization: {groundtruth_vis_}", '')
ground = get_nl(ground, pattern=r"## Response:(.+)")
ground = ground.replace("Step 3.", "\n **Step 3.**")
ground = ground.replace("Step 2.", "\n **Step 2.**")
ground = ground.replace("  ", "")

id = df_eval_newton_cot.at[st.session_state.index, 'nvBench_id'].strip()
st.session_state.nvbench_id = id
df_data = pd.read_csv(os.path.join('/Users/luca/Documents/Dottorato/LLM4VIS/Newton/data/final/NewtonLLM dataset/cot/datasets',  id + '.csv'))


st.write('User request: ', utterance )
st.write('Dataset explored: ', dataset )


col1, col2, col3 = st.columns(3)
with col1:
    st.write('## Response 1')
    groundtruth_vis_vl, _ = n.vz.to_VegaLite(groundtruth_vis)
    st.vega_lite_chart(df_data, groundtruth_vis_vl)
    st.write(ground)
    # st.write("## Vis")
    # st.code(groundtruth_vis)
    values1 = st.slider(
    'Select a range of values',
    0.0, 100.0, (25.0, 75.0),
    key='one')
st.write('Values:', values1)
with col2:
    st.write('## Response 2')
    try: 
        pred_vis_vl,_ = n.vz.to_VegaLite(pred_vis)
        st.vega_lite_chart(df_data, pred_vis_vl)
    except Exception:
        pass
    st.write(pred)
    values2 = st.slider(
    'Select a range of values',
    0.0, 100.0, (0.0, 75.0),
    key='two')
    st.write('Values:', values2)
with col3:
    st.write('## Response 3')
    try: 
        pred_vis_vl,_ = n.vz.to_VegaLite(pred_vis)
        st.vega_lite_chart(df_data, pred_vis_vl)
    except Exception:
        pass
    st.write(pred)
    values = st.slider(
    'Select a range of values',
    0.0, 100.0, (25.0, 75.0),
    key='three')
    st.write('Values:', values)
    
    
st.write(utterance)


st.button('Increment', on_click=increment_counter, kwargs=dict(increment_value=1))




# st.write(f"Pred: {pred}")
# st.write(f"Groundtruth: {groundtruth}")
# st.write(f"Len: {len(df_eval_newton_cot)}")


