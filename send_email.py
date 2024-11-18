import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from email.utils import formataddr 

class GmailAPI:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        self.creds = None
        self.service = None

    def authenticate(self):
        """Handle the authentication process."""
        # Check if token.pickle exists
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        # If credentials are invalid or don't exist, create new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Save credentials for future use
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('gmail', 'v1', credentials=self.creds)
        return True

    def create_message(self, sender, to, subject, name, due_date, invoice_no, amount, package_name):
        """Create email message."""
        message = MIMEMultipart('alternative')
        message['to'] = to
        message['from'] = formataddr(("Sonitech Data Connections", sender))
        message['subject'] = subject
        message['bcc'] = sender

        # Plain text version
        text_content = f"""
        Subject: Service Expiry Reminder

        Dear {name},

        We hope you're enjoying your internet service from Sonitech Data Connections. This is a friendly reminder that your invoice for the {package_name} package will be due soon.
        Please settle the amount of {amount} by {due_date} to ensure uninterrupted service.

        For any questions or assistance with payment, feel free to reach out to us.
        Note: This is a system-generated email. Please do not reply to this message.

        Thank you for choosing Sonitech Data Connections!

        Best regards,
        Sonitech Data Connections
        sonitechconnections@gmail.com
        """

        # HTML version
        html_content = f"""
        <html>
        <body>
            <p>Dear {name},</p>
            
            <p>We hope you're enjoying your internet service from Sonitech Data Connections. This is a friendly reminder that your invoice 
            for the {package_name} package will be due soon.</p>
            
            <p>Please settle the amount of {amount} by {due_date} to ensure uninterrupted service.</p>
            
            <p>For any questions or assistance with payment, feel free to reach out to us.</p>
            <p><i>Note: This is a system-generated email. Please do not reply to this message.</i></p>
            
            <p>Thank you for choosing Sonitech Data Connections!</p>
            
            <p>Best regards,<br>
            Sonitech Data Connections<br>
            sonitechconnections@gmail.com</p>
        </body>
        </html>
        """

        # Attach both versions
        message.attach(MIMEText(text_content, 'plain'))
        message.attach(MIMEText(html_content, 'html'))

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}

    def send_email(self, sender, to, subject, name, due_date, invoice_no, amount, package_name):
        """Send email using Gmail API."""
        try:
            if not self.service:
                self.authenticate()

            message = self.create_message(
                sender, 
                to, 
                subject, 
                name, 
                due_date, 
                invoice_no, 
                amount, 
                package_name
            )
            
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            print(f'Message Id: {sent_message["id"]}')
            return True, sent_message['id']

        except Exception as e:
            print(f'An error occurred: {e}')
            return False, str(e)

# Example usage
def main():
    # Initialize the Gmail API handler
    gmail = GmailAPI()

    # Email
    sender = "sonitechconnections@gmail.com"  # Your Gmail address
    to = "isaackaris.52@gmail.com"
    subject = "Test Email from Gmail API"
    name = "John Doe"
    due_date = "2023-12-31"
    invoice_no = "INV12345"
    amount = "$100"
    package_name = "Premium"

    # Send email
    success, message = gmail.send_email(sender, to, subject, name, due_date, invoice_no, amount, package_name)
    
    if success:
        print("Email sent successfully!")
    else:
        print(f"Failed to send email: {message}")

if __name__ == '__main__':
    main()