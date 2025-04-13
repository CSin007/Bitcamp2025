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
    env_path = ".env"

    # Read existing lines
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # Update lines if keys found
    for i, line in enumerate(lines):
        if line.startswith("FITBIT_ACCESS_TOKEN="):
            lines[i] = f"FITBIT_ACCESS_TOKEN={ACCESS_TOKEN}\n"
            found_access = True
        elif line.startswith("FITBIT_REFRESH_TOKEN="):
            lines[i] = f"FITBIT_REFRESH_TOKEN={REFRESH_TOKEN}\n"
            found_refresh = True

    # Append if not found
    if not found_access:
        lines.append(f"FITBIT_ACCESS_TOKEN={ACCESS_TOKEN}\n")
    if not found_refresh:
        lines.append(f"FITBIT_REFRESH_TOKEN={refresh_token}\n")

    # Write back to .env
    with open(env_path, "w") as f:
        f.writelines(lines)
    print("Tokens updated in .env file.")
    print("Access token:", ACCESS_TOKEN)
    print("Refresh token:", REFRESH_TOKEN)

    print("Token refreshed.")
    return True


def get_day_data(target_date):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    steps_url = (
        f"https://api.fitbit.com/1/user/-/activities/steps/date/{target_date}/1d.json"
    )
    sleep_url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{target_date}.json"

    steps_res = requests.get(steps_url, headers=headers)
    sleep_res = requests.get(sleep_url, headers=headers)

    if steps_res.status_code == 401 or sleep_res.status_code == 401:
        if refresh_token():
            return get_day_data(target_date)
        else:
            return None

    steps_data = steps_res.json()
    sleep_data = sleep_res.json()

    try:
        step_count = int(steps_data["activities-steps"][0]["value"])
    except (KeyError, IndexError):
        step_count = 0

    try:
        total_sleep = sum(
            entry["minutesAsleep"] for entry in sleep_data.get("sleep", [])
        )
    except Exception:
        total_sleep = 0

    return {"date": target_date, "steps": step_count, "totalMinutesAsleep": total_sleep}


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
    print("Fetching Fitbit data for last 5 days...")
    today = date.today()
    all_days = []

    for offset in range(1, 6):  # Days 1 to 5 ago
        d = (today - timedelta(days=offset)).isoformat()
        day_data = get_day_data(d)
        if day_data:
            collection.update_one(
                {"date": day_data["date"]}, {"$set": day_data}, upsert=True
            )
            all_days.append(day_data)

    print("Inserted/Updated entries for last 5 days:")
    for entry in all_days:
        print(entry)


if __name__ == "__main__":
    main()
