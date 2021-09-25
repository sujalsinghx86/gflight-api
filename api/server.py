from flask import Flask, request, json
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
        return app.response_class(status=200, mimetype="application/json", response=json.dumps({
            "status": "success",
            "tickets": API(params).get_data()
        }))
    else:
        return app.response_class(status=404, mimetype="application/json", response=json.dumps({
            "status": "failure",
            "tickets": []
        }))


if __name__ == "__main__":
    app.run()
