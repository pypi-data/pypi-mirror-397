import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import webbrowser
import pyautogui
import time
import random


def send_whats_msg(number: str, message: str):
    """
    Send a WhatsApp message via WhatsApp Web.

    Args:
        number (str): Phone number in international format, without '+'
        message (str): Text message to send
    """
    try:
        message = message.replace(" ", "%20")
        webbrowser.open(f"https://web.whatsapp.com/send?phone={number}&text={message}")
        print("WhatsApp Web has opened... Wait a moment for the download to complete")
        time.sleep(15)
        pyautogui.press("enter")
        print("Successfully send.")
    
    except Exception as e:
        print(f"Error: {e}")


def send_mail(email_sender: str, app_password: str, subject: str, body: str, email_receiver: str):
    """
    Send a plain text email.

    Args:
        email_sender (str): sender's email address
        app_password (str): sender's email password or app password
        subject (str): email subject
        body (str): email body (plain text)
        email_receiver (str): recipient's email address
    """
    msg = MIMEText(body, "plain", "utf-8")
    msg['Subject'] = subject
    msg['From'] =  email_sender
    msg['To'] = email_receiver
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as sender_email:
        sender_email.login(email_sender, app_password)
        sender_email.sendmail(email_sender, email_receiver, msg.as_string())


def send_html_mail(email_sender: str, app_password: str, subject: str, html_code: str, email_receiver: str):
    """
    Send a html email.

    Args:
        email_sender (str): sender's email address
        app_password (str): sender's email password or app password
        subject (str): email subject
        body (str): email body (plain text)
        email_receiver (str): recipient's email address
    """
    msg = MIMEText(html_code, "html", "utf-8")
    msg['Subject'] = subject
    msg['From'] =  email_sender
    msg['To'] = email_receiver
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as sender_email:
        sender_email.login(email_sender, app_password)
        sender_email.sendmail(email_sender, email_receiver, msg.as_string())


def send_mail_and_add_your_name(email_sender: str, app_password: str, you_email_name: str, subject: str, body: str, email_receiver: str):
    """
    Send an email in plain text and add your name to the outside of the message.

    Args:
        email_sender (str): sender's email address
        app_password (str): sender's email password or app password
        subject (str): email subject
        body (str): email body (plain text)
        email_receiver (str): recipient's email address
    """
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = formataddr((you_email_name, email_sender))
    msg['To'] = email_receiver
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as sender_email:
        sender_email.login(email_sender, app_password)
        sender_email.sendmail(email_sender, email_receiver, msg.as_string())
        
        
def generate_otp(length=6):
    """
    Generate a random OTP of given length.

    Args:
        type (int): Number of digits (default 6)
    """
    return random.randint(10**(length-1), 10**length - 1)


