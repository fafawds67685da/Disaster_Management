from twilio.rest import Client

# Twilio credentials
account_sid = 'AC4c024fc964c6236c3b439abd84d49329'
auth_token = 'e5d445e9dc0f544efe4ca61a8fb76c09'
from_phone = '+19137330629'

def send_message(to_phone, message):
    client = Client(account_sid, auth_token)
    try:
        message_sent = client.messages.create(
            body=message,
            from_=from_phone,
            to=to_phone
        )
        return f"Message sent to {to_phone}: {message_sent.sid}"
    except Exception as e:
        return f"Failed to send message to {to_phone}: {e}"
