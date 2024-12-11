import requests
import json

base = f'https://api.telegram.org/bot{BOT_TOKEN}/'

def getChatMember(chat_id, user_id):
    url = base + f'getChatMember?chat_id={chat_id}&user_id={user_id}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting chat member: {response.status_code}")
        return None

def sendMessage(chat_id, text, reply_markup=None):
    url = base + f'sendMessage?chat_id={chat_id}&text={text}'
    if reply_markup:
        url += f'&reply_markup={json.dumps(reply_markup)}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error sending message: {response.status_code}")
        return None

def editMessageText(chat_id, msg_id, text, reply_markup=None):
    url = base + f'editMessageText?chat_id={chat_id}&message_id={msg_id}&text={text}'
    if reply_markup:
        url += f'&reply_markup={json.dumps(reply_markup)}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error editing message text: {response.status_code}")
        return None

def deleteMessage(chat_id, msg_id):
    url = base + f'deleteMessage?chat_id={chat_id}&message_id={msg_id}'
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error deleting message: {response.status_code}")

def sendDocument(chat_id, file_id):
    url = base + f'sendDocument?chat_id={chat_id}&document={file_id}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error sending document: {response.status_code}")
        return None

def sendVideo(chat_id, file_id):
    url = base + f'sendVideo?chat_id={chat_id}&video={file_id}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error sending video: {response.status_code}")
        return None

def sendPhoto(chat_id, photo, caption=None, reply_markup=None):
    url = base + f'sendPhoto?chat_id={chat_id}&photo={photo}'
    if caption:
        url += f'&caption={caption}'
    if reply_markup:
        url += f'&reply_markup={json.dumps(reply_markup)}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error sending photo: {response.status_code}")
        return None

def editMessageCaption(chat_id, msg_id, caption, reply_markup=None):
    url = base + f'editMessageCaption?chat_id={chat_id}&message_id={msg_id}&caption={caption}'
    if reply_markup:
        url += f'&reply_markup={json.dumps(reply_markup)}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error editing message caption: {response.status_code}")
        return None
