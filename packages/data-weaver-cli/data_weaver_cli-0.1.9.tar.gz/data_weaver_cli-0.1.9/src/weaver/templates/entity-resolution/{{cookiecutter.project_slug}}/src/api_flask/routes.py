from flask import Blueprint, jsonify

api = Blueprint('api', __name__)


@api.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'Flask API is running'
    })