from flask import Flask, request

app = Flask(__name__)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    print(f"\nPaste this code into your token exchange: \n{code}\n")
    return "Authorization code received. You can close this tab."

if __name__ == "__main__":
    app.run(port=8080)
