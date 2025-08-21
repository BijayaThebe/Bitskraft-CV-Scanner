from connectors.outlook_onedrive import connect_outlook_onedrive, fetch_file_from_onedrive
from connectors.gdrive import connect_gdrive, upload_to_gdrive
from analysis.document_analysis import analyze_document
from analysis.pdf_writer import write_pdf
from notifications.send_outlook import send_outlook_mail
from notifications.send_teams import send_teams_message

def main():
    # STEP 1: Connect to Outlook/OneDrive
    account = connect_outlook_onedrive()

    # STEP 2: Fetch file from OneDrive
    file_path = fetch_file_from_onedrive(account, "input.txt")

    # STEP 3: Analyze file with LangChain + Sentence Transformers
    analysis_result = analyze_document(file_path)

    # STEP 4: Write analysis to PDF
    pdf_file = write_pdf(analysis_result)

    # STEP 5: Upload to OneDrive & Google Drive
    folder = account.storage().get_default_drive().get_root_folder()
    folder.upload_file(pdf_file)

    gdrive_service = connect_gdrive()
    gdrive_file_id = upload_to_gdrive(gdrive_service, pdf_file, "result.pdf")

    # STEP 6: Send Email with PDF
    send_outlook_mail(
        account,
        to="someone@example.com",
        subject="Document Analysis Result",
        body="Here is the analyzed document.",
        attachment_path=pdf_file,
    )

    # STEP 7: Send Teams message
    send_teams_message(account, user_id="USER_ID", message="Analysis done! Check OneDrive/Google Drive.")

    print("✅ Workflow Completed Successfully")

if __name__ == "__main__":
    main()
