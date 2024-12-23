"""
Gmail API for Repository Notifications

This script sends emails to notify repository owners about build issues.
Uses Gmail API with OAuth 2.0 authentication.

Usage:
    1. Command line:
        python gmail_api.py owner_email repo_name repo_url
        Example: python gmail_api.py user@example.com my-repo https://github.com/user/my-repo

    2. Import as module:
        from gmail_api import main
        await main(owner_email="user@example.com", repo_name="my-repo", repo_url="https://github.com/user/my-repo")

    3. Testing (uses default values):
        python gmail_api.py

Note: Requires .env with Gmail API credentials and OAuth token.
"""

import os
from dotenv import load_dotenv
import asyncio
import sys
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pathlib
import time


async def main(owner_email=None, repo_name=None, repo_url=None):
    # Load environment variables
    load_dotenv()
    
    # Gmail API setup
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    # Create credentials from environment variables
    creds = Credentials(
        token=None,  # We'll use refresh token flow
        refresh_token=os.getenv('GMAIL_REFRESH_TOKEN'),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv('GMAIL_CLIENT_ID'),
        client_secret=os.getenv('GMAIL_CLIENT_SECRET'),
        scopes=SCOPES
    )

    # Try to refresh the credentials
    try:
        creds.refresh(Request())
    except Exception as e:
        print(f"Error refreshing credentials: {e}")
        return

    # Use command line arguments if no parameters provided
    if owner_email is None and len(sys.argv) > 1:
        owner_email = sys.argv[1]
    if repo_name is None and len(sys.argv) > 2:
        repo_name = sys.argv[2]
    if repo_url is None and len(sys.argv) > 3:
        repo_url = sys.argv[3]
    
    # Default values for testing if no arguments provided
    owner_email = owner_email or "test@example.com"
    repo_name = repo_name or "test-repo"
    repo_url = repo_url or "https://github.com/test-person/test-repo"

    # Create email content with timestamp
    current_time = datetime.now().strftime("%H:%M:%S")
    EMAIL_SUBJECT = f"your repo: {repo_name} can't be built"
    EMAIL_CONTENT = f"""
    Hey there,

    Your repository: {repo_name} can no longer be built! 
    We went ahead and fixed this for you. ❤️
    
    You can find the fixed repository here: {repo_url}

    Time: {current_time}

    Best regards,
    Grim Repo-r
    """

    # Create HTML content with font size 12
    HTML_CONTENT = f"""
    <html>
        <body style="font-family: Arial, sans-serif; font-size: 12pt;">
            <p>Hey there,</p>
            <p>Your repository: <b>{repo_name}</b> can no longer be built!</p>
            <p>We went ahead and fixed this for you. ❤️</p>
            <p>You can find the fixed repository here: <a href="{repo_url}">{repo_url}</a></p>
            <p>Time: {current_time}</p>
            <br>
            <p>Best regards,<br>Grim Repo-r</p>
        </body>
    </html>
    """

    # Create multipart message
    message = MIMEMultipart('alternative')
    message['to'] = owner_email
    message['subject'] = EMAIL_SUBJECT

    # Add plain text and HTML parts
    text_part = MIMEText(EMAIL_CONTENT, 'plain')
    html_part = MIMEText(HTML_CONTENT, 'html')
    
    message.attach(text_part)  # Plain text fallback
    message.attach(html_part)  # HTML version

    print("Waiting for 10 seconds before sending the email...")
    await asyncio.sleep(10)

    # Try to send email with error handling and rate limiting
    try:
        service = build('gmail', 'v1', credentials=creds)
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        print("Email sent successfully!")
        time.sleep(0.25)  # 250ms delay = ~240 emails per minute
    except Exception as e:
        print(f"Sadface homies. Error: {e}")

if __name__ == "__main__":
    # Run the script
    asyncio.run(main())
