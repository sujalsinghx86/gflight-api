from flask import Flask
from flask import request
from api.scrapper import API

app = Flask(__name__)


def are_valid_query_params(query_params):
    required_params = ["oci", "oco", "dci", "dco", "dd"]

    try:
        for param in required_params:
            assert param in query_params.keys()
        return True
    except AssertionError:
        return False


@app.route("/")
def fetch_and_return_flights():
    params = request.args

    if are_valid_query_params(params):
        api = API(params)
        return {
            "status": "success",
            "tickets": api.get_data()
        }
    else:
        return {
            "status": "failure",
            "tickets": {}
        }


if __name__ == "__main__":
    app.run()
