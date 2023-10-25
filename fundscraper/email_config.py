import json
from getpass import getpass

# Collect email configuration
sender_email = input("Enter sender email: ")
sender_password = getpass("Enter sender password: ")
receiver_email = input("Enter receiver email: ")

# Load existing JSON data or create a new dictionary
try:
    with open('fundscraper/data/email_config_file.json', 'r') as config_file:
        config_data = json.load(config_file)
except FileNotFoundError:
    config_data = {}

# Update the dictionary with new values
config_data['sender_email'] = sender_email
config_data['sender_password'] = sender_password
config_data['receiver_email'] = receiver_email

# Write the updated data back to the JSON file
with open('fundscraper/data/email_config_file.json', 'w') as config_file:
    json.dump(config_data, config_file)
