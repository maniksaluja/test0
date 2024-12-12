import requests
import json
import time

# Session to reuse connections
base = f'https://api.telegram.org/bot{BOT_TOKEN}/'
session = requests.Session()

# Function to handle retries
def make_request(url, retries=3, timeout=10):
    for _ in range(retries):
        try:
            response = session.get(url, timeout=timeout)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code} - Retrying...")
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e} - Retrying...")
        time.sleep(2)  # 2 seconds delay before retrying
    print("Error after retries.")
    return None

def getChatMember(chat_id, user_id):
    url = base + f'getChatMember?chat_id={chat_id}&user_id={user_id}'
    return make_request(url)

def sendMessage(chat_id, text, reply_markup=None):
    url = base + f'sendMessage?chat_id={chat_id}&text={text}'
    if reply_markup:
        url += f'&reply_markup={json.dumps(reply_markup)}'
    return make_request(url)

def editMessageText(chat_id, msg_id, text, reply_markup=None):
    url = base + f'editMessageText?chat_id={chat_id}&message_id={msg_id}&text={text}'
    if reply_markup:
        url += f'&reply_markup={json.dumps(reply_markup)}'
    return make_request(url)

def deleteMessage(chat_id, msg_id):
    url = base + f'deleteMessage?chat_id={chat_id}&message_id={msg_id}'
    response = make_request(url)
    if response is None:
        print("Failed to delete message.")

def sendDocument(chat_id, file_id):
    url = base + f'sendDocument?chat_id={chat_id}&document={file_id}'
    return make_request(url)

def sendVideo(chat_id, file_id):
    url = base + f'sendVideo?chat_id={chat_id}&video={file_id}'
    return make_request(url)

def sendPhoto(chat_id, photo, caption=None, reply_markup=None):
    url = base + f'sendPhoto?chat_id={chat_id}&photo={photo}'
    if caption:
        url += f'&caption={caption}'
    if reply_markup:
        url += f'&reply_markup={json.dumps(reply_markup)}'
    return make_request(url)

def editMessageCaption(chat_id, msg_id, caption, reply_markup=None):
    url = base + f'editMessageCaption?chat_id={chat_id}&message_id={msg_id}&caption={caption}'
    if reply_markup:
        url += f'&reply_markup={json.dumps(reply_markup)}'
    return make_request(url)
