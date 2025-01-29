import random
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from app.database import form_Wilmington_Chess_Coaching

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask import Blueprint, request, jsonify
from app.utils.email_utils import send_email
import pytz
from datetime import datetime

# Set timezone to New York (Eastern Time)
new_york_tz = pytz.timezone('America/New_York')
current_datetime = datetime.now(new_york_tz)
 
form_Wilmington_Chess_Coaching_bp = Blueprint('form_Wilmington_Chess_Coaching', __name__)
# Get current date and time
current_date = current_datetime.strftime('%m-%d-%Y')  # Format as MM-DD-YYYY
current_time = current_datetime.strftime('%H:%M:%S')  # Format as HH:MM:SS

# Function to generate a random 6-digit profile_id
def generate_unique_profile_id():
    while True:
        profile_id = str(random.randint(100000, 999999))  # Generate a random 6-digit number
        # Check if the profile_id already exists in the database
        if form_Wilmington_Chess_Coaching.count_documents({"profile_id": profile_id}) == 0:
            return profile_id

@form_Wilmington_Chess_Coaching_bp.route('/form_Wilmington_Chess_Coaching_bp_submit', methods=['POST'])
def form_Wilmington_Chess_Coaching_bp_submit():
    try:
        # Parse the incoming JSON data
        data = request.json

        # Extract and validate required fields
        parent_first_name = data.get('parent_first_name', "")
        parent_last_name = data.get('parent_last_name', "")
        child_first_name = data.get('child_first_name', "")
        child_last_name = data.get('child_last_name', "")
        child_grade= data.get('child_grade', "")
        program= data.get('program', "")
        USCF_Rating= data.get('USCF_Rating', "")
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
            "child_grade":child_grade,
            "program":program,
            "USCF_Rating":USCF_Rating,
            "Wilmington_Chess_Coaching": True,
            "email_request":True,
            "date": current_date,  # Add the current date (MM-DD-YYYY)
            "time": current_time,  # Add the current time (HH:MM:SS)
        }

        # Insert into MongoDB
        form_Wilmington_Chess_Coaching.insert_one(form_data)

        return jsonify({"message": "Form submitted successfully!", "profile_id": profile_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@form_Wilmington_Chess_Coaching_bp.route('/form_Wilmington_Chess_Coaching_bp_delete_records_by_profile_ids', methods=['DELETE'])
def form_Wilmington_Chess_Coaching_bp_delete_records_by_profile_ids():
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
            result = form_Wilmington_Chess_Coaching.delete_one({"profile_id": str(profile_id)})

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

@form_Wilmington_Chess_Coaching_bp.route('/get_forms_form_Wilmington_Chess_Coaching', methods=['GET'])
def get_forms_form_Wilmington_Chess_Coaching():
    try:
        # Fetch all documents from the collection in descending order
        records = list(form_Wilmington_Chess_Coaching.find({}, {'_id': 0}).sort([('_id', -1)]))  # Sort by '_id' in descending order
        
        return jsonify(records), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@form_Wilmington_Chess_Coaching_bp.route('/form_Wilmington_Chess_Coaching_by_profile_id', methods=['GET'])
def get_form_Wilmington_Chess_Coaching_by_profile_id():
    try:
        # Extract 'profile_id' from query parameters
        profile_id = request.args.get('profile_id')

        # Validate the input
        if not profile_id:
            return jsonify({"error": "Profile ID is required"}), 400

        # Fetch the document from the collection
        record = form_Wilmington_Chess_Coaching.find_one({"profile_id": str(profile_id)}, {'_id': 0})  # Exclude MongoDB's default '_id' field

        if record:
            return jsonify(record), 200
        else:
            return jsonify({"error": "Record not found"}), 404

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

