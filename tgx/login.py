import json
import requests
import os


def main():
    url=os.environ['url_auth0']
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
                'Connection': 'Close'}

    client_id = os.environ['client_id']
    audience='https://api.travelgatex.com'
    grant_type='password'
    scope='openid'
    client_secret = os.environ['client_secret']

    username = input("username: ")
    password = input("password: ")

    body='client_id='+client_id + '&username='+username + '&password='+password + '&audience='+audience + '&grant_type='+grant_type + '&scope='+scope + '&client_secret='+client_secret


    response = requests.post(url,body,verify=True,headers=headers)
    response_json=json.loads(response.content.decode('utf-8'))
    print('\n\nBearer ' + response_json["id_token"]+'\n\n')
    print("Please keep in mind that this is NOT the token to input in the 'CONFIG' command")