import streamlit as st
import pymongo
import openai

user = st.secrets["USER"]
password = st.secrets["PASSWORD"]
uri_url = st.secrets["URI_URL"]

uri = f"mongodb+srv://{user}:{password}@{uri_url}/?retryWrites=true&w=majority&appName=Cluster0"

# 1. Create mongo db connection
client = pymongo.MongoClient(uri)
db = client["valentine_tech"]
collection = db["responses"]

# 2. Auth with openai
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("Hacker spirit + valentines recommendation system")

st.divider()

st.image("https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimage.freepik.com%2Ffree-vector%2Fhand-drawn-valentine-s-day-penguins-couple_23-2148390371.jpg&f=1&nofb=1&ipt=1bc3afe7a7710f79006ea0810b3f5f62dda75dda3e29db6f12ddd4f3820dc79f&ipo=images")

st.subheader("Fill the questions below to get your techie match")

favorite_coffee = st.text_input("What is your favorite drink to order at a coffee shop?")
favorite_keycap = st.text_input("What is your keycap for a mechanical keyboard?")
programming_language = st.text_input("What is your favorite programming language?")
text_editor = st.text_input("What is your favorite code editor?")
favorite_snack = st.text_input("What is your favorite snack to munch while coding?")
favorite_browser = st.text_input("What is your favorite browser?")

if st.button("Submit"):
    # recommendation function
    st.success("Match has been found yei!")
else:
    st.warning("Please fill all of the question blanks")

