import streamlit as st
import pymongo
import openai
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from bson.binary import Binary

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

hacker_name = st.text_input("What is your name or discord username?")
favorite_coffee = st.text_input("What is your favorite drink to order at a coffee shop?")
favorite_keycap = st.text_input("What is your keycap for a mechanical keyboard?")
programming_language = st.text_input("What is your favorite programming language?")
text_editor = st.text_input("What is your favorite code editor?")
favorite_snack = st.text_input("What is your favorite snack to munch while coding?")
favorite_browser = st.text_input("What is your favorite browser?")
favorite_pizza_topping = st.text_input("What is your favorite pizza topping? (also chocolate is valid)")
hacker_description = st.text_area("Give us a short description about yourself, excluding your name")

# 3. Generate embeddings from openai model
def get_embedding(text):
    response = openai.embeddings.create(
    input=text,
    model="text-embedding-ada-002"
    )
    return response.data[0].embedding

# 4. Save responses in mongodb
def save_response(response, embedding):
    result = collection.insert_one({
        "responses": response,
        "embedding": Binary(pickle.dumps(embedding))
    })
    return result.inserted_id

# 5. Find match using cosine similarity math formula
def find_match(current_user_id, current_embedding):
    all_responses = list(collection.find())
    similarities = []

    for doc in all_responses:
        if doc['_id'] == current_user_id:
            continue
        stored_embedding = pickle.loads(doc["embedding"])
        similarity = cosine_similarity([current_embedding], [stored_embedding])[0][0]
        similarities.append((similarity, doc["responses"]))

    similarities.sort(reverse=True, key=lambda x:x[0])

    return similarities[0][1] if similarities else None

if st.button("Submit"):
    if hacker_name and favorite_coffee and favorite_keycap and programming_language and text_editor and favorite_snack and favorite_browser and favorite_pizza_topping and hacker_description:
        response = {
            "hacker_name": hacker_name,
            "favorite_coffee": favorite_coffee,
            "favorite_keycap": favorite_keycap,
            "programming_language": programming_language,
            "text_editor": text_editor,
            "favorite_snack": favorite_snack,
            "favorite_browser": favorite_browser,
            "favorite_pizza_topping": favorite_pizza_topping,
            "hacker_description": hacker_description 
        }

        # Generate embeddings
        responses_text = " ".join(response.values())
        actual_embedding = get_embedding(responses_text)

        # Add to mongodb
        current_user_id = save_response(response, actual_embedding)

        # Find match
        match = find_match(current_user_id, actual_embedding)

        if match:
            top_match, top_response = match[0]
            st.success(f"Match found! {match}")
        else:
            st.warning("You are the first person to be added to the system") 
else:
    st.warning("Please fill all of the question blanks")

