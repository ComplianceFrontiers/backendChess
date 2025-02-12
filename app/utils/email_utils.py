import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DISPLAY_NAME = "Chess Champs Academy"
def send_email(email, session_link, date, time, coach_name):
    sender_email = "connect@chesschamps.us"
    sender_password = "akln niwh wzra ruzf"  # Use your app-specific password here
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
    sender_password = "akln niwh wzra ruzf"  # Use your app-specific password here
    subject = "Welcome to 'Basics of Chess' Online Tutorial"

    body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
            }}
            .important-note {{
                color: red;
                font-style: italic;
            }}
            .bold {{
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <p>Dear Patron,</p>
        
        <p>Thank you for registering for the <span class="bold">Basics of Chess.</span> This course is specially designed for absolute beginners or individuals with minimal knowledge of chess. 
        The modules are presented as concise videos, and we recommend watching them multiple times to gain confidence in the concepts discussed.</p>

        <p>To access the course modules, please log in to <a href="{online_portal_link}">www.ChessChamps.us</a> and navigate to the <span class="bold">Chess Champs Academy</span> portal. Below are your access credentials for the portal:</p>

        <ul>
            <li><strong>Access Email:</strong> {email}</li>
        </ul>

        <p>Upon your first login, a one-time password (OTP) will be generated for verification. Once logged in, you will remain signed in unless you click 'Logout' or access the portal from a different device. 
        For security reasons, we kindly ask that you do not share your access credentials with others.</p>

        <p><strong>Important Note:</strong> <span class="important-note">Access to the portal will be activated upon successful payment.</span></p>

        <p>If you have any questions or require assistance, please feel free to contact our support team.</p>

        <p>Warm regards,</p>

        <p>Training Team<br>Chess Champs Academy</p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = f'{DISPLAY_NAME} <{sender_email}>'
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False
