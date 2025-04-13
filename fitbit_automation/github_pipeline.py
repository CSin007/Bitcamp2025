import requests
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from urllib.parse import quote_plus

load_dotenv()

# GitHub credentials
token = os.getenv("GITHUB_TOKEN")
owner = "CSin007"
author = "Arushitib"
repo = "Bitcamp2025"

# MongoDB setup
# Load credentials
MONGO_USERNAME = os.getenv("MONGODB_USERNAME")
MONGO_PASSWORD = quote_plus(os.getenv("MONGODB_PASSWORD"))
# MongoDB setup
uri = (
    f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}"
    "@ac-dlwqh3t-shard-00-00.11aamhq.mongodb.net:27017,"
    "ac-dlwqh3t-shard-00-01.11aamhq.mongodb.net:27017,"
    "ac-dlwqh3t-shard-00-02.11aamhq.mongodb.net:27017/"
    "?replicaSet=atlas-14od89-shard-0"
    "&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=Cluster0"
)
# Initialize client
mongo_client = MongoClient(
    uri,
    tls=True,
    tlsAllowInvalidCertificates=True,
    tlsAllowInvalidHostnames=True,
)
db = mongo_client["burnoutbuddy"]
collection = db["github_data"]

headers = {"Authorization": f"token {token}"}
url = f"https://api.github.com/repos/{owner}/{repo}/commits"

# Get commit count for last 5 days
commit_summary = []

for i in range(5, 0, -1):  # Days 5 to 1 ago
    day = datetime.now(timezone.utc) - timedelta(days=i)
    next_day = day + timedelta(days=1)

    params = {"author": author, "since": day.isoformat(), "until": next_day.isoformat()}

    response = requests.get(url, headers=headers, params=params)
    commits = response.json()

    commit_data = {"date": day.date().isoformat(), "commit_count": len(commits)}

    commit_summary.append(commit_data)

    # Upsert to MongoDB
    collection.update_one(
        {"date": commit_data["date"]}, {"$set": commit_data}, upsert=True
    )

# Print output
for entry in commit_summary:
    print(entry)

print("✅ GitHub commit data for last 5 days saved to MongoDB.")
