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
 
@bulkemail_bp.route('/get_forms2', methods=['GET'])
def get_forms2():
    try:
        # Fetch all documents from the collection
        records = list(bulkemail.find({}, {'_id': 0}))  # Exclude the MongoDB ID field
        
        return jsonify(records), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
