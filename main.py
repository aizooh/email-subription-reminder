import os
from datetime import datetime
import pandas as pd
from send_email import send_email
import openpyxl
from datetime import datetime, timedelta, time

# Get sheet ID from environment variable
sheet_id = os.getenv('SHEET_ID')
sheet_name = 'Copy of customer_info'

url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'

def load_df(url):
    parse_dates = ["Service expiry date:", "Reminder_date"]
    df = pd.read_csv(url, parse_dates=parse_dates)
    return df

def query_data_and_send_email(df):
    today = datetime.now().date()
    email_counter = 0
    
    for _, row in df.iterrows():
        # Calculate days until expiry
        expiry_date = row['Service expiry date:'].date()
        days_to_expiry = (expiry_date - today).days
        
        # Send email if it's 0, 1, 3, or 5 days before expiry
        if days_to_expiry in [0, 1, 3, 5]:
            success, _ = send_email(
               to=row['Email address'],
                name=row['Name'],
                due_date=row['Service expiry date:'].strftime('%Y-%m-%d'),
                invoice_no=row.get('Invoice_no', 'N/A'),
                amount=row['Amount'],
                package_name=row['Package_Name']
            )
            if success:
                print(f"Email sent to {row['Name']} ({days_to_expiry} days to expiry)")
                email_counter += 1
    
    return email_counter
def is_valid_day():
    """Check if today is between 25th and 15th"""
    day = datetime.now().day
    return 25 <= day <= 31 or 1 <= day <= 15

def main():
    if not is_valid_day():
        print("Not in valid date range (25th-15th). Skipping execution.")
        return

    sheet_id = os.getenv('SHEET_ID')
    sheet_name = 'sheet1'
    
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    
    try:
        df = load_df(url)
        emails_sent = query_data_and_send_email(df)
        print(f"Total emails sent: {emails_sent}")
        
    except Exception as e:
        print(f"Error running script: {e}")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    df = load_df(url)
    emails_sent = query_data_and_send_email(df)
    print(f"Total emails sent: {emails_sent}")

print(f"Script running on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Day of month: {datetime.now().day}")

import os
from datetime import datetime, timedelta
import pandas as pd
from send_email import send_email
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

class ReminderSystem:
    def __init__(self):
        self.sheet_id = os.getenv('SHEET_ID')
        self.sheet_name = 'customer_info'
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.creds = None
        self.reminder_days = [5, 3, 1, 0]  # Days before expiry to send reminders

    def calculate_next_month(self, current_date):
        """Move to next month while preserving the day"""
        if current_date.month == 12:
            next_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            next_date = current_date.replace(month=current_date.month + 1)
        return next_date

    def should_send_reminder(self, expiry_date, last_email_date):
        """Check if reminder should be sent based on days until expiry"""
        today = datetime.now().date()
        days_until_expiry = (expiry_date - today).days

        # If no email sent today and days match reminder schedule
        if days_until_expiry in self.reminder_days:
            if last_email_date is None or last_email_date != today:
                return True, days_until_expiry
        return False, days_until_expiry

    def update_sheet(self, row_index, email_sent_date, next_reminder_date, days_to_expiry):
        try:
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', self.SCOPES)
                    self.creds = flow.run_local_server(port=0)

            service = build('sheets', 'v4', credentials=self.creds)
            
            range_name = f'{self.sheet_name}!M{row_index+2}:O{row_index+2}'
            values = [[
                email_sent_date.strftime('%Y-%m-%d'),
                next_reminder_date.strftime('%Y-%m-%d'),
                f"{days_to_expiry} days to expiry"
            ]]
            
            body = {'values': values}
            service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"Updated sheet for row {row_index+2}")
            return True
            
        except Exception as e:
            print(f"Error updating sheet: {e}")
            return False

    def process_reminders(self):
        """Process reminders and update dates"""
        today = datetime.now().date()
        url = f'https://docs.google.com/spreadsheets/d/{self.sheet_id}/gviz/tq?tqx=out:csv&sheet={self.sheet_name}'
        
        try:
            df = pd.read_csv(url, parse_dates=['Service expiry date:', 'Next_Reminder_Date', 'Last_Email_Sent'])
            email_counter = 0
            
            for index, row in df.iterrows():
                expiry_date = row['Service expiry date:'].date()
                last_email_date = row['Last_Email_Sent'].date() if pd.notnull(row['Last_Email_Sent']) else None
                
                should_send, days_to_expiry = self.should_send_reminder(expiry_date, last_email_date)
                
                if should_send:
                    # Customize message based on days to expiry
                    expiry_message = {
                        0: "SERVICE EXPIRES TODAY!",
                        1: "SERVICE EXPIRES TOMORROW!",
                        3: f"SERVICE EXPIRES IN {days_to_expiry} DAYS",
                        5: f"SERVICE EXPIRES IN {days_to_expiry} DAYS"
                    }.get(days_to_expiry, "")

                    success, _ = send_email(
                        to=row['Email Address:'],
                name=row['Name:'],
                due_date=row['Service expiry date:'].strftime('%Y-%m-%d'),
                invoice_no=row.get('Invoice_no', 'N/A'),
                amount=row['Amount'],
                package_name=row['Package_Name'],
                        expiry_message=expiry_message
                    )
                    
                    if success:
                        # Calculate next month's date if this is the final reminder (0 days)
                        next_reminder_date = (
                            self.calculate_next_month(expiry_date) 
                            if days_to_expiry == 0 
                            else expiry_date
                        )
                        
                        if self.update_sheet(index, today, next_reminder_date, days_to_expiry):
                            email_counter += 1
                            print(f"Processed {row['Name']}: {expiry_message}")
            
            return email_counter
            
        except Exception as e:
            print(f"Error processing reminders: {e}")
            return 0

def main():
    reminder_system = ReminderSystem()
    emails_sent = reminder_system.process_reminders()
    print(f"Total emails sent: {emails_sent}")
