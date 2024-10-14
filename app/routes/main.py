from flask import Blueprint, request, jsonify
from app.database import demo_user  # Ensure you have the correct import for your database object

# Create a Blueprint for the main application
main_bp = Blueprint('main', __name__)

@main_bp.route('/submit_answer', methods=['POST'])
def submit_answer():
    # Get the JSON data from the request
    data = request.get_json()
    print(data)
    
    # Validate the incoming data
    if not all(key in data for key in ('id', 'rollno', 'given_answer', 'actual_answer')):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Extract the data
    user_id = data['id']
    roll_no = data['rollno']
    given_answer = data['given_answer']
    actual_answer = data['actual_answer']
    
    # Prepare the document to insert into the database
    document = {
        "id": user_id,
        "rollno": roll_no,
        "given_answer": given_answer,
        "actual_answer": actual_answer
    }
    
    # Insert the document into the demo_user collection
    try:
        result = demo_user.insert_one(document)  # This returns an InsertOneResult object
        # Return the inserted document without the _id field
        document["_id"] = str(result.inserted_id)  # Optionally, include the inserted_id if needed
        return jsonify(document), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route('/')
def home():
    return "Hello, Flask on Vercel!"
