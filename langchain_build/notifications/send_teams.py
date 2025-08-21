import requests

def send_teams_message(account, user_id, message):
    token = account.connection.get_access_token().get("access_token")
    url = f"https://graph.microsoft.com/v1.0/users/{user_id}/chats"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"body": {"content": message}}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
