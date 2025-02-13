import streamlit as st
import pymongo
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from bson.binary import Binary
import pickle
import streamlit as st

user = st.secrets["USER"]
password = st.secrets["PASSWORD"]
uri_url = st.secrets["URI_URL"]

uri = f"mongodb+srv://{user}:{password}@{uri_url}/?retryWrites=true&w=majority&appName=Cluster0"

# MongoDB connection
client = pymongo.MongoClient(uri)
db = client["techie_matcher"]
collection = db["responses"]

# OpenAI API key for embeddings (replace with your own API key)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Streamlit interface
st.title("Hacker Spirit + Valentine's Recommendation System")
st.divider()
st.image("https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimage.freepik.com%2Ffree-vector%2Fhand-drawn-valentine-s-day-penguins-couple_23-2148390371.jpg&f=1&nofb=1&ipt=1bc3afe7a7710f79006ea0810b3f5f62dda75dda3e29db6f12ddd4f3820dc79f&ipo=images")

st.subheader("Fill the questions below to get your techie match")

name = st.text_input("What is your name?")
favorite_coffee = st.text_input("What is your favorite drink to order at a coffee shop?")
favorite_keycap = st.text_input("What is your keycap for a mechanical keyboard?")
programming_language = st.text_input("What is your favorite programming language?")
text_editor = st.text_input("What is your favorite code editor?")
favorite_snack = st.text_input("What is your favorite snack to munch while coding?")
favorite_browser = st.text_input("What is your favorite browser?")

def get_embedding(text):
    # Get the embedding for the response from OpenAI API (you can use other models as well)
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def save_response_to_db(responses, embedding):
    result = collection.insert_one({
        "responses": responses,
        "embedding": Binary(pickle.dumps(embedding))  # Store embeddings as binary
    })
    return result.inserted_id 


def find_match(current_embedding, current_user_id):
    all_responses = list(collection.find())
    similarities = []

    for doc in all_responses:
        if doc['_id'] == current_user_id:
            continue
        
        stored_embedding = pickle.loads(doc['embedding'])
        similarity = cosine_similarity([current_embedding], [stored_embedding])[0][0]
        similarities.append((similarity, doc['responses']))

    # Sort by similarity (highest first)
    similarities.sort(reverse=True, key=lambda x: x[0])
    
    return similarities[0][1] if similarities else None


if st.button("Submit"):
    if favorite_coffee and favorite_keycap and programming_language and text_editor and favorite_snack and favorite_browser:
        # Combine answers into one string
        responses = {
            "name": name,
            "favorite_coffee": favorite_coffee,
            "favorite_keycap": favorite_keycap,
            "programming_language": programming_language,
            "text_editor": text_editor,
            "favorite_snack": favorite_snack,
            "favorite_browser": favorite_browser
        }

        # Generate embeddings for the responses
        responses_text = " ".join(responses.values())
        current_embedding = get_embedding(responses_text)

        # Save the response to MongoDB along with the embedding
        current_user_id = save_response_to_db(responses, current_embedding)

        # Find a match based on similarity
        match = find_match(current_embedding, current_user_id)

        if match:
            top_match_similarity, top_match_responses = match[0]
            st.success(f"Match found! Here's someone similar to you: {match}")
            st.write(f"Similarity score: {top_match_similarity}")
        else:
            st.warning("No matches found. Be the first to enter the system!")
    else:
        st.warning("Please fill all of the question blanks")

