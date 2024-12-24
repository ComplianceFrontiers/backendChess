import random
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from app.database import schoolform_coll

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask import Blueprint, request, jsonify
from app.utils.email_utils import send_email
 

schoolform_bp = Blueprint('schoolform', __name__)

# Function to generate a random 6-digit profile_id
def generate_unique_profile_id():
    while True:
        profile_id = str(random.randint(100000, 999999))  # Generate a random 6-digit number
        # Check if the profile_id already exists in the database
        if schoolform_coll.count_documents({"profile_id": profile_id}) == 0:
            return profile_id

@schoolform_bp.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        # Parse the incoming JSON data
        data = request.json

        # Extract and validate required fields
        parent_first_name = data.get('parent_first_name',"")
        parent_last_name = data.get('parent_last_name',"")
        child_first_name = data.get('child_first_name',"")
        child_last_name = data.get('child_last_name',"")
        child_grade = data.get('child_grade',"")
        email = data.get('email',"")
        phone = data.get('phone',"")
        RequestFinancialAssistance = data.get('RequestFinancialAssistance',"")
        SchoolName = data.get('SchoolName',"")
        PaymentStatus = data.get('redirect_status','Not started')
        program=data.get('program','program not selected')
        Year=data.get('year',2025)
        mpes = data.get('mpes', False)  # Default to False if not provided
        lombardy = data.get('lombardy', False)  # Default to False if not provided
        jcc = data.get('jcc', False) 

        # Optional: Perform validation on the data here (e.g., check if email is valid)

        # Generate a unique profile_id
        profile_id = generate_unique_profile_id()

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
            "email": email,
            "phone": phone,
            "RequestFinancialAssistance": RequestFinancialAssistance,
            "SchoolName": SchoolName,
            "PaymentStatus":PaymentStatus,
            "year":Year,
            "program":program,
            "mpes": mpes, 
            "lombardy": lombardy,
            "jcc":jcc
        }

        # Insert into MongoDB
        schoolform_coll.insert_one(form_data)

        return jsonify({"message": "Form submitted successfully!", "profile_id": profile_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@schoolform_bp.route('/get_forms', methods=['GET'])
def get_forms():
    try:
        # Fetch all documents from the collection in descending order
        records = list(schoolform_coll.find({}, {'_id': 0}).sort([('_id', -1)]))  # Sort by '_id' in descending order
        
        return jsonify(records), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@schoolform_bp.route('/update_student_records', methods=['PUT'])
def update_student_records():
    try:
        # Parse request JSON
        data = request.json
        email = data.get("email")  # Get the email from the request body

        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Remove email from the update data to avoid updating it accidentally
        update_data = {key: value for key, value in data.items() if key != "email"}

        if not update_data:
            return jsonify({"error": "No fields to update"}), 400

        # Update the document where the email matches
        result = schoolform_coll.update_one(
            {"email": email},  # Filter by email
            {"$set": update_data}  # Update the provided fields
        )

        # Check if a document was modified
        if result.matched_count == 0:
            return jsonify({"error": "No document found for the given email"}), 404

        return jsonify({"message": "Document updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@schoolform_bp.route('/get_forms_group', methods=['GET'])
def get_forms_by_group():
    try:
        # Get query parameters from the request
        group = request.args.get('group')  # Fetch 'group' parameter from the query string

        # Build the filter condition dynamically
        filter_condition = {}
        if group:
            filter_condition['group'] = group

        # Fetch documents matching the dynamic filter condition
        records = list(schoolform_coll.find(filter_condition, {'_id': 0}))  # Exclude the MongoDB ID field

        return jsonify(records), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@schoolform_bp.route('/send-email-form-lombardy', methods=['POST'])
def send_email_school_form_lombardy():
    data = request.json
    email = data.get('email')
   

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Email configuration
        DISPLAY_NAME="Chess Champs Academy"
        sender_email = "connect@chesschamps.us"
        sender_password = "iyln tkpp vlpo sjep"  # Use your app-specific password here
        subject = "Lombardy Chess Program!"

        body = (
            "Dear Parents,\n\n"
            "We are excited to welcome your child to the after-school chess program at Lombardy Elementary! Thank you for trusting us with your child's chess development and for encouraging their interest in this wonderful game.\n\n"
            "At Chess Champs, we believe that chess not only sharpens minds but also nurtures critical thinking, problem-solving, and concentration skills. Our program is designed to be both fun and educational, and we are committed to making this an enriching experience for your child.\n\n"
            "We have a fantastic lineup of activities planned. Throughout the program, your child will learn valuable chess strategies, participate in friendly matches, and develop their confidence both on and off the board.\n\n"
            "Please don't hesitate to reach out to us if you have any questions or need further information.\n\n"
            "Once again, thank you for enrolling your child in our program. We look forward to an exciting journey ahead!\n\n"
            "Best regards ,\n\n"
            
            "Training Team\n"
            "Chess Champs Academy"
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



@schoolform_bp.route('/send-email-form-mpes', methods=['POST'])
def send_email_school_form_mpes():
    data = request.json
    email = data.get('email')
   

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Email configuration
        DISPLAY_NAME="Chess Champs Academy"
        sender_email = "connect@chesschamps.us"
        sender_password = "iyln tkpp vlpo sjep"  # Use your app-specific password here
        subject = "MPE Chess Program!"

        body = (
            "Dear Parents,\n\n"
            "We are excited to welcome your child to the after-school chess program at Mount Pleasant Elementary! Thank you for trusting us with your child's chess development and for encouraging their interest in this wonderful game.\n\n"
            "At Chess Champs, we believe that chess not only sharpens minds but also nurtures critical thinking, problem-solving, and concentration skills. Our program is designed to be both fun and educational, and we are committed to making this an enriching experience for your child.\n\n"
            "We have a fantastic lineup of activities planned. Throughout the program, your child will learn valuable chess strategies, participate in friendly matches, and develop their confidence both on and off the board.\n\n"
            "Please don't hesitate to reach out to us if you have any questions or need further information.\n\n"
            "Once again, thank you for enrolling your child in our program. We look forward to an exciting journey ahead!\n\n"
            "Best regards ,\n\n"
            
            "Training Team\n"
            "Chess Champs Academy"
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


@schoolform_bp.route('/send-email-form-jcc', methods=['POST'])
def send_email_school_form_jcc():
    data = request.json
    email = data.get('email')
   

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Email configuration
        DISPLAY_NAME="Chess Champs Academy"
        sender_email = "connect@chesschamps.us"
        sender_password = "iyln tkpp vlpo sjep"  # Use your app-specific password here
        subject = "Chess Program at JCC!"
        body = (
                "Dear Parents,\n\n"
                "We are excited to welcome your child to the chess program at J!\n\n"
                "Thank you for trusting us with your child's chess development and for encouraging their interest in this wonderful game. "
                "At Chess Champs, we believe that chess not only sharpens minds but also nurtures critical thinking, problem-solving, and concentration skills.\n\n"
                "Our program is designed to be both fun and educational, and we are committed to making this an enriching experience for your child. "
                "We have a fantastic lineup of activities planned. Throughout the program, your child will learn valuable chess strategies, participate in friendly matches, "
                "and develop their confidence both on and off the board.\n\n"
                "Please don't hesitate to reach out to us if you have any questions or need further information.\n\n"
                "Once again, thank you for enrolling your child in our program. We look forward to an exciting journey ahead!\n\n"
                "Best regards,\n\n"
                "Training Team\n"
                "Chess Champs"
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


@schoolform_bp.route('/update_forms', methods=['POST'])
def update_forms():
    try:
        # Parse the incoming JSON data
        data = request.json

        # Extract the list of updates, each with a profile_id and its associated fields
        updates = data.get('updates', [])  # Expecting a list of update objects

        # Ensure that updates are provided and it's a non-empty list
        if not updates or not isinstance(updates, list):
            return jsonify({"error": "A list of updates is required!"}), 400

        # Process each update
        update_results = []
        for update in updates:
            profile_id = update.get('profile_id')
            payment_status = update.get('payment_status')
            group = update.get('group')
            level = update.get('level')

            # Ensure profile_id is provided
            if not profile_id:
                update_results.append({"profile_id": None, "status": "Profile ID is required"})
                continue

            # Prepare the update data
            update_data = {
                "payment_status": payment_status,
                "group": group,
                "level": level
            }

            # Update the document
            result = schoolform_coll.update_one(
                {"profile_id": profile_id},
                {"$set": update_data}
            )

            if result.matched_count > 0:
                update_results.append({"profile_id": profile_id, "status": "Updated successfully"})
            else:
                update_results.append({"profile_id": profile_id, "status": "No matching profile ID found"})

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
            f"Our training videos are optimized for desktop viewing, though a mobile version is available. Please note the mobile experience may be slightly glitchy, and we are actively working to improve it. "
            f"Thank you for your patience and continued support.\n\n"
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

@schoolform_bp.route('/send_mails_for_updated_records', methods=['POST'])
def send_mails_for_updated_records():
    try:
        # Parse the incoming JSON data
        data = request.json

        # Extract the updates
        updates = data.get('updates', [])

        if not updates:
            return jsonify({"error": "No updates provided!"}), 400

        for update in updates:
            profile_id = update.get('profile_id')
            group = update.get('group')
            email = update.get('email')

            if not profile_id or not email:
                return jsonify({"error": "Profile ID and email are required for each update!"}), 400

            # Determine the online portal link based on the group
            if group == "In School Program":
                online_portal_link = "https://chess-in-school.vercel.app/"
            else:
                online_portal_link = "https://chess-learning-platform.vercel.app/"

            # Send the email
            if not send_email(email, online_portal_link):
                return jsonify({"status": "Failed to send email for some updates."}), 500

        return jsonify({"status": "Emails sent successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400