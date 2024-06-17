import os
import random
from dotenv import load_dotenv
from pyrogram import Client
import time
from smsactivate.api import SMSActivateAPI

# Load environment variables from .env file
load_dotenv(".env", override=True)
print("Country Code:", os.getenv("COUNTRY_CODE"))

# Access environment variables
API_KEY = os.getenv("API_KEY")
TG_API_ID = os.getenv("TG_API_ID")
TG_API_HASH = os.getenv("TG_API_HASH")
COUNTRY_CODE = os.getenv("COUNTRY_CODE")

# Set up proxy for all requests
proxy_dict = {
    "http": "socks5://frostonfire8:yVzPZiJKuK@193.5.64.184:59101",
    "https": "socks5://frostonfire8:yVzPZiJKuK@193.5.64.184:59101"
}

# Initialize the SMSActivateAPI with proxy support
sa = SMSActivateAPI(API_KEY)
sa.debug_mode = True

# Load names from file
with open('names.txt', 'r') as file:
    names = [line.strip() for line in file if line.strip()]

# Ensure the sessions directory exists
if not os.path.exists('sessions'):
    os.makedirs('sessions')

def get_number():
    response = sa.getNumber(service='tg', country=COUNTRY_CODE)
    print("Full API Response:", response)
    if 'activation_id' in response and 'phone' in response:
        print(f"Obtained number: {response['phone']}")
        return response['activation_id'], response['phone']
    else:
        print("Failed to get a number: Missing 'activation_id' or 'phone' in response")
        return None, None

def get_sms(activation_id, timeout=900):
    start_time = time.time()
    while time.time() - start_time < timeout:
        status_response = sa.getStatus(id=activation_id)
        print("[Debug] Status Response:", status_response)
        if 'STATUS_OK' in status_response:
            return status_response.split(':')[1]
        elif 'STATUS_WAIT_CODE' in status_response or 'STATUS_WAIT_RESEND' in status_response:
            time.sleep(30)
        else:
            return None
    return None

def create_telegram_session(phone_number, activation_id, session_number):
    fullname = random.choice(names)  # random name
    first_name = fullname.split(' ')[0]
    last_name = fullname.split(' ')[1] if len(fullname.split(' ')) > 1 else ''
    session_name = f"sessions/session_{session_number}"
    phone_number = "+" + str(phone_number)
    app = Client(session_name, api_id=TG_API_ID, api_hash=TG_API_HASH, phone_number=phone_number)
    connected = False
    try:
        app.connect()
        connected = True
        sent_code = app.send_code(phone_number)
        if sent_code:
            phone_code_hash = sent_code.phone_code_hash
            sms_code = get_sms(activation_id)
            if sms_code:
                app.sign_up(phone_number=phone_number, phone_code_hash=phone_code_hash, phone_code=sms_code, first_name=first_name, last_name=last_name)
                print(f"Telegram session {session_number} created successfully.")
            else:
                print("SMS retrieval failed.")
        else:
            print("Failed to send verification code.")
    except Exception as e:
        print(f"Failed to create session: {e}")
    finally:
        if connected:
            try:
                app.disconnect()
            except Exception as e:
                print("Failed to disconnect properly:", e)

for i in range(1):  # Adjust the range as needed for multiple accounts
    id, number = get_number()
    if id and number:
        create_telegram_session(number, id, i + 1)
        sa.setStatus(id=id, status=6)  # Mark as complete
    else:
        print("Number acquisition failed.")