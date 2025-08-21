from O365 import Account

CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_SECRET_ID"
TENANT_ID = "YOUR_TENANT_ID"

credentials = (CLIENT_ID, CLIENT_SECRET)

def connect_outlook_onedrive():
    account = Account(credentials, auth_flow_type="credentials", tenant_id=TENANT_ID)
    if not account.is_authenticated:
        account.authenticate()
    return account

def fetch_file_from_onedrive(account, file_name):
    onedrive = account.storage()
    folder = onedrive.get_default_drive().get_root_folder()
    items = folder.get_items()
    for item in items:
        if item.name == file_name:
            local_path = f"./{file_name}"
            item.download(to_path=local_path)
            return local_path
    raise FileNotFoundError(f"{file_name} not found in OneDrive")
