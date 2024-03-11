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

st.write("# Welcome to NewtonLLM evaluation task! 👋")

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
    ## User Feedback on Visualizations

    Welcome! Your valuable feedback on visualizations is crucial for enhancing their effectiveness. Below are the steps to follow:

    ### Task Instructions:

    1. You will be presented with user utterance and corresponding datasets.
    2. For each question, three different visualization responses will be provided.
    3. Evaluate each visualization based on its clarity and effectiveness in conveying relevant information.
    4. **Assign a score between 1 and 3** for each visualization:
    - **1:** Poor
    - **2:** Fair
    - **3:** Excellent
    5. Your feedback will contribute to refining the quality of these visualizations.

    Thank you for your participation and dedication to improving visual communication!
    """
)

st.markdown("""
    ### Poor response example
    **Score 1 👈**
    > The request is to show each nationality and the number of pilots of each nationality.
    > The dataset contains 5 columns:
    > * `pilot_id`: the id of each pilot.
    > * `pilot_name`: the name of each pilot.
    > * `rank`: the rank of each pilot.
    > * `age`: the age of each pilot.
    > * `nationality`: the nationality of each pilot.
    > * `position`: the position of each pilot.
    > * `join_year`: the year when the pilot join the team.
    > * `team`: the team that each pilot belong to.
    """)

st.markdown("""
    ### Medium response example
    **Score 2 👈**
    > This visualization is a bar chart with two bars. The first bar shows the distribution of job_id, the second bar shows the sum of employee_id. The chart is sorted by the y axis from low to high.
    > #### Insights: 
    > There is a job_id with 60 employees. The sum of employee_id for this job_id is 60.
    > #### Suggestions: 
    > You can try to explore the dataset with the following queries:
    > - Show the top 10 employees by their job_id and the sum of employee_id.
    > - Show the top 10 departments by their job_id and the sum of employee_id.
    """)

st.markdown("""
    ### Good response example
    **Score 3 👈**
    > Visualization explanation: 
    > The 'name' and'manufacturer' columns are selected because the user wants to know the distribution of products across different manufacturers. The 'price' column is used to filter the data to only include products within a certain price range. The 'code' and 'name' columns are not selected as they do not provide the information the user is looking for.
    > The visualization is a bar chart where the x-axis represents the 'Name' and the y-axis represents the 'Manufacturer'. There is no aggregation function applied. The data is filtered to only include prices between 60 and 120.
    > Which manufacturer has the highest number of products priced between 60 and 120?; Are there any manufacturers that do not have any products priced between 60 and 120?
    """)

if st.button("Start evaluating", type="primary"):
    switch_page("Evaluate")

