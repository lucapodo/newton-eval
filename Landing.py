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
eval_table = "evaluation_duplicate_old"
conn = st.connection("supabase",type=SupabaseConnection)

rows = conn.query("*", table="dataset" ,ttl="0").execute()
tmp_dataset = pd.DataFrame(rows.data)

answers = conn.query("*", table=eval_table ,ttl="0").execute()
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
    # df_eval_newton_cot = df_joined
    #df_eval_newton_cot = df_joined[(df_joined['num_evaluations'] < 3) | (df_joined['num_evaluations'].isnull())]
    df_joined['num_evaluations'] = df_joined['num_evaluations'].replace(np.nan, 0)
    df_eval_newton_cot = df_joined.sort_values(by='num_evaluations')
    # df_eval_newton_cot = df_eval_newton_cot[(df_eval_newton_cot['num_evaluations'] < 3) | (df_eval_newton_cot['num_evaluations'].isnull())]
    df_eval_newton_cot.reset_index(inplace=True)
else:
    df_eval_newton_cot = tmp_dataset

# df_eval_newton_cot = df_eval_newton_cot.sample(frac=1).reset_index(drop=True) #DA RIATTIVARE è LO SHUFFLE


st.session_state.df = df_eval_newton_cot


#df_eval_newton_cot = pd.read_csv('evaluation-cot-large_54.csv', index_col=0)
#st.session_state.df = df_eval_newton_cot
st.session_state.user = uuid.uuid4()
st.session_state.start = True

st.write("# Welcome to V-RECS Turing test! 👋")
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
    1. You will be presented with an utterance and a dataset description. The total number of responses to evaluate are 20.
    2. Along with this, you will see two responses proposed for the given utterance, as in the example below.
    3. Your task is to rank each response on a scale from 1 to 5 based on how human-like or natural it sounds to you.
    4. Assign a score of 1 to the response that seems the least human-like or natural to you, and a score of 5 to the response that seems the most human-like or natural.
    5. You can assign scores between 1 and 5 to both responses, ensuring each response receives a unique score.
    6. Your ratings will help us assess the effectiveness of various language generation models.

    🚨 TO SCORE CONSIDER BOTH THE TEXT AND THE VISUALIZATION GENERATED.

    ### Score description:
    1. Completely Meaningless: Indicates utter insignificance or lack of importance.
    2. Mostly Meaningless: Implies minimal significance or relevance.
    3. Beginning to Inform: Signifies the start of providing some information or significance.
    4. Mostly Meaningful: Suggests considerable importance or relevance.
    5. Completely Meaningful: Signifies utmost significance or profound relevance.

    Thank you for your participation and dedication to improving visual communication!

    ## Example:

    ### User Utterance:
    """
)
# st.write("SISTEMARE CHE DOMANDA E RISPOSTA COICIDONO")
st.write("""
    :blue[Return the average price of products that have each category code .]
    """)
st.write("""
    ### Dataset Description:   
        """)
st.write("""
         
    :blue[[('product_id', 'numeric'), ('parent_product_id', 'numeric'), ('product_category_code', 'categorical'), ('date_product_first_available', 'temporal'), ('date_product_discontinued', 'temporal'), ('product_name', 'categorical'), ('product_description', 'categorical'), ('product_price', 'numeric')]]
    """)
st.write("""
    ### Responses:
""")


col1, col3 = st.columns(2)
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


with col1:
    st.write("""
    #### Response 1
             """)
    st.image("image_example.png", width=100)
    st.write("""
    The user is interested in understanding the average price of products in each category. Therefore, the 'product_category_code' is selected as the x-axis to represent different categories, and the 'product_price' is selected as the y-axis to represent the price of the products. The'mean' aggregate function is used to calculate the average price for each category. The data is then grouped by 'product_category_code' to calculate the average price for each category. This is a bar chart where the x-axis represents different product category codes and the y-axis represents the mean price of products in each category. The bars are grouped by product category code.

    - Which product category has the highest average price?
    - Which product category has the lowest average price?
    - Are there any product categories that have similar average prices?
    """)
    st.radio(
        "Score the answer",
        radio_options, 
        captions = radio_captions, 
        key="2")


with col3:
    st.write("""
    #### Response 2
             """)
    st.image("image_example.png", width=100)
    st.write("""
    The visualization is a bar chart where each bar represents a product category. The height of each bar represents the average price of products in that category. This allows us to easily compare the average prices across different product categories.

    Other instructions to generate other data visualizations, based on the generated one, could be:

    - Return the maximum price of products that have each category code.
    - Return the minimum price of products that have each category code.
    - Return the total number of products that have each category code.
    - Return the average price of products that have each category code, but only for products that are still available (not discontinued).
    """)

    st.radio(
        "Score the answer",
        radio_options, 
        captions = radio_captions, 
        key="3")

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
        "Yopur experties",
     
        placeholder="e.g., Data visualization",
    )

if st.button("Start evaluating", type="primary"):

    st.write(text_gender)
    st.write(text_age)
    st.write(text_experties)

    conn.table("population").insert(
        [{"experties": text_experties, 
        'age':  text_age, 
        'gender': text_gender, 
        'user_id': str(st.session_state.user),
        }], count="None"
    ).execute()

    switch_page("Evaluate")

