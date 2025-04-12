# backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

CORS(app)  # Enable CORS for all routes


@app.route("/")  # Define what happens at root URL
def home():
    return "Hello, world!"


# how to make a simple API that returns JSON:
# @app.route("/api/capital", methods=["GET"])
# def get_capital():
#     country = request.args.get("country")
#     capitals = {"France": "Paris", "Spain": "Madrid"}
#     capital = capitals.get(country, "Not found")
#     return jsonify({"country": country, "capital": capital})


if __name__ == "__main__":
    app.run(debug=True)
