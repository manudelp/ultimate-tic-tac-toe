import os
import requests

def validate_turnstile(token, remote_ip=None):
    """Validate Cloudflare Turnstile token"""
    try:
        secret_key = os.getenv('TURNSTILE_SECRET_KEY')

        if not secret_key:
            return False, "Turnstile not configured"

        response = requests.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data={'secret': secret_key, 'response': token, 'remoteip': remote_ip},
            timeout=10
        )
        result = response.json()

        if result.get('success', False):
            return True, None

        error_codes = result.get('error-codes', [])
        return False, f"Turnstile validation failed. Errors: {error_codes}"

    except requests.exceptions.RequestException as e:
        return False, f"Network error: {str(e)}"
    except Exception as e:
        return False, f"Verification error: {str(e)}"
