# downloader.py
import os
import win32com.client
import pythoncom
import streamlit as st
import pandas as pd
from datetime import datetime
import time

class OutlookCVFetcher:
    def __init__(self, email_account, parser=None, analyzer=None, save_dir=None):
        self.email_account = email_account
        self.save_dir = save_dir or r"set your path"
        self.parser = parser
        self.analyzer = analyzer

        # Create directory if not exists
        os.makedirs(self.save_dir, exist_ok=True)

    def process_jobbox(self):  # ← Must be exactly this name
        pythoncom.CoInitialize()
        try:
            outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
            account = outlook.Folders[self.email_account]
            jobbox = account.Folders["JobBox"]

            messages = jobbox.Items
            print(f"📬 Found {messages.Count} emails in JobBox")

            for msg in messages:
                try:
                    # Add None checks for message properties
                    if msg is None:
                        continue
                        
                    # Check if message has attachments
                    if not hasattr(msg, 'Attachments') or msg.Attachments is None:
                        continue
                        
                    attachments = msg.Attachments
                    for attachment in attachments:
                        if attachment is None or not hasattr(attachment, 'FileName'):
                            continue
                            
                        if attachment.FileName.lower().endswith(".pdf"):
                            # Sanitize filename
                            safe_name = "".join(c for c in attachment.FileName if c.isalnum() or c in "._- ")
                            if not safe_name:
                                safe_name = f"cv_{hash(attachment.FileName)}.pdf"

                            save_path = os.path.join(self.save_dir, safe_name)

                            # Avoid overwriting
                            base, ext = os.path.splitext(save_path)
                            counter = 1
                            while os.path.exists(save_path):
                                save_path = f"{base}_{counter}{ext}"
                                counter += 1

                            # Save attachment
                            attachment.SaveAsFile(save_path)
                            print(f"✅ Saved: {save_path}")

                            # Optional: Parse with better error handling
                            if self.parser:
                                try:
                                    parsed_data = self.parser.parse(save_path)
                                    # Add None check for parsed data
                                    if parsed_data is not None:
                                        print(f"📄 Parsed: {parsed_data}")
                                    else:
                                        print(f"⚠️ Parse returned None for: {save_path}")
                                except Exception as e:
                                    print(f"⚠️ Parse failed: {e}")

                except Exception as e:
                    print(f"❌ Error processing message: {e}")

        except Exception as e:
            print(f"❌ Failed to connect to Outlook: {e}")
        finally:
            pythoncom.CoUninitialize()

class OutlookEmailSender:
    def __init__(self, email_account):
        self.email_account = email_account
    
    def send_email(self, recipient_email, subject, body, html_body=None, attachment_path=None):
        """
        Send email using Outlook desktop application
        
        Args:
            recipient_email (str): Email address of the recipient
            subject (str): Email subject
            body (str): Plain text email body
            html_body (str, optional): HTML formatted email body
            attachment_path (str, optional): Path to attachment file
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        # Add input validation
        if not recipient_email or not subject or not body:
            st.error("Missing required email fields")
            return False
            
        pythoncom.CoInitialize()
        try:
            # Create Outlook application instance
            outlook = win32com.client.Dispatch("Outlook.Application")
            
            # Create a new mail item
            mail = outlook.CreateItem(0)  # 0 = olMailItem
            
            # Set email properties
            mail.To = recipient_email
            mail.Subject = subject
            
            # Use HTML body if provided, otherwise plain text
            if html_body:
                mail.HTMLBody = html_body
            else:
                mail.Body = body
            
            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                mail.Attachments.Add(attachment_path)
            
            # Send the email
            mail.Send()
            
            return True
            
        except Exception as e:
            st.error(f"Error sending email to {recipient_email}: {str(e)}")
            return False
        finally:
            pythoncom.CoUninitialize()

def send_bulk_emails(top_candidates_df, email_template, sender_email):
    """
    Send emails to top candidates
    
    Args:
        top_candidates_df (DataFrame): DataFrame containing top candidates
        email_template (dict): Template for email content
        sender_email (str): Your email address for the sender field
    
    Returns:
        list: List of emails that were sent successfully
    """
    successful_emails = []
    
    # Add None checks for inputs
    if top_candidates_df is None or top_candidates_df.empty:
        st.error("No candidates data provided")
        return successful_emails
        
    if not email_template or not sender_email:
        st.error("Missing email template or sender email")
        return successful_emails
    
    sender = OutlookEmailSender(sender_email)
    
    for index, candidate in top_candidates_df.iterrows():
        try:
            # Add None checks for candidate data
            candidate_name = candidate.get('Name', 'Candidate') if candidate.get('Name') is not None else 'Candidate'
            position = candidate.get('Position', 'the position') if candidate.get('Position') is not None else 'the position'
            candidate_email = candidate.get('Email')
            
            # Skip if no email
            if not candidate_email or pd.isna(candidate_email):
                print(f"⚠️ Skipping candidate {candidate_name} - no email address")
                continue
            
            # Personalize the email content
            personalized_body = email_template['body'].format(
                candidate_name=candidate_name,
                position=position,
                company_name="Bitskraft"
            )
            
            personalized_subject = email_template['subject'].format(
                position=position
            )
            
            # Send email
            success = sender.send_email(
                recipient_email=candidate_email,
                subject=personalized_subject,
                body=personalized_body
            )
            
            if success:
                successful_emails.append(candidate_email)
                print(f"✅ Email sent to: {candidate_email}")
                # Add delay to avoid overwhelming Outlook
                time.sleep(2)
            else:
                print(f"❌ Failed to send email to: {candidate_email}")
                
        except Exception as e:
            print(f"❌ Error processing candidate {index}: {e}")
            continue
    
    return successful_emails

# Default email template
DEFAULT_EMAIL_TEMPLATE = {
    'subject': "Congratulations! Next Steps for {position} Position at Bitskraft",
    'body': """Dear {candidate_name},

We are impressed with your qualifications and would like to invite you to the next stage of our hiring process for the {position} position at {company_name}.

Your application stood out among many others, and we believe your skills and experience would be a valuable addition to our team.

Next Steps:
1. We will contact you within 2 business days to schedule an interview
2. Please be prepared to discuss your experience in more detail
3. We may conduct a technical assessment based on the role requirements

If you have any questions in the meantime, please don't hesitate to reach out.

Best regards,
The Bitskraft Hiring Team"""
}