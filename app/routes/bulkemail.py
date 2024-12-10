import base64
import random
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from app.database import bulkemail

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from app.utils.email_utils import send_email
import os
from werkzeug.utils import secure_filename

bulkemail_bp = Blueprint('bulkemail', __name__)
# Define the upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Make sure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper function to check allowed image extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bulkemail_bp.route('/upload_image1', methods=['POST'])
def upload_image1():
    try:
        # Parse the incoming JSON data
        data = request.get_json()

        # Check if base64 image data is present in the request
        if 'image_data' not in data:
            return jsonify({"error": "No image data provided"}), 400

        image_data = data['image_data']
        
        # Extract the file extension from the base64 string (assuming it's in the form "data:image/png;base64,xxxx")
        if image_data.startswith('data:image'):
            # Find the file extension by locating the part after the 'data:image/' part and before ';base64'
            file_extension = image_data.split(';')[0].split('/')[1]
            if file_extension not in ALLOWED_EXTENSIONS:
                return jsonify({"error": "Invalid file type"}), 400

            # Remove the metadata part (e.g., "data:image/png;base64,") and get only the base64-encoded string
            image_data = image_data.split(',')[1]
        else:
            return jsonify({"error": "Invalid base64 image data"}), 400

        # Decode the base64 string into bytes
        image_bytes = base64.b64decode(image_data)

        # Generate a secure filename
        filename = secure_filename(f"image_{len(os.listdir(UPLOAD_FOLDER)) + 1}.{file_extension}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # Save the image as a file
        with open(file_path, 'wb') as file:
            file.write(image_bytes)

        # Generate the URL for the uploaded image
        image_url = f"https://backend-chess-tau.vercel.app/{file_path}"  # Assuming your app serves static files at this URL

        return jsonify({"image_url": image_url}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
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
