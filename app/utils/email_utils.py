import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
DISPLAY_NAME = "Chess Champs Academy"
def send_email(email, session_link, date, time, coach_name):
    sender_email = "connect@chesschamps.us"
    sender_password = "iyln tkpp vlpo sjep"  # Use your app-specific password here
    subject = "Your Chess Session Enrollment"

    body = (
        f"Dear Participant,\n\n"
        f"You have successfully enrolled in the chess session.\n\n"
        f"Details of the session are as follows:\n"
        f"Date: {date}\n"
        f"Time: {time}\n"
        f"Coach: {coach_name}\n"
        f"Session Link: {session_link}\n\n"
        f"We hope you enjoy your session!\n\n"
        f"Best regards,\n"
        f"The Chess Training Team"
    )

    msg = MIMEMultipart()
    msg['From'] = f'{DISPLAY_NAME} <{sender_email}>'
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    text = msg.as_string()
    server.sendmail(sender_email, email, text)
    server.quit()


def send_email_BOC_list(email, online_portal_link):
    sender_email = "connect@chesschamps.us"
    sender_password = "iyln tkpp vlpo sjep"  # Use your app-specific password here
    subject = "Welcome to 'Basics of Chess' Online Tutorial"

    body = (
        f"Subject: Welcome to 'Basics of Chess' Online Tutorial\n\n"
        f"Dear Patron,\n\n"
        f"Thank you for registering for the 'Basics of Chess'. This course is specially designed for absolute beginners or individuals with minimal knowledge of chess. "
        f"The modules are presented as concise videos, and we recommend watching them multiple times to gain confidence in the concepts discussed.\n\n"
        f"To access the course modules, please log in to www.ChessChamps.us and navigate to the 'Chess Champs Academy' portal. Below are your access credentials for the portal:\n\n"
        f"• Access Email: {email}\n\n"
        f"Upon your first login, a one-time password (OTP) will be generated for verification. Once logged in, you will remain signed in unless you click 'Logout' or access the portal from a different device. "
        f"For security reasons, we kindly ask that you do not share your access credentials with others.\n\n"
        f"Important Note: Access to the portal will be activated upon successful payment.\n\n"
        f"If you have any questions or require assistance, please feel free to contact our support team.\n\n"
        f"Warm regards,\n\n"
        f"Training Team\n"
        f"Chess Champs Academy"
    )

    msg = MIMEMultipart()
    msg['From'] = f'{DISPLAY_NAME} <{sender_email}>'
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False