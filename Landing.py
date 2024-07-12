import streamlit as st
import pandas as pd
import uuid
from streamlit_extras.switch_page_button import switch_page 
from st_supabase_connection import SupabaseConnection
import numpy as np
# st.set_page_config(layout="wide")

st.session_state.clear()
st.set_page_config(
    page_title="Hello",
    page_icon="👋",
    initial_sidebar_state="collapsed"
)

eval_table = "evaluation"
conn = st.connection("supabase",type=SupabaseConnection)

dataset = conn.query("*", table="dataset_new" ,ttl="0").execute()
df_dataset = pd.DataFrame(dataset.data)

evaluations = conn.query("*", table=eval_table ,ttl="0").execute()
df_evaluations = pd.DataFrame(evaluations.data)

# st.write(len(df_evaluations))

if(len(df_evaluations)>0):
# Perform left join
    df_joined = df_dataset.merge(
        df_evaluations.groupby('index_vis').size().reset_index(name='num_evaluations'),
        how='left',
        left_on='id',
        right_on='index_vis'
    )

    # Apply conditions
    # df_eval_newton_cot = df_joined
    #df_eval_newton_cot = df_joined[(df_joined['num_evaluations'] < 3) | (df_joined['num_evaluations'].isnull())]

    df_joined['num_evaluations'] = df_joined['num_evaluations'].replace(np.nan, 0)
    df_eval_newton_cot = df_joined.sort_values(by='num_evaluations')
    # df_eval_newton_cot = df_eval_newton_cot[(df_eval_newton_cot['num_evaluations'] < 3) | (df_eval_newton_cot['num_evaluations'].isnull())]
    df_eval_newton_cot.reset_index(inplace=True)
else:
    df_eval_newton_cot = df_dataset

# df_eval_newton_cot = df_eval_newton_cot.sample(frac=1).reset_index(drop=True) #DA RIATTIVARE è LO SHUFFLE


st.session_state.df = df_eval_newton_cot




#df_eval_newton_cot = pd.read_csv('evaluation-cot-large_54.csv', index_col=0)
#st.session_state.df = df_eval_newton_cot
st.session_state.user = uuid.uuid4()
st.session_state.start = True

st.write("# Welcome to V-RECS evaluation test! 👋")
left_co, cent_co,last_co = st.columns(3)
with cent_co:
    st.image("logo.png")

# with st.sidebar:
#     st.title('Newton webapp')
#     st.image('assets/newton.jpg', output_format='auto')
#     # username = st.text_input('Inserisci il tuo nome', '')
#     st.write('The current user is', st.session_state.user)
#     # st.session_state.username = username
#     # st.write('Instance = ', st.session_state.index)


def navigate_to_page(page):
    st.query_params(page=page)

session_state = st.session_state
current_page = session_state.get("page", "home")

st.markdown(
    """
    ## Test description

    Welcome! Your valuable feedback on VRECS responses is crucial for enhancing its effectiveness. Below are the steps to follow:

    ### Task Instructions:
    
    1. You will evaluate 20 responses, each consisting of an utterance and a dataset description.
    2. For each utterance, you will see two proposed responses.
    3. Each response includes four parts: the visualization, the explanation (E), the caption (C), and the suggested questions (S).
    4. Rank each response on a scale from 1 to 5 based on how human-like or natural it sounds.
    5. E, C, and S have two scores:
        - **Informativeness**: How well the text conveys the semantic meaning related to the visualization.
        - **Usefulness**: How helpful the text is in interpreting the visualization.
    6. Finally, you have to provide an overall score of the informativenss of E,C,S

    🚨 TO SCORE CONSIDER BOTH THE TEXT AND THE VISUALIZATION GENERATED.

    ### Score description:
    * 1: Completely Meaningless: Indicates utter insignificance or lack of importance.
    * 2: Mostly Meaningless: Implies minimal significance or relevance.
    * 3: Beginning to Inform: Signifies the start of providing some information or significance.
    * 4: Mostly Meaningful: Suggests considerable importance or relevance.
    * 5: Completely Meaningful: Signifies utmost significance or profound relevance.

    Thank you for your participation and dedication to improving visual communication!

    ## Example:

    ### User's query:
    """
)
st.write("""
    :blue[What is the average rank of pilots in different positions?]
    """)
st.write("""
    ### Dataset Description:   
        """)
# st.write("""
         
#     :blue[[('product_id', 'numeric'), ('parent_product_id', 'numeric'), ('product_category_code', 'categorical'), ('date_product_first_available', 'temporal'), ('date_product_discontinued', 'temporal'), ('product_name', 'categorical'), ('product_description', 'categorical'), ('product_price', 'numeric')]]
#     """)
st.dataframe(pd.read_csv("https://nvbenchdatasets.s3.eu-north-1.amazonaws.com/datasets/2586.csv").head(1))
st.write("""
    ### Responses:
""")


col1, col3 = st.columns(2)
# radio_options = [
#     "1 - Completely Meaningless",
#     "2 - Mostly Meaningless",
#     "3 - Beginning to Inform",
#     "4 - Mostly Meaningful",
#     "5 - Completely Meaningful"
# ]
# radio_captions = [
#     "Indicates utter insignificance or lack of importance.",
#     "Implies minimal significance or relevance.",
#     "Signifies the start of providing some information or significance.",
#     "Suggests considerable importance or relevance.",
#     "Signifies utmost significance or profound relevance."
# ]


with col1:
    st.write("""
    #### Response
             """)
    st.image("image_example.png", width=100)

     
        
    vis_score = st.slider(
        "Score the visualization", 0, 5, 1)


    caption = st.container(height=400)
    caption.markdown('#### Caption')
    caption.write("""
                    The visualization is a bar chart that shows the average rank of pilots in different positions The x-axis represents the different positions and the y-axis represents ...
                    """)
    value_caption = caption.slider(
        "How informative is the caption?", 0, 5, 1,
        )
    
    value_caption = caption.slider(
        "How useful is the caption to interpret the visualization?", 0, 5, 1,
        )
    
    explanation = st.container(height=400)
    explanation.markdown('#### Explanation')
    explanation.write("""
The 'rank' and 'position' features are the best among all the others from the dataset based on the user instruction because the user wants to know the average rank of pilots in different ...""")
    
    explanation.slider(
        "How informative is the explanation?", 0, 5, 1,
        )
    explanation.slider(
        "How useful is the explanation to interpret the visualization?", 0, 5, 1,
        )

    questions = st.container(height=400)
    questions.markdown('#### Questions')
    questions.write("""
                Other instructions to generate other data visualizations, based on the generated one, could be
                * What is the average age of pilots in different positions?
                    """)
    questions.slider(
        "How informative are the questions?", 0, 5, 1,
        )
    
    questions.slider(
        "How useful are the questions to interpret the visualization", 0, 5, 1,
        )
    
    narrarives = st.container(height=200)
    narrarives.markdown('#### Narratives importance')
    narrarives_importance = narrarives.slider(
        "How much have the three narratives helped you interpret the visualization?", 0, 5, 1,
        key="18"
       )


with col3:
    st.write("""
    #### Response
             """)
    st.image("image_example.png", width=100)
    
    st.slider(
        "Score the visualization", 0, 5, 1,
        key="11")


    caption = st.container(height=400)
    caption.markdown('#### Caption')
    caption.write("""
                    The visualization is a bar chart that shows the average rank of pilots in different positions The x-axis represents the different positions and the y-axis represents ...
                    """)
    value_caption = caption.slider(
        "How informative is the caption?", 0, 5, 1,
        key="12"
        )
    
    value_caption = caption.slider(
        "How useful is the caption to interpret the visualization?", 0, 5, 1,
        key="13"
        )
    
    explanation = st.container(height=400)
    explanation.markdown('#### Explanation')
    explanation.write("""
        The 'rank' and 'position' features are the best among all the others from the dataset based on the user instruction because the user wants to know the average rank of pilots in different ...""")
    
    explanation.slider(
        "How informative is the explanation?", 0, 5, 1,
        key="14"
        )
    explanation.slider(
        "How useful is the explanation to interpret the visualization?", 0, 5, 1,
        key="15"
        )

    questions = st.container(height=400)
    questions.markdown('#### Questions')
    questions.write("""
                Other instructions to generate other data visualizations, based on the generated one, could be
                * What is the average age of pilots in different positions?
                    """)
    questions.slider(
        "How informative are the questions?", 0, 5, 1,
        key="16"
        )
    
    questions.slider(
        "How useful are the questions to interpret the visualization", 0, 5, 1,
        key="17"
        )
    
    narrarives = st.container(height=200)
    narrarives.markdown('#### Narratives importance')
    narrarives_importance = narrarives.slider(
        "How much have the three narratives helped you interpret the visualization?", 0, 5, 1,
        key="19"
       )


st.write("## Before to proceed, please fillout this form:")

text_gender = st.text_input(
        "Gender",
     
        placeholder="Male/Female/Other",
    )

text_age = st.text_input(
        "Age",
       
        placeholder="e.g., 25",
    )

text_experties = st.text_input(
        "Your expertise",

        placeholder="e.g., Data visualization",
    )

da_skills = st.slider(
            "Provide your experties in data analysis in a scale from 1 to 5, where 1=non-expert to 5=expert", 0, 5, 1
            )


dv_skills = st.slider(
            "Provide your experties in data visualization in a scale from 1 to 5, where 1=non-expert to 5=expert", 0, 5, 1,
            )

if st.button("Start evaluating", type="primary"):

    # st.write(text_gender)
    # st.write(text_age)
    # st.write(text_experties)
    st.write(da_skills)

    conn.table("population").insert(
        [{"experties": text_experties, 
        'age':  text_age, 
        'gender': text_gender, 
        'user_id': str(st.session_state.user),
        'da_skills': da_skills, 
        'dv_skills': dv_skills, 
        }], count="None"
    ).execute()

    switch_page("Evaluate")

