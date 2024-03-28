import datetime
import pytz as pytz
from flask import Flask, request, jsonify, make_response

import config
import json
flask_app = Flask(__name__)
application = flask_app
import mysql.connector
import requests

def validate_api(token):
    if token not in config.config['x-api-key']:
        return 401

@flask_app.route("/api/v1/identify", methods=["POST", "OPTIONS"])
def api_allapplications_insert():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    elif request.method == "POST":
        # Check if API key present
        if 'Authorization' not in request.headers:
            return _corsify_actual_response(jsonify({'response': 'failure', 'message': 'API Key Required'})), 401

        # Check if API key is valid
        if validate_api(request.headers['Authorization'].split(' ')[1]) == 401:
            return _corsify_actual_response(jsonify({'response': 'failure', 'message': 'In-valid Token'})), 401


        return _corsify_actual_response(jsonify({'response': 'success'})), 201


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == '__main__':
    flask_app.run(host= '0.0.0.0',port=678, debug=True)
