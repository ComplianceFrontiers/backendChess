from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from app.database import schoolform_coll

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask import Blueprint, request, jsonify
from app.utils.email_utils import send_email
 

schoolform_bp = Blueprint('schoolform', __name__)

@schoolform_bp.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        # Parse the incoming JSON data
        data = request.json
        
        # Extract and validate required fields
        parent_first_name = data.get('parent_first_name')
        parent_last_name = data.get('parent_last_name')
        child_first_name = data.get('child_first_name')
        child_last_name = data.get('child_last_name')
        child_grade = data.get('child_grade')
        email = data.get('email')
        phone = data.get('phone')
        address_line_1 = data.get('address_line_1')
        address_line_2 = data.get('address_line_2')
        city = data.get('city')
        state = data.get('state')
        zip_code = data.get('zip_code')
        RequestFinancialAssistance = data.get('RequestFinancialAssistance')
        SchoolName=data.get('SchoolName')
        
        # Optional: Perform validation on the data here (e.g., check if email is valid)

        # Prepare document for MongoDB insertion
        form_data = {
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
            "address": {
                "line_1": address_line_1,
                "line_2": address_line_2,
                "city": city,
                "state": state,
                "zip_code": zip_code
            },
            "RequestFinancialAssistance":RequestFinancialAssistance,
            "SchoolName":SchoolName
        }
        

        # Insert into MongoDB
        schoolform_coll.insert_one(form_data)

        return jsonify({"message": "Form submitted successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@schoolform_bp.route('/get_forms', methods=['GET'])
def get_forms():
    try:
        # Fetch all documents from the collection
        records = list(schoolform_coll.find({}, {'_id': 0}))  # Exclude the MongoDB ID field
        
        return jsonify(records), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@schoolform_bp.route('/send-email-form', methods=['POST'])
def send_email_school_form():
    data = request.json
    email = data.get('email')
    parent_first_name = data.get('parent_first_name')
    parent_last_name = data.get('parent_last_name')
    child_first_name = data.get('child_first_name')
    child_last_name = data.get('child_last_name')
    child_grade = data.get('child_grade')
    phone = data.get('phone')
    address_line_1 = data.get('address_line_1')
    address_line_2 = data.get('address_line_2')
    city = data.get('city')
    state = data.get('state')
    zip_code = data.get('zip_code')
    request_financial_assistance = data.get('RequestFinancialAssistance')
    school_name = data.get('SchoolName', "Mount Pleasant Elementary School")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Email configuration
        sender_email = "connect@chesschamps.us"
        sender_password = "iyln tkpp vlpo sjep"  # Use your app-specific password here
        subject = "Welcome to the Chess After-School Program – Your Enrollment is Confirmed!"

        body = (
            f"Dear {parent_first_name} {parent_last_name},\n\n"
            f"Thank you for enrolling {child_first_name} {child_last_name} in the Chess After-School Program at {school_name}.\n\n"
            f"We are excited to have {child_first_name} join us for an engaging experience designed to enhance critical thinking, "
            f"problem-solving skills, and confidence through interactive chess lessons and games.\n\n"
            
            f"**Program Details:**\n"
            f"- **Program**: 10 Week Training for K-5 Students\n"
            f"- **Duration**: 25 Sep 2024 to 18 Dec 2024\n"
            f"- **Timing**: 3:30 PM - 4:30 PM\n"
            f"- **Note**: No classes on 27 Nov 2024\n\n"
            
            f"**Participant Information:**\n"
            f"- **Child's Name**: {child_first_name} {child_last_name}\n"
            f"- **Grade**: {child_grade}\n\n"
            
            f"**Contact Information:**\n"
            f"- **Phone**: {phone}\n"
            f"- **Address**: {address_line_1}, {address_line_2}, {city}, {state}, {zip_code}\n\n"
            
            f"{'**Financial Assistance**: Requested' if request_financial_assistance else '**Financial Assistance**: Not Requested'}\n\n"
            
            f"We look forward to a wonderful learning experience with {child_first_name}. If you have any questions or need further assistance, "
            f"please do not hesitate to contact us.\n\n"
            
            f"Best regards,\n"
            f"Chess Champs Team\n"
            f"connect@chesschamps.us"
        )

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the Gmail server and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()

        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

