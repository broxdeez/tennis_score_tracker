from datetime import datetime

import pandas as pd
import streamlit as st
from supabase import create_client

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


for idx, row in enumerate(rows.data):
    st.markdown(f"""`{row["dt"]}`""")
    st.dataframe(list_to_dataframe(row["score"]))
    if st.button("Delete", key=idx):
        supabase.table("score_tracker").delete().eq("id", row["id"]).execute()
        st.rerun()

    # modal to update the score
    container = st.container()
    dialog = st.dialog("dialog_key_simplest_example")
    with dialog:
        st.write("### Enter updated score below:")
        upt_score = st.text_input("New Score:")
        upt_score = [int(x) for x in upt_score.split()]
        submitted = st.form_submit_button("Submit")
        if submitted:
            (
                supabase.table("score_tracker")
                .update({"score": upt_score})
                .eq("id", row["id"])
                .execute()
            )
            dialog.close()

    if st.button("Update", key="first_dialog_alert_button"):
        dialog.open()
