from flask_cors import CORS
from flask import Flask, jsonify
from pymongo import MongoClient
import os
import json
import re
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
    # genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    # # Choose a model
    # model = genai.GenerativeModel("gemini-2.0-flash")

    # # Ask a question
    # question = "What is the point of fatigue?"
    # response = model.generate_content(question)

    # # Print the answer
    # # print(response.text)

    return "Hello, world!"


# @app.route("/api/quotes")  # Define what happens at root URL
# def quotes():
#     genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
#     model = genai.GenerativeModel("gemini-2.0-flash")
#     question = "Generate a list of ten funny quotes about being burnt out and return it as a json object."
#     response = model.generate_content(question)

#     try:
#         # Convert response.text to a Python dict first
#         quote_data = json.loads(response.text)
#         return jsonify(quote_data)  # Sends real JSON with correct headers
#     except Exception as e:
#         return (
#             jsonify({"error": "Could not parse Gemini response", "details": str(e)}),
#             500,
#         )


@app.route("/api/quotes")
def quotes():
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")
    question = "Generate a list of ten funny quotes about being burnt out and return it as a json object."
    response = model.generate_content(question)

    raw_text = response.text.strip()

    # Remove Markdown code block wrapper
    if raw_text.startswith("```json"):
        raw_text = re.sub(r"```json\s*", "", raw_text)  # remove ```json
        raw_text = raw_text.replace("```", "").strip()  # remove ending ```

    try:
        quote_data = json.loads(raw_text)
        return jsonify(quote_data)
    except Exception as e:
        print("Failed to parse Gemini response:")
        print(repr(raw_text))
        return (
            jsonify({"error": "Could not parse Gemini response", "details": str(e)}),
            500,
        )


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
