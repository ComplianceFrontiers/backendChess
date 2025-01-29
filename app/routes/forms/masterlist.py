import random
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from app.database import form_chess_club,form_Wilmington_Chess_Coaching,form_Bear_Middletown_Chess_Tournament,form_Bear_Middletown_Chess_Coaching,form_New_Jersey_Chess_Tournament,form_Basics_Of_Chess,masterlist
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask import Blueprint, request, jsonify
from app.utils.email_utils import send_email
import pytz
from datetime import datetime

masterlist_bp = Blueprint('masterlist', __name__)
new_york_tz = pytz.timezone('America/New_York')
current_datetime = datetime.now(new_york_tz)
current_date = current_datetime.strftime('%m-%d-%Y')  # Format as MM-DD-YYYY
current_time = current_datetime.strftime('%H:%M:%S')  # Format as HH:MM:SS

# Function to generate a random 6-digit profile_id
def generate_unique_profile_id():
    while True:
        profile_id = str(random.randint(100000, 999999))  # Generate a random 6-digit number
        # Check if the profile_id already exists in the database
        if masterlist.count_documents({"profile_id": profile_id}) == 0:
            return profile_id

@masterlist_bp.route('/masterlist_bp_submit', methods=['POST'])
def masterlist_bp_submit():
    try:
        # Parse the incoming JSON data
        data = request.json

        # Extract and validate required fields
        parent_first_name = data.get('parent_first_name', "")
        parent_last_name = data.get('parent_last_name', "")
        child_first_name = data.get('child_first_name', "")
        child_last_name = data.get('child_last_name', "")
        child_grade = data.get('child_grade',"")
        email = data.get('email', "")
        phone = data.get('phone', "")
        RequestFinancialAssistance = data.get('RequestFinancialAssistance',False)
        SchoolName = data.get('SchoolName',"")
        program=data.get('program','')
        Year = data.get('year', 2025)
        mpes = data.get('mpes', False)  # Default to False if not provided
        lombardy = data.get('lombardy', False)  # Default to False if not provided
        jcc = data.get('jcc', False) 
        jcc_kp = data.get('jcc_kp', False) 
        WhatsApp= data.get('WhatsApp', False)
        Website= data.get('Website', False) 
        New_Jersey_Masterclass = data.get('New_Jersey_Masterclass', False) 
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
            "child_grade": child_grade,
            "RequestFinancialAssistance": RequestFinancialAssistance,
            "SchoolName": SchoolName,
            "email": email,
            "phone": phone,
            "email_request":True,
            "year": Year,
            "program":program,
            "WhatsApp":WhatsApp,
            "Website":Website,

            "mpes": mpes, 
            "lombardy": lombardy,
            "jcc":jcc,
            "jcc_kp":jcc_kp,
            "New_Jersey_Masterclass":New_Jersey_Masterclass,
            "date": current_date,  # Add the current date (MM-DD-YYYY)
            "time": current_time,  # Add the current time (HH:MM:SS)
        }

        # Insert into MongoDB
        masterlist.insert_one(form_data)

        return jsonify({"message": "Form submitted successfully!", "profile_id": profile_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@masterlist_bp.route('/masterlist_bp_delete_records_by_profile_ids', methods=['DELETE'])
def masterlist_bp_delete_records_by_profile_ids():
    try:
        # Extract the list of profile IDs from the request body
        data = request.json
        profile_ids = data.get('profile_ids')

        # Validate input
        if not profile_ids or not isinstance(profile_ids, list):
            return jsonify({"error": "A valid list of profile_ids is required"}), 400

        # List of all collections to check and delete records
        collections = [
            form_chess_club,
            form_Wilmington_Chess_Coaching,
            form_Bear_Middletown_Chess_Tournament,
            form_Bear_Middletown_Chess_Coaching,
            form_New_Jersey_Chess_Tournament,
            form_Basics_Of_Chess,
            masterlist
        ]

        deleted_profiles = []
        not_found_profiles = []

        # Iterate over all profile IDs
        for profile_id in profile_ids:
            found = False
            # Check all collections for the given profile_id
            for collection in collections:
                result = collection.delete_one({"profile_id": str(profile_id)})
                if result.deleted_count > 0:
                    found = True  # Mark as found and deleted
            if found:
                deleted_profiles.append(profile_id)  # Profile ID successfully deleted
            else:
                not_found_profiles.append(profile_id)  # Profile ID not found in any collection

        return jsonify({
            "status": True,
            "message": "Deletion process completed",
            "deleted_profiles": deleted_profiles,
            "not_found_profiles": not_found_profiles
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@masterlist_bp.route('/get_form_master_list', methods=['GET'])
def get_master_list():
    try:
        # List of all collections to fetch data from
        collections = [
            form_chess_club,
            form_Wilmington_Chess_Coaching,
            form_Bear_Middletown_Chess_Tournament,
            form_Bear_Middletown_Chess_Coaching,
            form_New_Jersey_Chess_Tournament,
            form_Basics_Of_Chess,
            masterlist
        ]

        # Fetch all records from collections
        all_records = []
        for collection in collections:
            all_records.extend(collection.find({}, {'_id': 0}))

        # Merge records by email
        merged_records = {}
        for record in all_records:
            email = record.get('email')
            if email:
                # Use `setdefault` to initialize or merge the record
                existing_record = merged_records.setdefault(email, {})
                for key, value in record.items():
                    if key not in existing_record or not existing_record[key]:
                        existing_record[key] = value

        # Convert merged records to a list
        result = list(merged_records.values())

        # Sort the result by the 'date' field in descending order
        # Assumes the 'date' field is in the format 'MM-DD-YYYY'
        sorted_result = sorted(
            result,
            key=lambda x: datetime.strptime(x.get('date', '01-01-1970'), '%m-%d-%Y'),
            reverse=True
        )

        return jsonify(sorted_result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@masterlist_bp.route('/masterlist_by_profile_id', methods=['GET'])
def get_masterlist_by_profile_id():
    try:
        # Extract 'profile_id' from query parameters
        profile_id = request.args.get('profile_id')

        # Validate the input
        if not profile_id:
            return jsonify({"error": "Profile ID is required"}), 400

        # List of all collections to search
        collections = [
            form_chess_club,
            form_Wilmington_Chess_Coaching,
            form_Bear_Middletown_Chess_Tournament,
            form_Bear_Middletown_Chess_Coaching,
            form_New_Jersey_Chess_Tournament,
            form_Basics_Of_Chess,
            masterlist
        ]

        # Search for the profile ID in all collections
        for collection in collections:
            record = collection.find_one({"profile_id": str(profile_id)}, {'_id': 0})  # Exclude MongoDB's default '_id' field
            if record:
                return jsonify(record), 200  # Return the first match found

        # If not found in any collection
        return jsonify({"error": "Record not found"}), 404

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@masterlist_bp.route('/get_masterlist_by_email', methods=['GET'])
def get_masterlist_by_email():
    try:
        # Extract 'email' from query parameters
        email = request.args.get('email')

        # Validate the input
        if not email:
            return jsonify({"error": "Email is required"}), 400

        # List of all collections to search
        collections = [
            form_chess_club,
            form_Wilmington_Chess_Coaching,
            form_Bear_Middletown_Chess_Tournament,
            form_Bear_Middletown_Chess_Coaching,
            form_New_Jersey_Chess_Tournament,
            form_Basics_Of_Chess,
            masterlist
        ]

        # Search for the first record matching the email
        for collection in collections:
            record = collection.find_one({"email": email}, {'_id': 0})  # Exclude MongoDB's default '_id' field
            if record:
                return jsonify(record), 200  # Return the first match found

        # If no records found
        return jsonify({"error": "No records found for the provided email"}), 404

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@masterlist_bp.route('/update_masterlist_by_email', methods=['PUT'])
def update_masterlist_by_email():
    try:
        # Extract 'email' and 'email_request' from request body
        data = request.get_json()
        email = data.get('email')
        email_request = data.get('email_request')

        # Validate the input
        if not email or email_request is None:
            return jsonify({"error": "Both 'email' and 'email_request' are required"}), 400

        # List of all collections to update
        collections = [
            form_chess_club,
            form_Wilmington_Chess_Coaching,
            form_Bear_Middletown_Chess_Tournament,
            form_Bear_Middletown_Chess_Coaching,
            form_New_Jersey_Chess_Tournament,
            form_Basics_Of_Chess,
            masterlist
        ]

        # Update all records matching the email
        total_updated = 0
        for collection in collections:
            result = collection.update_many(
                {"email": email},  # Filter by email
                {"$set": {"email_request": email_request}}  # Set the new field
            )
            total_updated += result.modified_count  # Track the number of updated records

        # If no records were updated
        if total_updated == 0:
            return jsonify({"error": "No records found for the provided email"}), 404

        # Return success response
        return jsonify({
            "message": f"Successfully updated {total_updated} records",
            "email": email,
            "email_request": email_request
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
def send_email(email, online_portal_link):
    DISPLAY_NAME="Chess Champs Academy"
    sender_email = "connect@chesschamps.us"
    sender_password = "iyln tkpp vlpo sjep"  # Use your app-specific password here
    subject = "Your Access Credentials for Chess Champs Academy Portal"

    body = (
            f"Dear Patron,\n\n"
            f"We are pleased to provide you with the access credentials for the Chess Champs Academy portal. Below are your login details:\n"
            f"• Access Link: {online_portal_link}\n"
            f"• Access Email: {email}\n\n"
            f"Please use these credentials to log in to the portal and explore the resources available. An OTP will be generated upon your first login. "
            f"You will remain logged in unless you click 'Logout' or access the portal from a different device. For security purposes, we kindly recommend not sharing the link with others.\n\n"
            f"If you have any questions or need further assistance, feel free to contact our support team.\n\n"
            f"Warm Regards ,\n\n"
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
        print(f"Failed to send email: {str(e)}")
        return False
