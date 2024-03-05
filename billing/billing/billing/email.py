import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(email, balance):
    sender_email = 'popugmoney@exmaple.com'
    sender_password = 'popug_password'
    recipient_email = email
    subject = 'Get Your Money'
    message = f'You earned {balance} popug bucks'

    _send_email(sender_email, sender_password, recipient_email, subject, message)


def _send_email(sender_email, sender_password, recipient_email, subject, message):
    # Set up the SMTP server (Gmail SMTP server in this case)
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Attach the message to the email body
    msg.attach(MIMEText(message, 'plain'))

    # Connect to the SMTP server and send the email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")
