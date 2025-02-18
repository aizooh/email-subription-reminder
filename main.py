import os
from datetime import datetime
import pandas as pd
from send_email import send_email
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

class ReminderSystem:
    def __init__(self):
        self.sheet_id = os.getenv('SHEET_ID')
        self.sheet_name = 'new'
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.creds = None
        self.reminder_days = [5, 3, 1, 0]

    def get_spreadsheet_data(self):
        """Fetches data from the Google Spreadsheet."""
        url = f'https://docs.google.com/spreadsheets/d/{self.sheet_id}/gviz/tq?tqx=out:csv&sheet={self.sheet_name}'
        try:
            df = pd.read_csv(url, parse_dates=['Service expiry date:', 'Next_Reminder_Date', 'Last_Email_Sent'])
            return df
        except Exception as e:
            print(f"Error reading spreadsheet: {e}")
            return None

    def update_sheet(self, row_index, email_sent_date, next_reminder_date, days_to_expiry):
        """Updates the spreadsheet with email sent information."""
        try:
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', self.SCOPES)
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
                spreadsheetId=self.sheet_id, range=range_name,
                valueInputOption='RAW', body=body
            ).execute()

            print(f"Updated sheet for row {row_index+2}")
            return True

        except Exception as e:
            print(f"Error updating sheet: {e}")
            return False

    def process_reminders(self):
        """Processes reminders and sends emails."""
        df = self.get_spreadsheet_data()
        if df is None:
            return 0

        today = datetime.now().date()
        email_counter = 0

        for index, row in df.iterrows():
            expiry_date = row['Service expiry date:'].date()
            last_email_date = row['Last_Email_Sent'].date() if pd.notnull(row['Last_Email_Sent']) else None
            days_to_expiry = (expiry_date - today).days

            if days_to_expiry in self.reminder_days and (last_email_date is None or last_email_date != today):
                expiry_message = {
                    0: "SERVICE EXPIRES TODAY!",
                    1: "SERVICE EXPIRES TOMORROW!",
                    3: f"SERVICE EXPIRES IN {days_to_expiry} DAYS",
                    5: f"SERVICE EXPIRES IN {days_to_expiry} DAYS"
                }.get(days_to_expiry, "")

                success, _ = send_email(
                    to=row['Email Address:'], name=row['Name:'],
                    due_date=row['Service expiry date:'].strftime('%Y-%m-%d'),
                    invoice_no=row.get('Invoice_no', 'N/A'),
                    amount=row['Amount'], package_name=row['Package_Name'],
                    expiry_message=expiry_message
                )

                if success:
                    next_reminder_date = expiry_date.replace(year=expiry_date.year + (expiry_date.month == 12), month=(expiry_date.month % 12) + 1) if days_to_expiry == 0 else expiry_date
                    if self.update_sheet(index, today, next_reminder_date, days_to_expiry):
                        email_counter += 1
                        print(f"Processed {row['Name']}: {expiry_message}")

        return email_counter


def is_valid_day():
    """Check if today is between 1st and 15th OR 25th and 31st"""
    day = datetime.now().day
    return 1 <= day <= 15 or 25 <= day <= 31

def main():
    if not is_valid_day():
        print("Not in valid date range (1st-15th or 25th-31st). Skipping execution.")
        return

    reminder_system = ReminderSystem()
    emails_sent = reminder_system.process_reminders()
    print(f"Total emails sent: {emails_sent}")


if __name__ == "__main__":
    main()

print(f"Script running on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Day of month: {datetime.now().day}")
