import os
from datetime import datetime
import pandas as pd
from send_email import send_email
import openpyxl
from datetime import datetime, timedelta, time

# Get sheet ID from environment variable
sheet_id = "1oU-AA_OuxCNzotgE_QYvjXoyReNamvVSLpt2zXldPd0"
sheet_name = 'customer_info'

url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'

def load_df(url):
    parse_dates = ["Service expiry date:", "Reminder_date"]
    df = pd.read_csv(url, parse_dates=parse_dates)
    return df

# df = load_df(url)
# print(df)

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

def main():
    try:
        df = load_df(url)
        emails_sent = query_data_and_send_email(df)
        print(f"Total emails sent: {emails_sent}")
        
    except Exception as e:
        print(f"Error running script: {e}")

if __name__ == "__main__":
    main()