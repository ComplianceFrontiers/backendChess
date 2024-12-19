import random
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from app.database import bulkemail,schoolform_coll

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

        existing_record = bulkemail.find_one({"email": data["email"]})
        existing_in_schoolcol = schoolform_coll.find_one({"email": data["email"]})

        if existing_record or existing_in_schoolcol:
            # If the email exists, update the existing record
            updated_data = {
            }

            # Update optional fields dynamically
            for key, value in data.items():
                if key not in ['email']:  # Skip required fields
                    updated_data[key] = value

            # Update the record in the database
            bulkemail.update_one({"email": data.get('email')}, {"$set": updated_data})

            return jsonify({"message": "Record updated successfully!"}), 200
        else:
            # If the email does not exist, insert a new record
            profile_id = generate_unique_profile_id_1()  # Generate a unique profile ID

            # Prepare the document with required fields
            form_data = {
                "profile_id": profile_id,
                "name": data.get('name'),
                "email": data.get('email'),
                "phone": data.get('phone'),
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


@bulkemail_bp.route('/get_master_list', methods=['GET'])
def get_master_list():
    try:
        # Fetch records from both collections
        schoolform_records = list(schoolform_coll.find({}, {'_id': 0}))
        bulkemail_records = list(bulkemail.find({}, {'_id': 0}))

        # Combine the records
        all_records = schoolform_records + bulkemail_records

        # Dictionary to hold merged data by email
        merged_records = {}

        for record in all_records:
            email = record.get('email')
            if email:
                if email not in merged_records:
                    # Add the record if email is not already in the dictionary
                    merged_records[email] = record
                else:
                    # Merge fields for duplicate emails
                    for key, value in record.items():
                        if key not in merged_records[email] or not merged_records[email][key]:
                            merged_records[email][key] = value

        # Convert merged records back to a list
        result = list(merged_records.values())

        return jsonify(result), 200

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

        # Use HTML for email body to support formatting
        body = """
        <html>
        <body>
            <p>Dear Patron,</p>
            <p>Thank you for registering yourself/your child with Chess Champs! We’re excited to have you join our community, where young minds develop essential skills while exploring the wonderful world of chess.</p>
            <p>At Chess Champs, you will have access to:</p>
            <ul>
                <li><b>Chess Clubs</b>: Weekly sessions to learn, practice, and connect with other budding chess players.</li>
                <li><b>Tournaments</b>: Fun and competitive events to test their skills and build confidence.</li>
                <li><b>Community Events</b>: Special programs fostering teamwork, sportsmanship, and a love for the game.</li>
                <li><b>Online Courses</b>: Flexible, engaging lessons that allow learning from the comfort of home.</li>
            </ul>
            <p>Our programs are designed to be educational, interactive, and most importantly, enjoyable. We’re committed to providing an environment to thrive and grow, both on and off the chessboard.</p>
            <p>Should you have any questions or need further information, please don’t hesitate to reach out at <a href="mailto:connect@chesschamps.us">connect@chesschamps.us</a>.</p>
            <p>Thank you for letting us be a part of your chess journey. Together, we’ll inspire a lifelong passion for learning and success!</p>
            <p>Warm regards,</p>
            <p>
                Siddharth Bose (Sid)<br>
                Founder & Lead Coach<br>
                <a href="https://www.chesschamps.us">www.chesschamps.us</a>
            </p>
            <p><i>Empowering Young Minds Through Chess</i></p>
            <p style="font-size: 14px; color: #666; text-align: center; margin-top: 0px;">
                You are receiving this email because you signed up to receive updates and communications from 
                <a href="https://chesschamps.us" style="color: #f53db8; text-decoration: none;">Chess Champs</a>. 
                If you wish to stop receiving these emails, you can 
                <a href="https://chesschampsus.vercel.app/unsubscribe" style="color: #f53db8; text-decoration: none;">unsubscribe here</a>.
            </p>
        </body>
        </html>
        """

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = f'{DISPLAY_NAME} <{sender_email}>'
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))  # Set MIME type to 'html'

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
