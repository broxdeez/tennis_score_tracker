import pandas as pd
import streamlit as st
from supabase import create_client
from datetime import datetime

st.title("Score Tracker 🎾")
st.caption("Enter scores separated by a space. e.g. 6 4 4 6 7 5")
cur_score = st.text_input("Enter scores..")
cur_score = [int(x) for x in cur_score.split()]
res = st.button("Submit")

current_dt = datetime.now().strftime("%Y-%m-%d")


# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase = init_connection()


# @st.cache_resource(ttl=600)
def run_query():
    return supabase.table("score_tracker").select("*").order("dt", desc=True).execute()


def insert_db(score):
    supabase.table("score_tracker").insert(
        {"dt": current_dt, "score": score},
    ).execute()


if res:
    insert_db(cur_score)


st.divider()
st.markdown(
    "<h1 style='text-align: center; color: grey;'>Past Matches</h1>",
    unsafe_allow_html=True,
)

rows = run_query()


def list_to_dataframe(lst):
    if len(lst) % 2 != 0:
        raise ValueError("List length must be even")

    odd_elements = lst[::2]
    even_elements = lst[1::2]

    df = pd.DataFrame([odd_elements, even_elements])
    df.index = ["Ahmad", "Bharath"]
    df.columns = ["SET_" + str(i) for i in range(1, len(df.columns) + 1)]

    return df


for row in rows.data:

    st.markdown(f"""`{row["dt"]}`""")
    st.dataframe(list_to_dataframe(row["score"]))
