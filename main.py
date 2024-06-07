import datetime
import pytz as pytz
from flask import Flask, request, jsonify, make_response

import config
app = Flask(__name__)
import mysql.connector

def validate_api(token):
    if token not in config.config['x-api-key']:
        return 401
def find_contact(email, phone_number, contacts):
    linkedItems = []
    returnObject = []
    for contact in contacts:
        if (contact["email"] == email or contact["phoneNumber"] == phone_number) and not contact["deletedAt"]:
            if contact['linkedId'] == None:
                returnObject.append(contact)
                linkedItems.append(contact['id'])
            elif contact['linkedId'] != None and contact['linkedId'] not in linkedItems:
                returnObject.append(contact)
    returnObject = sorted(returnObject, key=lambda x: x['id'])
    return returnObject
@app.route("/api/v1/identify", methods=["POST", "OPTIONS"])
def api_identify():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    elif request.method == "POST":
        # Check if API key present
        if 'Authorization' not in request.headers:
            return _corsify_actual_response(jsonify({'response': 'failure', 'message': 'API Key Required'})), 401

        # Check if API key is valid
        if validate_api(request.headers['Authorization'].split(' ')[1]) == 401:
            return _corsify_actual_response(jsonify({'response': 'failure', 'message': 'In-valid Token'})), 401
        try:
            event = request.get_json()

            # make sure all required fields are present
            if 'email' not in event:
                return _corsify_actual_response(jsonify({'response': 'failure', 'message': '"email" key is missing'})), 400
            if 'phoneNumber' not in event:
                return _corsify_actual_response(jsonify({'response': 'failure', 'message': '"phoneNumber" key is missing'})), 400
            if (event['email'] == None and event['phoneNumber'] == None) or (event['email'] == '' and event['phoneNumber'] == '') or (event['email'] == '' and event['phoneNumber'] == None) or (event['email'] == None and event['phoneNumber'] == ''):
                return _corsify_actual_response(jsonify({'response': 'failure', 'message': 'Email/Phone number is mandatory'})), 400
            if event['phoneNumber'] != None and event['phoneNumber'] != '' and type(event['phoneNumber']) != str:
                return _corsify_actual_response(jsonify({'response': 'failure', 'message': 'Phone Number must be of string'})), 400

            # database connection
            mydb = mysql.connector.connect(host=config.config['dbHost'], user=config.config['dbUser'], password=config.config['dbPassword'], database=config.config['dbName'])
            mycursor = mydb.cursor(dictionary=True)

            # initialize datetime with indian timezone
            datetime_now = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
            mycursor.execute("SELECT * FROM Contact")
            contactResponse = []

            # filter for duplicate checks
            isAlreadyPresent = False
            for cntc in mycursor.fetchall():
                contactResponse.append(cntc)
                if cntc['email'] == event['email'] and cntc['phoneNumber'] == event['phoneNumber']:
                    isAlreadyPresent = True

            toInsert = []
            toUpdate = []
            if event['email'] != None and event['email'] != '' and event['phoneNumber'] != None and event['phoneNumber'] != '' and isAlreadyPresent == False:
                existing_contact = find_contact(event['email'], event['phoneNumber'], contactResponse)

                # for new entry
                if len(existing_contact) == 0:
                    toInsert.append((event['phoneNumber'], event['email'], None, "primary", datetime_now,datetime_now, None))

                # email and phoneNumber from single primary linkPrecedence
                elif len(existing_contact) == 1:
                    if event['email'] != existing_contact[0]["email"]:
                        toInsert.append((existing_contact[0]["phoneNumber"], event['email'], existing_contact[0]["id"] if existing_contact[0]["linkPrecedence"] == 'primary' else existing_contact[0]['linkedId'], "secondary", datetime_now, datetime_now, None))
                    elif event['phoneNumber'] != existing_contact[0]["phoneNumber"]:
                        toInsert.append((event['phoneNumber'], existing_contact[0]["email"], existing_contact[0]["id"] if existing_contact[0]["linkPrecedence"] == 'primary' else existing_contact[0]['linkedId'], "secondary", datetime_now, datetime_now, None))

                # email and phoneNumber from two different primary linkPrecedence
                elif len(existing_contact) == 2:
                    toUpdate.append((existing_contact[0]["id"], 'secondary', datetime_now, existing_contact[1]["id"]))
                    for item in contactResponse:
                        if item['id'] == existing_contact[1]["id"]:
                            item['linkedId'] = existing_contact[0]["id"]
                            item['linkPrecedence'] = 'secondary'
                            item['updatedAt'] = datetime_now
                            break

            returnResponse = {
                "contact":{
                    "primaryContatctId": None,
                    "emails": [],
                    "phoneNumbers": [],
                    "secondaryContactIds": []
                }
            }
            # insert and update queries
            mycursor.executemany("INSERT INTO Contact (phoneNumber, email, linkedId, linkPrecedence, createdAt, updatedAt, deletedAt) VALUES (%s, %s, %s, %s, %s, %s, %s)", toInsert)
            mycursor.executemany("UPDATE Contact SET linkedId = %s, linkPrecedence = %s, updatedAt = %s WHERE id = %s", toUpdate)
            mydb.commit()

            # fetch all contacts with updated primary index (id column). Here SQL query is used to fetch proper data with proper IDs
            mycursor.execute("SELECT * FROM Contact")
            contactResponse = []
            for cntc in mycursor.fetchall():
                contactResponse.append(cntc)

            # construct return response
            for item in contactResponse:
                if item['linkPrecedence'] == 'primary':
                    returnResponse['contact']['primaryContatctId'] = item['id']
                    if item['email'] != None and item['email'] not in returnResponse['contact']:
                        returnResponse['contact']['emails'] = [item['email']] + returnResponse['contact']['emails']
                    if item['phoneNumber'] != None and item['phoneNumber'] not in returnResponse['contact']:
                        returnResponse['contact']['phoneNumbers'] = [item['phoneNumber']] + returnResponse['contact']['phoneNumbers']
                elif item['linkPrecedence'] == 'secondary':
                    if 'secondaryContactIds' not in returnResponse['contact']:
                        returnResponse['contact']['secondaryContactIds'] = []
                    returnResponse['contact']['secondaryContactIds'].append(item['id'])
                    if item['email'] != None and item['email'] not in returnResponse['contact']['emails']:
                        returnResponse['contact']['emails'].append(item['email'])
                    if item['phoneNumber'] != None and item['phoneNumber'] not in returnResponse['contact']['phoneNumbers']:
                        returnResponse['contact']['phoneNumbers'].append(item['phoneNumber'])
            mycursor.close()
            mydb.close()
            return _corsify_actual_response(jsonify(returnResponse)), 201
        except Exception as e:
            # store error in log and return 500
            print (e)
            return _corsify_actual_response(jsonify({'response': 'failure', 'message': 'Internal Server Error'})), 500
@app.route("/api/v1/health_check", methods=["GET", "OPTIONS"])
def api_health_check():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    elif request.method == "GET":
        return _corsify_actual_response(jsonify({'response': 'success'})), 201
@app.route("/api/v1/truncate", methods=["DELETE", "OPTIONS"])
def api_truncate():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    elif request.method == "DELETE":
        # Check if API key present
        if 'Authorization' not in request.headers:
            return _corsify_actual_response(jsonify({'response': 'failure', 'message': 'API Key Required'})), 401

        # Check if API key is valid
        if validate_api(request.headers['Authorization'].split(' ')[1]) == 401:
            return _corsify_actual_response(jsonify({'response': 'failure', 'message': 'In-valid Token'})), 401
        try:
            # database connection
            mydb = mysql.connector.connect(host=config.config['dbHost'], user=config.config['dbUser'], password=config.config['dbPassword'], database=config.config['dbName'])
            mycursor = mydb.cursor(dictionary=True)

            # truncate query
            mycursor.execute("TRUNCATE TABLE Contact")
            mydb.commit()
            mycursor.close()
            mydb.close()
            return _corsify_actual_response(jsonify({'response': 'success'})), 201
        except Exception as e:
            # store error in log and return 500
            print (e)
            return _corsify_actual_response(jsonify({'response': 'failure', 'message': 'Internal Server Error'})), 500


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
    app.run(host= '0.0.0.0',port=678, debug=True)
