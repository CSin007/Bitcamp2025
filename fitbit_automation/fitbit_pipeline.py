import os
import base64
import requests
from datetime import date, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

# Load credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("FITBIT_ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("FITBIT_REFRESH_TOKEN")
MONGO_USERNAME = os.getenv("MONGODB_USERNAME")
MONGO_PASSWORD = quote_plus(os.getenv("MONGODB_PASSWORD"))
# MONGO_CLUSTER = os.getenv("MONGO_CLUSTER")

# MongoDB setup
# uri = (
#     f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}"
#     "@cluster0.ph7revd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# )
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

collection = db["fitbit_data"]


# Token refresh helper
def refresh_token():
    global ACCESS_TOKEN, REFRESH_TOKEN
    print("Refreshing Fitbit token...")

    b64_auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN}

    res = requests.post(
        "https://api.fitbit.com/oauth2/token", headers=headers, data=data
    )
    if res.status_code != 200:
        print("Failed to refresh token.")
        print(res.text)
        return False

    tokens = res.json()
    ACCESS_TOKEN = tokens["access_token"]
    REFRESH_TOKEN = tokens["refresh_token"]

    # Save back to .env (optional, or save to DB/file)
    with open(".env", "r") as f:
        lines = f.readlines()
    with open(".env", "w") as f:
        for line in lines:
            if line.startswith("FITBIT_ACCESS_TOKEN="):
                f.write(f"FITBIT_ACCESS_TOKEN={ACCESS_TOKEN}\n")
            elif line.startswith("FITBIT_REFRESH_TOKEN="):
                f.write(f"FITBIT_REFRESH_TOKEN={REFRESH_TOKEN}\n")
            else:
                f.write(line)

    print("Token refreshed.")
    return True


# API call helper
def get_fitbit_data():
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    # Steps
    steps_url = (
        f"https://api.fitbit.com/1/user/-/activities/steps/date/{yesterday}/1d.json"
    )
    steps_res = requests.get(steps_url, headers=headers)

    # Sleep
    sleep_url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{yesterday}.json"
    sleep_res = requests.get(sleep_url, headers=headers)

    if steps_res.status_code == 401 or sleep_res.status_code == 401:
        # Unauthorized → refresh token and retry
        if refresh_token():
            return get_fitbit_data()
        else:
            return None, None

    return steps_res.json(), sleep_res.json()


# Run the pipeline
def main():
    print("Fetching Fitbit data...")
    steps, sleep = get_fitbit_data()

    if steps and sleep:
        doc = {
            "date": (date.today() - timedelta(days=1)).isoformat(),
            "steps": steps,
            "sleep": sleep,
        }
        collection.insert_one(doc)
        print("Data inserted into MongoDB.")
    else:
        print("Could not fetch Fitbit data.")


if __name__ == "__main__":
    main()
