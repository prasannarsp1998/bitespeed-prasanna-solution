# Bitespeed-solution by Prasanna Sundaram

## Problem Statement

The task is to create a web service with an endpoint /identify that accepts HTTP POST requests with JSON data containing an email and phone number. The service should respond with a JSON object containing the primary contact ID, email, phone number, and secondary contact IDs.
For detailed problem statement, refer to [Click Here](https://bitespeed.notion.site/Bitespeed-Backend-Task-Identity-Reconciliation-53392ab01fe149fab989422300423199)

## Solution
The solution is implemented using Python Flask and is available in the main.py file. The service is deployed on AWS EC2 with production configuration, and the endpoint is accessible at http://3.6.99.106/identify.


## Technologies Used
- Python Flask
- AWS EC2 with Ubuntu 22.04
- MySQL (Hosted in EC2)
- Nginx (for serving the API, hosted in EC2)

## How to Use
1. Install Postman or any other API testing tool. 
2. An API key is required and should be passed as a Bearer Token in the Authorization header with the key ```Authorization``` and value Bearer ```r3PJdg$j8>1d0n!d:B#Oh.2KAsiMO7/!!~ZH^Wn6lp+qW9Trkc```.
3. Send a POST request to http://3.6.99.106/identify with the JSON body as specified in the problem statement.
4. The response will be in JSON format as described in the problem statement.

## Features Covered
1. CORS enabled for the API.
2. DB credentials and API key stored in config file.
3. MySQL database installed on EC2 with remote user access.
4. Solution deployed on EC2 with Nginx for production configuration ([Tutorial](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-22-04)).
5. Basic request input validation is done in the code. 
6. The code is written in Python 3.8

## Credentials
1. AWS IAM credentials
   * URL - https://933032009873.signin.aws.amazon.com/console
   * Username - Bitespeed_Prasanna
   * Password - wI25G6{)
2. MySQL Credentials
   * IP - 3.6.99.106
   * Username - remote-user
   * Password - Th@!!11@m
   * Database - bitespeed