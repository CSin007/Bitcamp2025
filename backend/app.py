from flask_cors import CORS
from flask import Flask, jsonify

app = Flask(__name__)
CORS(app)


@app.route("/")  # Define what happens at root URL
def home():
    return "Hello, world!"


if __name__ == "__main__":
    app.run(debug=True)
