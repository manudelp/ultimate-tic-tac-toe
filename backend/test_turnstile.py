from flask import Blueprint, request, jsonify
from turnstile_utils import validate_turnstile

test_bp = Blueprint('test', __name__)

@test_bp.route('/test-turnstile', methods=['POST'])
def test_turnstile():
    """Test endpoint to validate Turnstile tokens"""
    try:
        data = request.get_json()

        if not data or 'turnstile' not in data:
            return jsonify({'valid': False, 'error': 'No Turnstile token provided'}), 400

        is_valid, error_message = validate_turnstile(data['turnstile'], request.remote_addr)

        if is_valid:
            return jsonify({'valid': True})
        else:
            return jsonify({'valid': False, 'error': error_message}), 400

    except Exception as e:
        return jsonify({'valid': False, 'error': f'Test error: {str(e)}'}), 500
