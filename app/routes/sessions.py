from bson import ObjectId
from flask import Blueprint, request, jsonify
from app.database import admin_collection
import re

sessions_bp = Blueprint('sessions', __name__)

@sessions_bp.route('/add-session', methods=['POST'])
def add_session():
    data = request.json
    required_fields = ['date', 'time', 'coach_name', 'session_link']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f"'{field}' is required"}), 400

    try:
        # Add the new session to the first document in the collection
        result = admin_collection.update_one(
            {},  # match the first document
            {'$push': {'sessions': data}}
        )
        if result.modified_count == 1:
            return jsonify({'message': 'Session added successfully'}), 201
        else:
            return jsonify({'error': 'No document was updated'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sessions_bp.route('/sessions', methods=['GET'])
def view_sessions():
    try:
        sessions = list(admin_collection.find())
        for session in sessions:
            session['_id'] = str(session['_id'])
        return jsonify(sessions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sessions_bp.route('/del-sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    try:
        result = admin_collection.delete_one({'_id': ObjectId(session_id)})
        if result.deleted_count > 0:
            return jsonify({'message': 'Session deleted successfully'}), 200
        else:
            return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
