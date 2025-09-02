# email_sender.py
import win32com.client
import pythoncom
import streamlit as st
import pandas as pd
from datetime import datetime
import time
import os

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
    sender = OutlookEmailSender(sender_email)
    
    for index, candidate in top_candidates_df.iterrows():
        # Personalize the email content
        personalized_body = email_template['body'].format(
            candidate_name=candidate.get('Name', 'Candidate'),
            position=candidate.get('Position', 'the position'),
            company_name="Bitskraft"
        )
        
        personalized_subject = email_template['subject'].format(
            position=candidate.get('Position', 'Position')
        )
        
        # Send email
        success = sender.send_email(
            recipient_email=candidate['Email'],
            subject=personalized_subject,
            body=personalized_body
        )
        
        if success:
            successful_emails.append(candidate['Email'])
            # Add delay to avoid overwhelming Outlook
            time.sleep(2)
    
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