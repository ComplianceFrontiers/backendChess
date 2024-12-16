import random
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from app.database import email_request

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from app.utils.email_utils import send_email

email_request_bp = Blueprint('email_request', __name__)

# Function to generate a random 6-digit profile_id
def generate_unique_profile_id():
    while True:
        profile_id = str(random.randint(100000, 999999))  # Generate a random 6-digit number
        # Check if the profile_id already exists in the database
        return profile_id
        
@email_request_bp.route('/r121')
def home121():
    return "Hello, ramya!"


def send_email_to_admin(email,subject, question):
    """Send an email with the subject and question to connect@chesschamps.us."""
    sender_email = "connect@chesschamps.us"
    sender_password = "iyln tkpp vlpo sjep"  # Replace with your app-specific password
    recipient_email = "connect@chesschamps.us"
    subject_line = "New Question Submission"

    body = (
        f"A new question has been submitted:\n\n"
        f"Subject: {subject}\n"
        f"From Email: {email}\n"
        f"Question: {question}\n\n"
        f"Please review and respond accordingly."
    )

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject_line
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

@email_request_bp.route('/submit_question_email', methods=['POST'])
def submit_question_email():
    try:
        # Parse the incoming JSON data
        data = request.get_json()
        
        # Extract required fields
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        question = data.get('question')

        # Validate required fields
        if not all([name, email, subject, question]):
            return jsonify({"error": "Name, email, subject, and question are required"}), 400

        # Generate a new unique profile ID
        profile_id = generate_unique_profile_id()

        # Prepare the document to insert
        new_entry = {
            "profile_id": profile_id,
            "name": name,
            "email": email,
            "subject": subject,
            "question": question,
        }

        # Insert the document into MongoDB
        email_request.insert_one(new_entry)
        send_email_to_admin(email,subject, question)

        return jsonify({
            "message": "Question submitted successfully!",
            "profile_id": profile_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@email_request_bp.route('/get_forms21', methods=['GET'])
def get_forms21():
    try:
        # Fetch all documents from the collection
        records = list(email_request.find({}, {'_id': 0}))  # Exclude the MongoDB ID field
        
        return jsonify(records), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    