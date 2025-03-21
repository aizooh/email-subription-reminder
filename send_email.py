import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import base64
from datetime import datetime

class GmailAPI:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        self.creds = None
        self.service = None

    def authenticate(self):
        """Handle the authentication process."""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)

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

        expiry_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        days_to_expiry = (expiry_date - datetime.now().date()).days

        # Create appropriate expiry message
        if days_to_expiry == 0:
            expiry_message = "YOUR SERVICE EXPIRES TODAY!"
        elif days_to_expiry == 1:
            expiry_message = "YOUR SERVICE EXPIRES TOMORROW!"
        elif days_to_expiry == 3:
            expiry_message = "YOUR SERVICE EXPIRES IN 3 DAYS!"
        elif days_to_expiry == 5:
            expiry_message = "YOUR SERVICE EXPIRES IN 5 DAYS!"
        else:
            expiry_message = f"YOUR SERVICE EXPIRES IN {days_to_expiry} DAYS!"

        # Plain text version
        text_content = f"""
        Subject: Service Expiry Reminder

        Dear {name},

        {expiry_message}

        We hope you're enjoying your internet service from <em><strong>Sonitech Connections.</strong></em> This is a friendly reminder that your invoice for the {package_name} package will be due soon.
        Please settle the amount of <strong>{amount}</strong> by <strong>{due_date}</strong> to ensure uninterrupted service.

        For any questions or assistance with payment, feel free to reach out to us.
        Please disregard this email if you have already settled your bill.
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
            
            <p style="color: red; font-weight: bold;">{expiry_message}</p>
            
            <p>We hope you're enjoying your internet service from Sonitech Connections. This is a friendly reminder that your invoice 
            for the {package_name} package will be due soon.</p>
            
            <p>Please settle the amount of <strong>{amount}</strong> by <strong>{due_date}</strong> to ensure uninterrupted service.</p>
            
            <p>For any questions or assistance with payment, feel free to reach out to us.</p>
            <p>Please disregard this email if you have already settled your bill.</p>
            <p><i>Note: This is a system-generated email. Please do not reply to this message.</i></p>
            
            <p>Thank you for choosing Sonitech Connections!</p>
            
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

# Create an instance of GmailAPI
gmail_api = GmailAPI()

# Create the send_email function that main.py will import
def send_email(to, name, due_date, invoice_no, amount, package_name):
    sender = "sonitechconnections@gmail.com"
    subject = "Service Expiry Reminder"
    
    success, message = gmail_api.send_email(
        sender=sender,
        to=to,
        subject=subject,
        name=name,
        due_date=due_date,
        invoice_no=invoice_no,
        amount=amount,
        package_name=package_name
    )
    return success, message

# Example usage
if __name__ == '__main__':
    # Test the function
    success, message = send_email(
        to="isaackaris.52@gmail.com",
        name="John Doe",
        due_date="2024-12-31",
        invoice_no="INV12345",
        amount="KES 5,000",
        package_name="Premium Package"
    )
    
    if success:
        print("Email sent successfully!")
    else:
        print(f"Failed to send email: {message}")