from flask_cors import CORS
from flask import Flask, jsonify, request
from pymongo import MongoClient
import subprocess
import signal
import os
import json
from burnout_calculator import calculate_burnout
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
camera_process = None  # global process handle

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


@app.route("/api/toggle-camera", methods=["POST"])
def toggle_camera():
    global camera_process

    action = request.json.get("action")
    if action == "start" and camera_process is None:
        camera_process = subprocess.Popen(["python", "burnout_buddy_eye_tracker.py"])
        return jsonify({"status": "started"})
    elif action == "stop" and camera_process is not None:
        camera_process.terminate()
        camera_process = None
        return jsonify({"status": "stopped"})
    return jsonify({"status": "noop"})


@app.route("/api/burnout", methods=["GET"])
def get_burnout_score():
    try:
        # 1. Pull last 5 fitbit entries
        fitbit_data = list(db["fitbit_data"].find().sort("date", -1).limit(5))
        steps = [entry["steps"] for entry in reversed(fitbit_data)]
        sleep = [entry["totalMinutesAsleep"] for entry in reversed(fitbit_data)]

        # 2. Pull last 5 github commits
        github_data = list(db["github_data"].find().sort("date", -1).limit(5))
        commits = [entry["commit_count"] for entry in reversed(github_data)]

        # 3. Get latest fatigue score
        fatigue_score = 5  # fallback
        if os.path.exists("latest_score.json"):
            with open("latest_score.json") as f:
                data = json.load(f)
                fatigue_score = float(data.get("average_drowsiness", 5))

        # 4. Calculate burnout
        score = calculate_burnout(steps, sleep, commits, fatigue_score)
        return jsonify(
            {
                "burnout_score": score,
                "steps": steps,
                "sleep": sleep,
                "commits": commits,
                "fatigue_score": fatigue_score,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
