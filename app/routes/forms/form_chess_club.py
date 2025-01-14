import random
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from app.database import form_chess_club

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask import Blueprint, request, jsonify
from app.utils.email_utils import send_email
from datetime import datetime


form_chess_club_bp = Blueprint('form_chess_club', __name__)
# Get current date and time
current_datetime = datetime.now()
current_date = current_datetime.strftime('%m-%d-%Y')  # Format as MM-DD-YYYY
current_time = current_datetime.strftime('%H:%M:%S')  # Format as HH:MM:SS

# Function to generate a random 6-digit profile_id
def generate_unique_profile_id():
    while True:
        profile_id = str(random.randint(100000, 999999))  # Generate a random 6-digit number
        # Check if the profile_id already exists in the database
        if form_chess_club.count_documents({"profile_id": profile_id}) == 0:
            return profile_id

@form_chess_club_bp.route('/form_chess_club_bp_submit', methods=['POST'])
def form_chess_club_bp_submit():
    try:
        # Parse the incoming JSON data
        data = request.json

        # Extract and validate required fields
        parent_first_name = data.get('parent_first_name', "")
        parent_last_name = data.get('parent_last_name', "")
        child_first_name = data.get('child_first_name', "")
        child_last_name = data.get('child_last_name', "")
        email = data.get('email', "")
        phone = data.get('phone', "")
        Year = data.get('year', 2025)
        profile_id = generate_unique_profile_id()

        # Get current date and time
        current_datetime = datetime.now()
        current_date = current_datetime.strftime('%m-%d-%Y')  # Format as MM-DD-YYYY
        current_time = current_datetime.strftime('%H:%M:%S')  # Format as HH:MM:SS

        # Prepare document for MongoDB insertion
        form_data = {
            "profile_id": profile_id,  # Add the unique profile_id here
            "parent_name": {
                "first": parent_first_name,
                "last": parent_last_name
            },
            "child_name": {
                "first": child_first_name,
                "last": child_last_name
            },
            "email": email,
            "phone": phone,
            "year": Year,
            "chess_club": True,
            "date": current_date,  # Add the current date (MM-DD-YYYY)
            "time": current_time,  # Add the current time (HH:MM:SS)
        }

        # Insert into MongoDB
        form_chess_club.insert_one(form_data)

        return jsonify({"message": "Form submitted successfully!", "profile_id": profile_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@form_chess_club_bp.route('/form_chess_club_bp_delete_records_by_profile_ids', methods=['DELETE'])
def form_chess_club_bp_delete_records_by_profile_ids():
    try:
        # Extract the list of profile IDs from the request body
        data = request.json
        profile_ids = data.get('profile_ids')

        # Validate input
        if not profile_ids or not isinstance(profile_ids, list):
            return jsonify({"error": "A valid list of profile_ids is required"}), 400

        deleted_profiles = []
        not_found_profiles = []

        for profile_id in profile_ids:
            # Attempt to delete the record from the collection
            result = form_chess_club.delete_one({"profile_id": str(profile_id)})

            if result.deleted_count > 0:
                deleted_profiles.append(profile_id)  # Successfully deleted
            else:
                not_found_profiles.append(profile_id)  # Not found

        return jsonify({
            "status": True,
            "message": "Deletion process completed",
            "deleted_profiles": deleted_profiles,
            "not_found_profiles": not_found_profiles
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@form_chess_club_bp.route('/get_forms_form_chess_club', methods=['GET'])
def get_forms_form_chess_club():
    try:
        # Fetch all documents from the collection in descending order
        records = list(form_chess_club.find({}, {'_id': 0}).sort([('_id', -1)]))  # Sort by '_id' in descending order
        
        return jsonify(records), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
