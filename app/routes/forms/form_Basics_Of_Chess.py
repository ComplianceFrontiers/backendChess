import random
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from app.database import form_Basics_Of_Chess

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask import Blueprint, request, jsonify
from app.utils.email_utils import send_email
import pytz
from datetime import datetime
 

form_Basics_Of_Chess_bp = Blueprint('form_Basics_Of_Chess', __name__)

# Get current time in UTC
utc_time = datetime.now(pytz.utc)

# Convert UTC to New York time
new_york_tz = pytz.timezone('America/New_York')
current_datetime = utc_time.astimezone(new_york_tz)

current_date = current_datetime.strftime('%m-%d-%Y')  # Format as MM-DD-YYYY
current_time = current_datetime.strftime('%H:%M:%S')  # Format as HH:MM:SS

# Function to generate a random 6-digit profile_id
def generate_unique_profile_id():
    while True:
        profile_id = str(random.randint(100000, 999999))  # Generate a random 6-digit number
        # Check if the profile_id already exists in the database
        if form_Basics_Of_Chess.count_documents({"profile_id": profile_id}) == 0:
            return profile_id

@form_Basics_Of_Chess_bp.route('/form_Basics_Of_Chess_bp_submit', methods=['POST'])
def form_Basics_Of_Chess_bp_submit():
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
        New_Jersey_Masterclass = data.get('New_Jersey_Masterclass', False) 
        onlinePurchase=data.get('onlinePurchase',False)
        BasicsOfChess_Online=data.get('BasicsOfChess_Online',False)
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
            "year": Year,
            "program":program,
            "mpes": mpes, 
            "lombardy": lombardy,
            "jcc":jcc,
            "jcc_kp":jcc_kp,
            "New_Jersey_Masterclass":New_Jersey_Masterclass,
            "onlinePurchase":onlinePurchase,
            "BasicsOfChess_Online":BasicsOfChess_Online,
            "date": current_date,  # Add the current date (MM-DD-YYYY)
            "time": current_time,  # Add the current time (HH:MM:SS)
        }

        # Insert into MongoDB
        form_Basics_Of_Chess.insert_one(form_data)

        return jsonify({"message": "Form submitted successfully!", "profile_id": profile_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@form_Basics_Of_Chess_bp.route('/form_Basics_Of_Chess_bp_delete_records_by_profile_ids', methods=['DELETE'])
def form_Basics_Of_Chess_bp_delete_records_by_profile_ids():
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
            result = form_Basics_Of_Chess.delete_one({"profile_id": str(profile_id)})

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

@form_Basics_Of_Chess_bp.route('/get_forms_form_Basics_Of_Chess', methods=['GET'])
def get_forms_form_Basics_Of_Chess():
    try:
        # Fetch all documents from the collection in descending order
        records = list(form_Basics_Of_Chess.find({}, {'_id': 0}).sort([('_id', -1)]))  # Sort by '_id' in descending order
        
        return jsonify(records), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@form_Basics_Of_Chess_bp.route('/form_Basics_Of_Chess_by_profile_id', methods=['GET'])
def get_form_Basics_Of_Chess_by_profile_id():
    try:
        # Extract 'profile_id' from query parameters
        profile_id = request.args.get('profile_id')

        # Validate the input
        if not profile_id:
            return jsonify({"error": "Profile ID is required"}), 400

        # Fetch the document from the collection
        record = form_Basics_Of_Chess.find_one({"profile_id": str(profile_id)}, {'_id': 0})  # Exclude MongoDB's default '_id' field

        if record:
            return jsonify(record), 200
        else:
            return jsonify({"error": "Record not found"}), 404

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@form_Basics_Of_Chess_bp.route('/form_Basics_Of_Chess_update_forms', methods=['POST'])
def update_forms():
    try:
        # Parse the incoming JSON data
        data = request.json

        # Extract the list of updates, each with an email and its associated fields
        updates = data.get('updates', [])  # Expecting a list of update objects

        # Ensure that updates are provided and it's a non-empty list
        if not updates or not isinstance(updates, list):
            return jsonify({"error": "A list of updates is required!"}), 400

        # Process each update
        update_results = []
        for update in updates:
            email = update.get('email')
            payment_status = update.get('payment_status')
            group = update.get('group')
            level = update.get('level')

            # Ensure email is provided
            if not email:
                update_results.append({"email": None, "status": "Email is required"})
                continue

            # Prepare the update data
            update_data = {
                "payment_status": payment_status,
                "group": group,
                "level": level
            }

            # Update all documents with the specified email
            result = form_Basics_Of_Chess.update_many(
                {"email": email},
                {"$set": update_data}
            )

            if result.matched_count > 0:
                update_results.append({
                    "email": email,
                    "status": f"Updated {result.modified_count} record(s) successfully"
                })
            else:
                update_results.append({"email": email, "status": "No matching email found"})

        return jsonify({"results": update_results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


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
