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

df_eval_newton_cot = pd.read_csv('evaluation-cot-large_54.csv', index_col=0)
def get_nl(text, pattern):
    try:
        match = re.search(pattern, text, flags=re.DOTALL)
        return match.group(1).strip()
    except:
        return False
utterance = get_nl(df_eval_newton_cot.at[0, 'request'], pattern=r"## Dataset:(.+?)## Reasoning process:")
print(utterance)
