import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(to_email, subject, message):
    from_email = "mailer@agk-law.com"
    smtp_server = "mail.agk-law.com"
    smtp_port = 587
    smtp_username = "mailer@agk-law.com"
    smtp_password = "Eh@MMWVCuu_S"
    # Create the MIME message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the message body
    msg.attach(MIMEText(message, 'plain'))

    try:
        # Set up the SMTP server and start TLS for security
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        # Log in to the SMTP server
        server.login(smtp_username, smtp_password)

        # Send the email
        server.send_message(msg)
        print(f'Email sent successfully to {to_email}')

    except Exception as e:
        print(f'Failed to send email to {to_email}. Error: {e}')

    finally:
        # Terminate the SMTP session
        server.quit()

