import streamlit as st
import pandas as pd
import uuid
from streamlit_extras.switch_page_button import switch_page 
# st.set_page_config(layout="wide")

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
    initial_sidebar_state="collapsed"
)
df_eval_newton_cot = pd.read_csv('evaluation-cot-large_54.csv', index_col=0)
st.session_state.df = df_eval_newton_cot
st.session_state.user = uuid.uuid4()
st.session_state.start = True

st.write("# Welcome to VRECS Turing test! 👋")

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

    ### Score description:
    1 - Completely Meaningless: Indicates utter insignificance or lack of importance.
    2 - Mostly Meaningless: Implies minimal significance or relevance.
    3 - Beginning to Inform: Signifies the start of providing some information or significance.
    4 - Mostly Meaningful: Suggests considerable importance or relevance.
    5 - Completely Meaningful: Signifies utmost significance or profound relevance.

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
    #### Response 1:
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
    #### Response 1:
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


# st.markdown("""
#     ### Poor response example
#     **Score 1 👈**
#     > The request is to show each nationality and the number of pilots of each nationality.
#     > The dataset contains 5 columns:
#     > * `pilot_id`: the id of each pilot.
#     > * `pilot_name`: the name of each pilot.
#     > * `rank`: the rank of each pilot.
#     > * `age`: the age of each pilot.
#     > * `nationality`: the nationality of each pilot.
#     > * `position`: the position of each pilot.
#     > * `join_year`: the year when the pilot join the team.
#     > * `team`: the team that each pilot belong to.
#     """)

# st.markdown("""
#     ### Medium response example
#     **Score 2 👈**
#     > This visualization is a bar chart with two bars. The first bar shows the distribution of job_id, the second bar shows the sum of employee_id. The chart is sorted by the y axis from low to high.
#     > #### Insights: 
#     > There is a job_id with 60 employees. The sum of employee_id for this job_id is 60.
#     > #### Suggestions: 
#     > You can try to explore the dataset with the following queries:
#     > - Show the top 10 employees by their job_id and the sum of employee_id.
#     > - Show the top 10 departments by their job_id and the sum of employee_id.
#     """)

# st.markdown("""
#     ### Good response example
#     **Score 3 👈**
#     > Visualization explanation: 
#     > The 'name' and'manufacturer' columns are selected because the user wants to know the distribution of products across different manufacturers. The 'price' column is used to filter the data to only include products within a certain price range. The 'code' and 'name' columns are not selected as they do not provide the information the user is looking for.
#     > The visualization is a bar chart where the x-axis represents the 'Name' and the y-axis represents the 'Manufacturer'. There is no aggregation function applied. The data is filtered to only include prices between 60 and 120.
#     > Which manufacturer has the highest number of products priced between 60 and 120?; Are there any manufacturers that do not have any products priced between 60 and 120?
#     """)

if st.button("Start evaluating", type="primary"):
    switch_page("Evaluate")

