"""User registration actions for the Mail List Shield application.

This module contains actions that are performed when a new user
confirms their email address.
"""

from app.utilities.object_storage import generate_user_folder


def new_user_actions_for_email_confirmed(user):
    """Perform setup actions for a newly email-confirmed user.

    This function is called when a user confirms their email address
    for the first time. It sets up their account resources.

    Args:
        user: The user object whose email was just confirmed.
    """
    # Create a user folder for them in s3
    generate_user_folder(user)

    # Reset their totp secret
    user.totp_reset_secret()
