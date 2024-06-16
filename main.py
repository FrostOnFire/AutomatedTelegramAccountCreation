import os
import requests
from dotenv import load_dotenv
from pyrogram import Client
import time
from smsactivate.api import SMSActivateAPI
import random

# Load environment variables from .env file
load_dotenv()

# Access environment variables
API_KEY = os.getenv("API_KEY")
TG_API_ID = os.getenv("TG_API_ID")
TG_API_HASH = os.getenv("TG_API_HASH")
COUNTRY_CODE = os.getenv("COUNTRY_CODE")
MAX_PRICE = float(os.getenv("MAX_PRICE"))

# Initialize the SMSActivateAPI
sa = SMSActivateAPI(API_KEY)
sa.debug_mode = True

# Load proxies from a file or define them directly
with open('proxies.txt', 'r') as file:
    proxies_list = [line.strip() for line in file]

# Ensure the sessions directory exists
if not os.path.exists('sessions'):
    os.makedirs('sessions')

def get_proxy():
    # Randomly select a proxy from the list
    proxy = random.choice(proxies_list)
    return {'http': proxy, 'https': proxy}

def get_number():
    response = sa.getNumber(service='tg', country=COUNTRY_CODE)
    print("Full API Response:", response)
    if 'activation_id' in response and 'phone' in response:
        activation_id = response['activation_id']
        phone_number = response['phone']
        print(f"Obtained number: {phone_number}")
        return activation_id, phone_number
    else:
        print("Failed to get a number: Missing 'activation_id' or 'phone' in response")
        return None, None

def get_sms(id, timeout=900):
    url = 'https://sms-activate.ru/stubs/handler_api.php'
    params = {'api_key': API_KEY, 'action': 'getStatus', 'id': id}
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = requests.get(url, params=params, proxies=get_proxy()).text
        print("[Debug] " + response)
        if "STATUS_OK" in response:
            return response.split(':')[1]
        elif "STATUS_WAIT_CODE" in response or "STATUS_WAIT_RESEND" in response:
            time.sleep(30)
        else:
            return None
    return None

def create_telegram_session(phone_number, phone_code, session_number):
    session_name = f"sessions/session_{session_number}"
    app = Client(session_name, api_id=TG_API_ID, api_hash=TG_API_HASH, phone_number=phone_number)
    app.connect()
    app.sign_in(phone_number)
    app.sign_in(code=phone_code)
    app.disconnect()
    print(f"Telegram session {session_number} created successfully.")

for i in range(2, 3):  # Example to create multiple accounts
    id, number = get_number()
    if id and number:
        sms_code = get_sms(id)
        if sms_code:
            create_telegram_session(number, sms_code, i)
            sa.setStatus(id=id, status=6)
        else:
            print("SMS retrieval failed.")
    else:
        print("Number acquisition failed.")