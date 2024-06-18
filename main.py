import os
import random
from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.errors import PhoneNumberUnoccupied, PhoneNumberBanned
import time
import threading
from smsactivate.api import SMSActivateAPI

# Load environment variables from .env file
load_dotenv(".env", override=True)
print("Country Code:", os.getenv("COUNTRY_CODE"))

# Access environment variables
API_KEY = os.getenv("API_KEY")
TG_API_ID = os.getenv("TG_API_ID")
TG_API_HASH = os.getenv("TG_API_HASH")
COUNTRY_CODE = os.getenv("COUNTRY_CODE")
MAX_PRICE = os.getenv("MAX_PRICE")
# Proxy configuration
PROXY = {
    "http": os.getenv("HTTP_PROXY"),
    "https": os.getenv("HTTPS_PROXY")
}
# Initialize the SMSActivateAPI without proxy support (modify internally if needed)
sa = SMSActivateAPI(API_KEY)  # Assuming modification to accept proxy
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

def get_sms(activation_id, timeout=180):
    start_time = time.time()
    while time.time() - start_time < timeout:
        status_response = sa.getStatus(id=activation_id)
        if 'STATUS_OK' in status_response:
            print("________________________________________________________________________________________________SMS Response:", sa.getFullSms(activation_id))
            return status_response.split(':')[1]
        elif 'STATUS_WAIT_CODE' in status_response or 'STATUS_WAIT_RESEND' in status_response:
            print(timeout - (time.time() - start_time), ": seconds left")
            time.sleep(10)
        else:
            cancel_number(activation_id=activation_id)
            return None
    cancel_number(activation_id=activation_id)
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
                delete_session(session_name=session_name)
                cancel_number(activation_id=activation_id)
                print("SMS retrieval failed.")
        else:
            delete_session(session_name=session_name)
            cancel_number(activation_id=activation_id)
            print("Failed to send verification code.")
    except Exception as e:
        delete_session(session_name=session_name)
        cancel_number(activation_id=activation_id)
        print(f"Failed to create session: {e}")
    finally:
        if connected:
            try:
                app.disconnect()
            except Exception as e:
                print("Failed to disconnect properly:", e)


def check_telegram_account(api_id, api_hash, phone_number):
    app = Client("my_account", api_id=api_id, api_hash=api_hash, phone_number=str(phone_number))
    try:
        app.connect()
        app.send_code(str(phone_number))
        print("An account exists for this number.")
        return True
    except PhoneNumberUnoccupied:
        print("No account exists for this number.")
        return False
    except PhoneNumberBanned:
        print("The phone number is banned on Telegram.")
        return False
    finally:
        app.disconnect()


def cancel_number(activation_id):
    def cancel():
        time.sleep(120)  # Wait for 2 minutes
        try:
            response = sa.setStatus(id=activation_id, status=8)  # Status 8 for canceling the number
            if response == "ACCESS_CANCEL":
                print("Number successfully canceled.")
            else:
                print("Failed to cancel the number.")
        except Exception as e:
            print(f"Error canceling the number: {e}")

    # Start the delay and cancellation in a separate thread
    thread = threading.Thread(target=cancel)
    thread.start()



def delete_session(session_name):
    session_path = session_name
    if os.path.exists(session_path):
        os.remove(session_path)
        print("Session file has been deleted successfully.")
    else:
        print("The session file does not exist.")


def check_balance():
    max_price = float(os.getenv("MAX_PRICE"))
    try:
        response = sa.getBalance()
        if 'balance' in response:
            balance = float(response['balance'])  # Assuming the balance key contains the balance amount
            if balance >= max_price:
                print(f"Balance is sufficient: {balance}")
                return True
            else:
                print(f"Balance is insufficient: {balance}, required: {max_price}")
                return False
        else:
            print("Balance data not found in response")
            return False
    except Exception as e:
        print(f"Error checking balance: {e}")
        return False




dailyAmount = 0
index = 0
while index < 5:  # This will allow for at least one attempt
    if dailyAmount == 99:
        time.sleep(86400)
    sufficient_funds = check_balance()
    if not sufficient_funds:
        print("waiting for 2 minutes")
        time.sleep(120)
        continue
    id, number = get_number()
    dailyAmount += 1
    if id and number:
        if check_telegram_account(TG_API_ID, TG_API_HASH, number):
            cancel_number(activation_id=id)
            print("Account already exists, obtaining a new number...")
            continue  # Skip to the next iteration to get a new number
        success = create_telegram_session(number, id, index + 1)
        if success:
            print("________________________________________________________________________________________________SUCCESS!")
            index += 1
        else:
            print("Session creation failed, retrying...")
    else:
        print("Number acquisition failed.")
        break