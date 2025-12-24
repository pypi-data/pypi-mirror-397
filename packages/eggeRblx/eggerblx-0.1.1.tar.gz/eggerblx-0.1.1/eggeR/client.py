import requests

BASE_URL = "https://users.roblox.com/v1/users/"

def get_user(user_id):
    response = requests.get(BASE_URL + str(user_id))
    response.raise_for_status()
    return response.json()