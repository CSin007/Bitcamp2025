from flask import Flask, request

app = Flask(__name__)


@app.route("/callback")
def callback():
    code = request.args.get("code")
    print(f"\nGot your Fitbit CODE:\n{code}\n")
    return "Success! You can close this tab now."


if __name__ == "__main__":
    app.run(port=8080)
