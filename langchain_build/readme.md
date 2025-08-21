project/
│── .env                      # All your API keys and secrets
│── main.py                    # Entry point to run the workflow
│── config.py                  # Loads .env variables securely
|__ Readme.md                 # Necessary informations
│
├── connectors/
│    ├── __init__.py
│    ├── outlook_onedrive.py  # Functions to connect/fetch files from Outlook & OneDrive
│    └── gdrive.py             # Functions to connect/upload to Google Drive
│
├── analysis/
│    ├── __init__.py
│    ├── document_analysis.py  # LangChain + embeddings analysis
│    └── pdf_writer.py         # Write analysis results to PDF
│
└── notifications/
     ├── __init__.py
     ├── send_outlook.py       # Send emails via Outlook
     └── send_teams.py         # Send messages via Microsoft Teams
