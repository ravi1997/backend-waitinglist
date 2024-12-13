import requests

def send_ehospital_init():
    # Data for the POST request
    
    url = 'https://ehospitalapi.aiims.edu/patient/init'
    headers = {'Content-Type': 'application/json'}
    data = {'username': 'rpcapi','password': 'Rpcapi@#123'}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200 or response.status_code == 201:
        response_data = response.json()
        # Get the token from the response
        token = response_data.get('token')
        # Return the response from the SMS service
        return token

    else:
        print(response.status_code)
        return ""
