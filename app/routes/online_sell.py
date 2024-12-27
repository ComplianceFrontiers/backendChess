import random
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from app.database import app_signup
from app.database import schoolform_coll
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from app.utils.email_utils import send_email

online_Sell_bp = Blueprint('online_Sell', __name__)

# Function to generate a random 6-digit profile_id
def generate_unique_profile_id_1():
    while True:
        profile_id = str(random.randint(100000, 999999))  # Generate a random 6-digit number
        # Check if the profile_id already exists in the database
        if app_signup.count_documents({"profile_id": profile_id}) == 0:
            return profile_id
        
@online_Sell_bp.route('/rppp')
def home1():
    return "Hello, ramya evvu!"
# Function to generate a random 6-digit profile_id
def generate_unique_profile_id():
    while True:
        profile_id = str(random.randint(100000, 999999))  # Generate a random 6-digit number
        # Check if the profile_id already exists in the database
        if schoolform_coll.count_documents({"profile_id": profile_id}) == 0:
            return profile_id
        
@online_Sell_bp.route('/new_online_purchase_user', methods=['POST'])
def online_purchase_user():
    try:
        # Parse the incoming JSON data
        data = request.json

        # Extract and validate required fields
        email = data.get('email', "")

        # Optional: Perform validation on the email field
        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Check if the email exists in the database
        existing_user = schoolform_coll.find_one({"email": email})
        
        if existing_user:
            # Email exists, update fields with new data
            update_data = {
                "parent_name": {
                    "first": data.get('parent_first_name', ""),
                    "last": data.get('parent_last_name', "")
                },
                "child_name": {
                    "first": data.get('child_first_name', ""),
                    "last": data.get('child_last_name', "")
                },
                "phone":data.get('phone', ""),
                "category":data.get('category',""),
                "section":data.get('section', ""),
                "uscf_id":data.get('uscf_id',""),
                 "uscf_expiration_date":data.get('uscf_expiration_date',""),
                 "byes":data.get('byes',""),
                "WilmingtonChessCoaching":data.get('WilmingtonChessCoaching',""),

                 "Bear_Middletown_Chess_Tournament":data.get('Bear_Middletown_Chess_Tournament',""),
                  "New_Jersey_Masterclass":data.get('New_Jersey_Masterclass',""),
                                    "New_Jersey_Chess_Tournament":data.get('New_Jersey_Chess_Tournament',""),
                                    "chessclub":data.get('chessclub',""),

                  
            }

            # Update the user document in MongoDB
            schoolform_coll.update_one({"email": email}, {"$set": update_data})

            return jsonify({"success": "updated"}), 200
        else:
            # Generate a unique profile_id
            profile_id = generate_unique_profile_id()

            # Prepare document for MongoDB insertion
            form_data = {
                "profile_id": profile_id,  # Add the unique profile_id here
                "parent_name": {
                    "first": data.get('parent_first_name', ""),
                    "last": data.get('parent_last_name', "")
                },
                "child_name": {
                    "first": data.get('child_first_name', ""),
                    "last": data.get('child_last_name', "")
                },
                "email": email,
                "onlinePurchase": False,
                "online": True,
                "phone":data.get('phone',""),
                "PaymentStatus": data.get('payment_status', 'Not started'),
                 "category":data.get('category',""),
                "section":data.get('section', ""),
                "uscf_id":data.get('uscf_id',""),
                 "uscf_expiration_date":data.get('uscf_expiration_date',""),
                 "byes":data.get('byes',""),
                 "WilmingtonChessCoaching":data.get('WilmingtonChessCoaching',""),

                 "Bear_Middletown_Chess_Tournament":data.get('Bear_Middletown_Chess_Tournament',""),
                 "New_Jersey_Masterclass":data.get('New_Jersey_Masterclass',""),
                 "New_Jersey_Chess_Tournament":data.get('New_Jersey_Chess_Tournament',""),
                 "chessclub":data.get('chessclub',""),


            }

            # Insert the new document into MongoDB
            schoolform_coll.insert_one(form_data)

            return jsonify({"success": "new", "profile_id": profile_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
# Function to send email
def send_email(email, online_portal_link):
    DISPLAY_NAME = "Chess Champs Academy"
    sender_email = "connect@chesschamps.us"
    sender_password = "iyln tkpp vlpo sjep"  # Use your app-specific password here
    subject = "Your Access Credentials for Chess Champs Academy Portal"

    # Updated body with HTML for red text
    body = f"""
    <html>
    <body>
        <p>Dear Patron,</p>
        <p>We are pleased to provide you with the access credentials for the Chess Champs Academy portal. Below are your login details:</p>
        <ul>
            <li><strong>Access Link:</strong> <a href="{online_portal_link}">{online_portal_link}</a></li>
            <li><strong>Access Email:</strong> {email}</li>
        </ul>
        <p>Please use these credentials to log in to the portal and explore the resources available. An OTP will be generated upon your first login. 
        You will remain logged in unless you click 'Logout' or access the portal from a different device. For security purposes, we kindly recommend not sharing the link with others.</p>
        <p>Our training videos are optimized for desktop viewing, though a mobile version is available. Please note the mobile experience may be slightly glitchy, and we are actively working to improve it. 
        Thank you for your patience and continued support.</p>
        <p>If you have any questions or need further assistance, feel free to contact our support team.</p>
        <p><strong>Note:</strong> <span style="color: red;">This link will be accessible only when the payment is successful.</span></p>
        <p>Warm Regards,<br><br>Training Team<br>Chess Champs Academy</p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = f'{DISPLAY_NAME} <{sender_email}>'
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))  # Set content type to 'html'

    try:
        # SMTP server setup
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)  # Login to the email account
        server.sendmail(sender_email, email, msg.as_string())  # Send the email
        server.quit()  # Logout of the server
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

# API endpoint to trigger the email
@online_Sell_bp.route('/send_email_api_to_online_purchase_user', methods=['POST'])
def send_email_api_to_online_purchase_user():
    try:
        # Parse the incoming JSON data
        data = request.json
        email = data.get('email', '')
        
        if not email:
            return jsonify({"error": "Email is required"}), 400

        online_portal_link = "https://chess-in-school.vercel.app/"
        
        # Call the send_email function
        email_sent = send_email(email, online_portal_link)
        
        if email_sent:
            return jsonify({"success": "Email sent successfully"}), 200
        else:
            return jsonify({"error": "Failed to send email"}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

