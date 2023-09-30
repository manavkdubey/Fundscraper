import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

def load_previous_data(PREVIOUS_DATA_FILE,columns):
    try:
        return pd.read_csv(PREVIOUS_DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=columns)

def save_current_data(data,PREVIOUS_DATA_FILE,columns):
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(PREVIOUS_DATA_FILE, index=False)

def send_email(data,columns,x,PREVIOUS_DATA_FILE,email_subject):
    # Load previously scraped data
    previous_data = load_previous_data(PREVIOUS_DATA_FILE,columns)

    # Create a set of unique URLs from previous data
    previous_urls = set(previous_data[x])

    # Find new entries by comparing with previous data
    new_entries = [entry for entry in data if entry[x] not in previous_urls]

    if not new_entries:
        print("No new entries found. Email not sent.")
        return

    # Email configuration (same as before)
    sender_email = "dubeymanavkumar@gmail.com"
    sender_password = "yhcg wvpl yotu pngq"
    receiver_email = "dmanavkumar24@gmail.com"
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
