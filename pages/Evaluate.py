"""
    Score -> informativeness
    U -> usefulness
"""
import time
import streamlit as st
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

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
from pages.utils import *
from pages.style import *


conn = st.connection("supabase",type=SupabaseConnection)

next = False
debug = False


eval_table = "evaluation"
if st.button("Home", type="secondary"):
    switch_page("Landing")

js = '''
<script>
    var body = window.parent.document.querySelector(".main");
    console.log(body);
    body.scrollTop = 0;
</script>
'''

if 'df' not in st.session_state:
    
    rows = conn.query("*", table="dataset" ,ttl="0").execute()
    tmp_dataset = pd.DataFrame(rows.data)

    answers = conn.query("*", table=eval_table ,ttl="0").execute()
    tmp = pd.DataFrame(answers.data)
    st.info('The system will prompt you the first question twice. Don\' worry keep the same score and push again on next!', icon="ℹ️")

    if(len(tmp)>0):
        df_joined = tmp_dataset.merge(
            tmp.groupby('index_vis').size().reset_index(name='num_evaluations'),
            how='left',
            left_on='id',
            right_on='index_vis'
        )
        
        df_joined['num_evaluations'] = df_joined['num_evaluations'].replace(np.nan, 0)
        df_eval_newton_cot = df_joined.sort_values(by='num_evaluations')
        # df_eval_newton_cot = df_eval_newton_cot[(df_eval_newton_cot['num_evaluations'] < 3) | (df_eval_newton_cot['num_evaluations'].isnull())]
        
        # # df_eval_newton_cot = df_eval_newton_cot.sort_values(by='num_evaluations')
        # df_eval_newton_cot.set_index('id_', inplace=True)
        # df_eval_newton_cot.sort_index(inplace=True)
        # df_eval_newton_cot.reset_index(inplace=True)
        df_eval_newton_cot.reset_index(inplace=True)
        st.session_state.df = df_eval_newton_cot
    else:
        df_eval_newton_cot = tmp_dataset

    index = 0
    radio_index = None

else:
    df_eval_newton_cot = st.session_state.df
# df_eval_newton_cot.set_index('id_', inplace=True)

if (debug):
    st.dataframe(df_eval_newton_cot)

# df_eval_newton_cot = df_eval_newton_cot.sample(frac=1)
# st.dataframe(df_eval_newton_cot)


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


st.markdown(
    """
    <style>
    .stButton>button {
        width: 100%;
    }

    # .st-emotion-cache-0{
    # text-align: center;}


    .stSlider{
    padding-left: 30px;
    padding-right: 30px;
    }
    p{
    padding-left: 30px;
    padding-right: 30px;
    }

    ul{
    padding-left: 30px;
    padding-right: 30px;
    }

    # .vega-embed {
    # margin-left:40%}
    </style>

    
    """,
    unsafe_allow_html=True,
)

def text_to_markdown_bullet_list(text):
    # Split the text into individual instructions based on the semicolons
    instructions = text.split(":")[1]
    instructions = instructions.split(";")
    
    # Strip any leading/trailing whitespace from each instruction
    instructions = [instruction.strip() for instruction in instructions]
    
    # Create the Markdown bullet list
    markdown_list = "\n".join(f"- {instruction}" for instruction in instructions if instruction)
    
    return "Other instructions to generate other data visualizations, based on the generated one, could include \n" +   markdown_list

if(st.session_state.index < len(df_eval_newton_cot)):
        

    pred_vis_ = get_nl(df_eval_newton_cot.at[st.session_state.index, 'prediction'], pattern=r"Step 1\. Vegazero visualization:(.+?)Step 2\.").strip()
    pred_vis_gpt = json.loads(extract_text_between_backticks(df_eval_newton_cot.at[st.session_state.index,'prediction_gpt']))#df_eval_newton_cot.at[st.session_state.index, 'prediction_gpt'].strip()
    pred_vis_gpt['$schema'] = "https://vega.github.io/schema/vega-lite/v5.json"

    utterance = get_nl(df_eval_newton_cot.at[st.session_state.index, 'request'], pattern=r"## Request:(.+?)## Dataset:")
    dataset = get_nl(df_eval_newton_cot.at[st.session_state.index, 'request'], pattern=r"## Dataset:(.+?)## Reasoning process:").strip()

    pred_vis = insert_substring_before_encoding(pred_vis_, " data dataset ")
    pred_gpt = df_eval_newton_cot.at[st.session_state.index,'prediction_gpt']#df_eval_newton_cot.at[st.session_state.index, 'prediction_gpt'].split('Output 3. ADDITIONAL QUESTIONS')[1]
    

    explanation_gpt  = pred_gpt.split("Step 5")[1].split("Step 6")[0].replace(":", "").replace(".", "").strip()
    caption_gpt = pred_gpt.split("Step 6")[1].split("Step 7")[0].replace(":", "").replace(".", "").strip()
    questions_gpt = pred_gpt.split("Step 7")[1].replace(":", "").replace(".", "").strip()

    pred = df_eval_newton_cot.at[st.session_state.index, 'prediction'].replace(f"Step 1. Vegazero visualization: {pred_vis_}", '')

    pred = get_nl(pred, pattern=r"## Response:(.+)")

    try:
        caption_vrecs = "The visualization is" + pred.split("The visualization is ")[1].split('Step 3. Insights suggestions:')[0]
    except:
        try:
            caption_vrecs = "The visualization represents" + pred.split("The visualization represents ")[1].split('Step 3. Insights suggestions:')[0]
        except:
            try:
                caption_vrecs = "This is a" + pred.split("This is a ")[1].split('Step 3. Insights suggestions:')[0]
            except:
                try:
                    caption_vrecs = "The chart is" + pred.split("The chart is ")[1].split('Step 3. Insights suggestions:')[0]
                except:
                    try:
                        caption_vrecs = "The bar chart is" + pred.split("The bar chart is ")[1].split('Step 3. Insights suggestions:')[0]
                    except:
                        pass

    try:
        explanation_vrecs = pred.split('Step 2. Visualization explanation:')[1].split("The visualization is ")[0]
    except:
        try:
            explanation_vrecs = pred.split('Step 2. Visualization explanation:')[1].split("The visualization represents ")[0]
        except:
            try:
                explanation_vrecs = pred.split('Step 2. Visualization explanation:')[1].split("This is a ")[0]
            except:
                pass
    
    explanation_vrecs = explanation_vrecs.split('Step 3.')[0]
    questions_vrecs = pred.split('Step 3.')[1].replace("Insights suggestions:", 'Other instructions to generate other data visualizations, based on the generated one, could include:')
    st.write('Labeled', st.session_state.index+1, 'out of 20')

    def vrecs_content():
        st.write('## Response')
        # col11, col22, col33 = st.columns(3)
        vis_container = st.container(height=500)
        _, c2, _ = vis_container.columns((1, 1, 1))
        
        try: 
            with c2:
                pred_vis_vl,_ = n.vz.to_VegaLite(pred_vis)
                vis_container.vega_lite_chart(df_data, pred_vis_vl)
        except Exception:
            vis_container.write('Error to load')
            pass

        vis_score = vis_container.slider(
            "Score the visualization", 0, 5, 1,
            key="vis_score_vrecs")
        
        
        st.divider()

        caption = st.container(height=500)
        caption.markdown('#### Caption')
        caption.write(caption_vrecs)
        # value_caption = caption.slider(
        #     "Score the caption", 0, 5, 1,
        #     key="caption_vrecs")
        
        value_caption = caption.slider(
            "How informative is the caption?", 0, 5, 1,
            key="caption_vrecs"
        )
    
        u_caption = caption.slider(
            "How useful is the caption to interpret the visualization?", 0, 5, 1,
            key="u_caption_vrecs"
        )
        
        st.divider()

        explanation = st.container(height=500)
        explanation.markdown('#### Explanation')
        explanation.write(explanation_vrecs)
        # value_exaplanation = explanation.slider(
        #     "Score the explanation", 0, 5, 1,
        #     key="explanation_vrecs")
        value_exaplanation = explanation.slider(
            "How informative is the explanation?", 0, 5, 1,
            key="explanation_vrecs"
        )
    
        u_explanation = explanation.slider(
            "How useful is the caption to interpret the visualization?", 0, 5, 1,
            key="u_explanation_vrecs"
        )
        
        st.divider()

        questions = st.container(height=500)
        questions.markdown('#### Questions')
        questions.write(text_to_markdown_bullet_list(questions_vrecs))
        # value_questions = questions.slider(
        #     "Score the queries", 0, 5, 1,
        #     key="questions_vrecs")

        value_questions = questions.slider(
            "How informative are the questions?", 0, 5, 1,
            key="questions_vrecs"
        )
    
        u_questions = questions.slider(
            "How useful are the questions to interpret the visualization?", 0, 5, 1,
            key="u_questions_vrecs"
        )
        
        st.divider()
        
        narrarives = st.container(height=200)
        narrarives.markdown('#### Narratives importance')
        narrarives_importance = narrarives.slider(
            "How much have the three narratives helped you interpret the visualization?", 0, 5, 1,
            key="narratives_vrecs")
        
        return {"caption":value_caption, "explanation":value_exaplanation, "questions":value_questions, "vis_score": vis_score, "narrarives_importance": narrarives_importance,
                "u_caption":u_caption, "u_explanation":u_explanation, "u_questions":u_questions}

    def gpt_content():
        st.write('## Response')
        vis_container = st.container(height=500)
        del pred_vis_gpt['data']
        _, c2, _ = vis_container.columns((1, 1, 1))
        try: 
            with c2:
                vis_container.vega_lite_chart(df_data,pred_vis_gpt)
        except Exception:
            vis_container.write('Error to load')
        
        vis_score = vis_container.slider(
            "Score the visualization", 0, 5, 1,
            key="vis_score_gpt")
        
        st.divider()


        caption = st.container(height=500)
        caption.markdown('#### Caption')
        caption.write(caption_gpt)
        # value_caption = caption.slider(
        #     "Score the caption", 0, 5, 1,
        #     key="caption_gpt")

        value_caption = caption.slider(
            "How informative is the caption?", 0, 5, 1,
            key="caption_gpt"
        )
    
        u_caption = caption.slider(
            "How useful is the caption to interpret the visualization?", 0, 5, 1,
            key="u_caption_gpt"
        )
        
        st.divider()
        
        explanation = st.container(height=500)
        explanation.markdown('#### Explanation')
        explanation.write(explanation_gpt)
        # value_exaplanation = explanation.slider(
        #     "Score the explanation", 0, 5, 1,
        #     key="explanation_gpt")
        value_exaplanation = explanation.slider(
            "How informative is the explanation?", 0, 5, 1,
            key="explanation_gpt"
        )
    
        u_explanation = explanation.slider(
            "How useful is the caption to interpret the visualization?", 0, 5, 1,
            key="u_explanation_gpt"
        )
        
        st.divider()

        questions = st.container(height=500)
        questions.markdown('#### Questions')
        questions.write(questions_gpt)
        # value_questions = questions.slider(
        #     "Score the queries", 0, 5, 1,
        #     key="questions_gpt")
        
        value_questions = questions.slider(
            "How informative are the questions?", 0, 5, 1,
            key="questions_gpt"
        )
    
        u_questions = questions.slider(
            "How useful are the questions to interpret the visualization?", 0, 5, 1,
            key="u_questions_gpt"
        )
        
        st.divider()
        
        narrarives = st.container(height=200)
        narrarives.markdown('#### Narratives importance')
        narrarives_importance = narrarives.slider(
            "How much have the three narratives helped you interpret the visualization?", 0, 5, 1,
            key="narrarives_gpt")
        
        return {"caption":value_caption, "explanation":value_exaplanation, "questions":value_questions, "vis_score":vis_score, "narrarives_importance": narrarives_importance,
                "u_caption":u_caption, "u_explanation":u_explanation, "u_questions":u_questions}


    if(st.session_state.index < 60):
        
        with st.form("my_form"):
            
            st.write('User request')
            st.code(utterance)

            # st.write(os.path.join('https://nvbenchdatasets.s3.eu-north-1.amazonaws.com/datasets',  df_eval_newton_cot.at[st.session_state.index, 'nvBench_id'].strip() + '.csv'))
            # st.write(df_eval_newton_cot.at[st.session_state.index, 'nvBench_id'].strip())
            # df_data = pd.read_csv(os.path.join('https://nvbenchdatasets.s3.eu-north-1.amazonaws.com/datasets',  df_eval_newton_cot.at[st.session_state.index, 'nvBench_id'].strip() + '.csv'))
            if(df_eval_newton_cot.at[st.session_state.index, 'nvBench_id'].strip() == "custom_1"):
                df_data = pd.read_csv(os.path.join('https://nvbenchdatasets.s3.eu-north-1.amazonaws.com/datasets/custom_1.csv'), index_col=0,  sep=",", encoding='Latin-1')
                df_data = df_data.rename(columns=lambda x: x.lower())
            elif(df_eval_newton_cot.at[st.session_state.index, 'nvBench_id'].strip() =="custom_2"):
                df_data = pd.read_csv(os.path.join('https://nvbenchdatasets.s3.eu-north-1.amazonaws.com/datasets/custom_2.csv'),  sep=";", encoding='Latin-1', on_bad_lines='skip')
                df_data = df_data.rename(columns=lambda x: x.lower())
            else:
                df_data = pd.read_csv(os.path.join('https://nvbenchdatasets.s3.eu-north-1.amazonaws.com/datasets', df_eval_newton_cot.at[st.session_state.index, 'nvBench_id'].strip() + '.csv'), index_col=0)
                df_data = df_data.rename(columns=lambda x: x.lower())
            
            st.dataframe(df_data.head(1))

            col1, col3 = st.columns(2)

            columns_order = [col1, col3]
            random.shuffle(columns_order)
            col1, col3 = columns_order

            with col1:
                vres_scores = vrecs_content()
            with col3:
                gpt_scores = gpt_content()
            
            submitted = st.form_submit_button("Confirm and Next", type="primary")
            if submitted:
                
                col1.empty()
                col3.empty()


                temp = st.empty()
                with temp:
                    st.components.v1.html(js)
                    time.sleep(.5) # To make sure the script can execute before being deleted
                temp.empty()

                


                # st.write(df_eval_newton_cot.at[st.session_state.index, 'nvBench_id'].strip())

                if(not st.session_state.start):
                    if(not debug):
                        conn.table(eval_table).insert(
                            [{
                            'index_vis':  df_eval_newton_cot.at[st.session_state.index -1,'id'], 
                            'index_nvbench': df_eval_newton_cot.at[st.session_state.index -1, 'nvBench_id'].strip(), 
                            'user': str(st.session_state.user),
                            'score_caption_gpt': gpt_scores['caption'],
                            'score_explanation_gpt': gpt_scores['explanation'],
                            'score_questions_gpt': gpt_scores['questions'],
                            'score_caption_vrecs': vres_scores['caption'],
                            'score_explanation_vrecs':  vres_scores['explanation'],
                            'score_questions_vrecs': vres_scores['questions'],
                            'narratives_importance_gpt': gpt_scores['narrarives_importance'],
                            'narratives_importance_vrecs': vres_scores['narrarives_importance'],
                            'vis_score_gpt': gpt_scores['vis_score'],
                            'vis_score_vrecs': vres_scores['vis_score'],
                            'u_caption_vrecs': vres_scores['u_caption'],
                            'u_explanation_vrecs': vres_scores['u_explanation'],
                            'u_questions_vrecs': vres_scores['u_questions'],
                            'u_caption_gpt': gpt_scores['u_caption'],
                            'u_explanation_gpt': gpt_scores['u_explanation'],
                            'u_questions_gpt': gpt_scores['u_questions'],
                            }], count="None"
                        ).execute()

                        
                        

                    # else:
                    #     conn.table(eval_table).insert(
                    #     [{"score_response1": '', 
                    #     'index_vis':  df_eval_newton_cot.at[st.session_state.index -1,'id'], 
                    #     'index_nvbench': df_eval_newton_cot.at[st.session_state.index -1, 'nvBench_id'].strip(), 
                    #     'user': 'LUCA',
                    #     'score_response2': v1,
                    #     'score_response3': v3
                    #     }], count="None"
                    #     ).execute()
                        
                st.session_state.index += 1
            
                if(st.session_state.index>len(df_eval_newton_cot)):
                    st.session_state.index = 0
                st.session_state.start = False
                
            
    else:
        st.write("""
                ### Thank you 👏
                """)
else:
        st.write("""
                ### Thank you 👏
                """)



        