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
    return "Hello, ramya!"
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
            # Email exists, return success with "old"
            return jsonify({"success": "old"}), 201
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
                "phone": data.get('phone', ""),
                "SchoolName": data.get('SchoolName', ""),
                "PaymentStatus": data.get('redirect_status', 'Not started')
            }

            # Insert the new document into MongoDB
            schoolform_coll.insert_one(form_data)

            return jsonify({"success": "new", "profile_id": profile_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
