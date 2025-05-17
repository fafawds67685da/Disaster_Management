from twilio.rest import Client

# Twilio credentials
account_sid = ''  # Replace with your Twilio Account SID
auth_token = 'e5d445e9dc0f544efe4ca61a8fb76c09'    # Replace with your Twilio Auth Token

# Twilio phone number
from_phone = '+19137330629'       # Replace with your Twilio number
to_phone = '+919389969916'        # Replace with the recipient's phone number (e.g., India number)

# Message details
message = "I love you :)"

# Set up Twilio client
client = Client(account_sid, auth_token)

# Send SMS
message = client.messages.create(
    body=message,
    from_=from_phone,
    to=to_phone
)

print(f"Message sent: {message.sid}")
