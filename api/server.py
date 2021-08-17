from flask import Flask
from flask import request

app = Flask(__name__)


@app.route("/")
def fetch_and_return_flights():
    params = request.args
    return "hello world"


if __name__ == "__main__":
    app.run(debug=True)
