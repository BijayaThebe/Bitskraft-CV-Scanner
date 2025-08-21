from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/drive"]

def connect_gdrive(service_account_path="service-account.json"):
    creds = service_account.Credentials.from_service_account_file(
        service_account_path, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)
    return service

def upload_to_gdrive(service, file_path, file_name):
    file_metadata = {"name": file_name}
    media = MediaFileUpload(file_path, mimetype="application/pdf")
    file = service.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()
    return file.get("id")
