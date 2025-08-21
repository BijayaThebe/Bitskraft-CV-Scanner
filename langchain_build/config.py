import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

# Outlook / OneDrive
OUTLOOK_CLIENT_ID = os.getenv("OUTLOOK_CLIENT_ID")
OUTLOOK_CLIENT_SECRET = os.getenv("OUTLOOK_CLIENT_SECRET")
OUTLOOK_TENANT_ID = os.getenv("OUTLOOK_TENANT_ID")

# Google Drive
GDRIVE_SERVICE_ACCOUNT_PATH = os.getenv("GDRIVE_SERVICE_ACCOUNT_PATH")
