import datetime
import pytz as pytz
from flask import Flask, request, jsonify, make_response

import config
import json
flask_app = Flask(__name__)
application = flask_app
import mysql.connector
import requests


if __name__ == '__main__':
    flask_app.run(host= '0.0.0.0',port=678, debug=True)
