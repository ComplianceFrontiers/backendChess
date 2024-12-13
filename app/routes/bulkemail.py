import random
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from app.database import bulkemail

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from app.utils.email_utils import send_email

bulkemail_bp = Blueprint('bulkemail', __name__)

# Function to generate a random 6-digit profile_id
def generate_unique_profile_id_1():
    while True:
        profile_id = str(random.randint(100000, 999999))  # Generate a random 6-digit number
        # Check if the profile_id already exists in the database
        if bulkemail.count_documents({"profile_id": profile_id}) == 0:
            return profile_id
        
@bulkemail_bp.route('/r12')
def home12():
    return "Hello, ramya!"


@bulkemail_bp.route('/signup_bulk_email', methods=['POST'])
def signup_bulk_email():
    try:
        # Parse the incoming JSON data
        data = request.get_json()
        print(data)

        # Extract required fields
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')

        # Validate required fields
        if not all([name, email, phone]):
            return jsonify({"error": "Name, email, and phone are required"}), 400

        # Check if the email already exists in the database
        existing_record = bulkemail.find_one({"email": email})

        if existing_record:
            # If the email exists, update the existing record
            updated_data = {
                "name": name,
                "email": email,
                "phone": phone,
            }

            # Update optional fields dynamically
            for key, value in data.items():
                if key not in ['name', 'email', 'phone']:  # Skip required fields
                    updated_data[key] = value

            # Update the record in the database
            bulkemail.update_one({"email": email}, {"$set": updated_data})

            return jsonify({"message": "Record updated successfully!"}), 200
        else:
            # If the email does not exist, insert a new record
            profile_id = generate_unique_profile_id_1()  # Generate a unique profile ID

            # Prepare the document with required fields
            form_data = {
                "profile_id": profile_id,
                "name": name,
                "email": email,
                "phone": phone,
            }

            # Add optional fields dynamically
            for key, value in data.items():
                if key not in ['name', 'email', 'phone']:  # Skip required fields
                    form_data[key] = value

            # Insert the document into MongoDB
            bulkemail.insert_one(form_data)

            return jsonify({"message": "Form submitted successfully!", "profile_id": profile_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
 

@bulkemail_bp.route('/signup_bulk_only_email', methods=['POST'])
def signup_bulk_only_email():
    try:
        # Parse the incoming JSON data
        data = request.get_json()
        print(data)

        # Extract the email field
        email = data.get('email')

        # Validate the required email field
        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Check if the email already exists in the database
        existing_record = bulkemail.find_one({"email": email})

        if existing_record:
            # If the email exists, update the existing record
            updated_data = {"email": email}

            # Update optional fields dynamically
            for key, value in data.items():
                if key != 'email':  # Skip the email field
                    updated_data[key] = value

            # Update the record in the database
            bulkemail.update_one({"email": email}, {"$set": updated_data})

            return jsonify({"message": "Record updated successfully!"}), 200
        else:
            # If the email does not exist, insert a new record
            profile_id = generate_unique_profile_id_1()  # Generate a unique profile ID

            # Prepare the document with the required email field
            form_data = {
                "profile_id": profile_id,
                "email": email,
            }

            # Add optional fields dynamically
            for key, value in data.items():
                if key != 'email':  # Skip the email field
                    form_data[key] = value

            # Insert the document into MongoDB
            bulkemail.insert_one(form_data)

            return jsonify({"message": "Form submitted successfully!", "profile_id": profile_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400



@bulkemail_bp.route('/get_forms2', methods=['GET'])
def get_forms2():
    try:
        # Fetch all documents from the collection
        records = list(bulkemail.find({}, {'_id': 0}))  # Exclude the MongoDB ID field
        
        return jsonify(records), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@bulkemail_bp.route('/get_forms_byemail', methods=['GET'])
def get_forms_byemail():
    try:
        # Extract email from the query parameters
        email = request.args.get('email')  # Get email from the URL query string

        # Check if email is provided
        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Fetch documents from the collection where email matches
        record = bulkemail.find_one({"email": email}, {'_id': 0})  # Exclude the MongoDB ID field
        
        if not record:
            return jsonify({"error": "No record found for this email"}), 404

        return jsonify(record), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bulkemail_bp.route('/reviewfromemail', methods=['POST'])
def review_from_email():
    try:
        # Parse the JSON data from the request
        data = request.json

        # Extract required fields
        email = data.get('email')
        rate = data.get('rate')
        review = data.get('review')

        # Validate inputs
        if not email or not rate or not review:
            return jsonify({"error": "Email, rate, and review are required"}), 400

        # Find the record by email
        record = bulkemail.find_one({"email": email})
        if not record:
            return jsonify({"error": "No record found for the provided email"}), 404

        # Update the record with the review and rate
        bulkemail.update_one(
            {"email": email},
            {"$set": {"rate": rate, "review": review}}
        )

        return jsonify({"message": "Review and rating submitted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bulkemail_bp.route('/send-email-form-website-joined', methods=['POST'])
def send_email_school_form_website_joined():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Email configuration
        DISPLAY_NAME = "Chess Champs"
        sender_email = "connect@chesschamps.us"
        sender_password = "iyln tkpp vlpo sjep"  # Use your app-specific password here
        subject = "Welcome to Chess Champs – Thank You for Joining Us!"

        body = (
            "Dear Patron,\n\n"
            "Thank you for registering your child with Chess Champs! We’re excited to have your family join our community, where young minds develop essential skills while exploring the wonderful world of chess.\n\n"
            "At Chess Champs, your child will have access to:\n"
            "    • **Chess Clubs**: Weekly sessions to learn, practice, and connect with other budding chess players.\n"
            "    • **Tournaments**: Fun and competitive events to test their skills and build confidence.\n"
            "    • **Community Events**: Special programs fostering teamwork, sportsmanship, and a love for the game.\n"
            "    • **Online Courses**: Flexible, engaging lessons that allow learning from the comfort of home.\n\n"
            "Our programs are designed to be educational, interactive, and most importantly, enjoyable. We’re committed to providing an environment where your child can thrive and grow, both on and off the chessboard.\n\n"
            "Should you have any questions or need further information, please don’t hesitate to reach out at connect@chesschamps.us\n\n"
            "Thank you for letting us be a part of your child’s journey. Together, we’ll inspire a lifelong passion for learning and success!\n\n"
            "Warm regards,\n\n"
            "Siddharth Bose (Sid)\n"
            "Founder & Lead Coach\n"
            "www.chesschamps.us\n\n"
            "_Empowering Young Minds Through Chess_"
        )

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = f'{DISPLAY_NAME} <{sender_email}>'
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()

        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
