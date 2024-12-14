		
# UTILS

from datetime import datetime, timedelta
import random
import string
import requests

def send_sms(mobile,message):
    # Data for the POST request
    data = {
        'username': 'Aiims',
        'password': 'Aiims@123',
        'senderid': 'AIIMSD',
        'mobileNos': mobile,
        'message': message,
        'templateid1': '1307161579789431013'
    }

    # Headers for the POST request
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # URL of the service
    url = 'http://192.168.14.30/sms_service/Service.asmx/sendSingleSMS'

    # Send the POST request
    response = requests.post(url, data=data, headers=headers)

    # Return the response from the SMS service
    return response.status_code

def send_password_sms(mobile,password):
    return send_sms(mobile,f'your new password is {password}. Login to RPC waitinglist')

def send_OTP_sms(mobile,otp):
    # print("we are here")
    return 200
    # return send_sms(mobile,f'your new OTP is {otp}. Login to RPC waitinglist')


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

def send_ehospital_uhid(uhid):

    token = send_ehospital_init()

    if token == "":
        return None

    # Data for the POST request
    data = {
        'hospital_id': 4,
        'reg_no': uhid,
    }

    # Headers for the POST request
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    # URL of the service
    url = 'http://ehospitalapi.aiims.edu/patient/fetchPatientFullDetails'

    # Send the POST request
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200 or response.status_code == 201:
        response_data = response.json()
        # Get the token from the response
        patientDetails = response_data.get('patientDetails')
        # Return the response from the SMS service
        return patientDetails

    else:
        return ""

def to_date(date_string): 
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError('{} is not valid date in the format YYYY-MM-DD'.format(date_string))

def randomword(length):
	letters = 'abcdefghijklmnopqrstuvwxyz'
	return ''.join(random.choice(letters) for i in range(length))

def generate_random_phone_number():
    # Generate a random 10-digit number (excluding any specific formatting)
    number = ''.join(random.choices('0123456789', k=10))
    
    # Format the number as a typical phone number (e.g., ###-###-####)
    formatted_number = f'{number[:3]}-{number[3:6]}-{number[6:]}'
    
    return formatted_number

def generate_random_dob(start_date='1970-01-01', end_date='2005-12-31'):
    # Convert start_date and end_date to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Calculate the range in days
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    
    # Generate a random date within the specified range
    random_dob = start_date + timedelta(days=random_days)
    
    return random_dob.date()

def generate_strong_password(length=10):
	# Define characters to use in the password
	characters = string.ascii_letters + string.digits + string.punctuation
	
	# Generate password
	password = ''.join(random.choice(characters) for _ in range(length))
	
	return password


def randomOTP(length):
	letters = '0123456789'
	return ''.join(random.choice(letters) for i in range(length))