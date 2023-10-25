import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import json

def load_previous_data(PREVIOUS_DATA_FILE,columns):
    try:
        return pd.read_csv(PREVIOUS_DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=columns)

def save_current_data(data,PREVIOUS_DATA_FILE,columns):
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(PREVIOUS_DATA_FILE, index=False)

def load_email_config(config_file):
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            return config.get("sender_email"), config.get("sender_password"), config.get("receiver_email")
    except FileNotFoundError:
        print(f"Config file '{config_file}' not found.")
        return None, None, None
    
email_config_file = "fundscraper/data/email_config_file.json"

# Load email configuration from JSON file
sender_email, sender_password, receiver_email = load_email_config(email_config_file)

def send_email(data, columns, x, PREVIOUS_DATA_FILE, email_subject):
    # Load previously scraped data
    previous_data = load_previous_data(PREVIOUS_DATA_FILE, columns)

    # Create a set of unique URLs from previous data
    previous_urls = set(previous_data[x])

    # Find new entries by comparing with previous data
    new_entries = [entry for entry in data if entry[x] not in previous_urls]

    if not new_entries:
        print("No new entries found. Email not sent.")
        return


    if sender_email is None or sender_password is None or receiver_email is None:
        print("Email configuration is incomplete. Email not sent.")
        return

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Create the HTML content of the email (same as before)
    html_content = f"""
    <html>
    <body>
        <h2>{email_subject}</h2>
        {pd.DataFrame(new_entries, columns=columns).to_html(index=False, escape=False)}
    </body>
    </html>
    """

    # Create the MIMEText object with HTML content (same as before)
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = email_subject
    message.attach(MIMEText(html_content, "html"))

    # Connect to the SMTP server and send the email (same as before)
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print("Error sending email:", str(e))