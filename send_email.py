import os
import smtplib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

from dotenv import load_dotenv

port = 465
EMAIL_SERVER ="smtp.gmail.com"

#load environment variables
current_dir = Path(__file__).resolve().parent if(__file__) in locals() else Path.cwd()
envars =current_dir /".env"
load_dotenv(envars)

#read environment variables
sender_email=os.getenv("EMAIL")
password_email=os.getenv("PASSWORD")

#message context 
def send_email(subject, reciever_email, name, Due_date, Invoice_no, amount):
        msg=EmailMessage()
        msg['Subject']=subject
        msg['From']=formataddr(("Coding is fun Corp.", f"{sender_email}"))
        msg["To"]=reciever_email
        msg["BCC"]=sender_email
        msg.set_context(
                
                    f"""/
            Subject: Service Expiry Reminder

            Dear {name},

            We hope you're enjoying your internet service from Sonitech Data Connections. This is a friendly reminder that your invoice for the {Package_Name} package will be due soon.
             Please settle the amount of {Amount} by {Due_Date} to ensure uninterrupted service.

            For any questions or assistance with payment, feel free to reach out to us.
            Note: This is a system-generated email. Please do not reply to this message.

            Thank you for choosing Sonitech Data Connections!

            Best regards,
            Sonitech Data Connections
            sonitechconnections@gmail.com

        """
)
        #html version 
        msg.add_alternative(
                f"""
                <html>
                <body>
                <p>Hi {name},</p>
                <p>Your account will expire on 2024-10-10. Please update your payment to continue enjoying our services.</p>
                <p> Note: This is a system-generated email. Please do not reply to this message.</p>
                <p>Best regards,</p>
                <p>Best regards,</p>
                <p>Best regards,</p>
                </body>
                </html>
""", 
subtype ='html',
        )
 
with smtplib.SMTP(EMAIL_SERVER, port) as server:
        server.starttls()
        server.login(sender_email, password_email)
        server.sendmail(sender_email, receiver_email, msg.as_string())

        if __name__ =="__main__":
                send_email(
        subject="Invoice Reminder",
        name="John doe",
        reciever_email="isaackaris.52@gmail.com",
        Due_date="11, Aug 2024",
        amount="ksh 1500",
)
send_email(
        subject="Invoice Reminder",
        name="John doe",
        reciever_email="yoxoc62272@advitize.com",
        Due_date="11, Aug 2024",
        amount="ksh 1500",
)