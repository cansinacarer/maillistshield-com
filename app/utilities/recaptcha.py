"""reCAPTCHA verification utilities for the Mail List Shield application.

This module provides functions for verifying Google reCAPTCHA v2 responses
to protect forms from automated submissions.
"""

import requests

from flask import current_app


def verify_recaptcha(recaptcha_response, remote_ip):
    """Verify the reCAPTCHA response.

    Args:
        recaptcha_response (str): The response token from the reCAPTCHA widget.
        remote_ip (str): The IP address of the user.

    Returns:
        bool: True if verification succeeded, False otherwise.
    """
    if not recaptcha_response:
        return False

    data = {
        "secret": current_app.config["RECAPTCHA_SECRET_KEY"],
        "response": recaptcha_response,
        "remoteip": remote_ip,
    }

    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify", data=data
    )

    result = response.json()
    return result.get("success", False)
