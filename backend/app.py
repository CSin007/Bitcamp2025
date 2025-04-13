from flask_cors import CORS
from flask import Flask, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import google.generativeai as genai
from urllib.parse import quote_plus

# Load environment variables from .env file
load_dotenv()

MONGO_USERNAME = os.getenv("MONGODB_USERNAME")
MONGO_PASSWORD = quote_plus(os.getenv("MONGODB_PASSWORD"))

app = Flask(__name__)
CORS(app)

uri = (
    f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}"
    "@ac-dlwqh3t-shard-00-00.11aamhq.mongodb.net:27017,"
    "ac-dlwqh3t-shard-00-01.11aamhq.mongodb.net:27017,"
    "ac-dlwqh3t-shard-00-02.11aamhq.mongodb.net:27017/"
    "?replicaSet=atlas-14od89-shard-0"
    "&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=Cluster0"
)

# Initialize client
client = MongoClient(
    uri,
    tls=True,
    tlsAllowInvalidCertificates=True,
    tlsAllowInvalidHostnames=True,
)
db = client["burnoutbuddy"]
collection = db["fitbit_data"]
collection2 = db["github_data"]


@app.route("/")  # Define what happens at root URL
def home():
    # Set up the API key
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    # Choose a model
    model = genai.GenerativeModel("gemini-2.0-flash")

    # Ask a question
    question = "What is the point of fatigue?"
    response = model.generate_content(question)

    # Print the answer
    # print(response.text)

    return response.text  # "Hello, world!"


@app.route("/api/fitbit/sleep")
def get_sleep_data():
    # Get the 5 most recent documents sorted by date descending
    docs = collection.find().sort("date", -1).limit(5)

    # Transform documents into a list of dicts
    result = []
    for doc in docs:
        result.append(
            {
                "date": doc.get("date"),
                "steps": doc.get("steps", 0),
                "totalMinutesAsleep": doc.get("totalMinutesAsleep", 0),
            }
        )

    return jsonify(result)


@app.route("/api/github/commits")
def get_github_commits():
    # Get the 5 most recent documents sorted by date descending
    docs = collection2.find().sort("date", -1).limit(5)

    # Transform documents into a list of dicts
    result = []
    for doc in docs:
        result.append(
            {
                "date": doc.get("date"),
                "commit_count": doc.get("commit_count", 0),
            }
        )

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
