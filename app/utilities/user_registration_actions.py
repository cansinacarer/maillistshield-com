from app.utilities.object_storage import generate_user_folder


def new_user_actions_for_email_confirmed(user):
    # Create a user folder for them in s3
    generate_user_folder(user)

    # Reset their totp secret
    user.totp_reset_secret()
