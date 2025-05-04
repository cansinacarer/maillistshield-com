from datetime import datetime, timezone, timedelta
from itsdangerous import URLSafeTimedSerializer

from flask import flash, render_template, url_for, current_app
from flask_mail import Message

from app import mail
from app.config import appTimezone
from app.decorators import asyncr
from app.models import Users


def send_email_to_reset_password(email):
    """Send an email with the password reset link.

    Args:
        email (str): The email address of the user.

    """

    # Tokenize the email address
    ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    token = ts.dumps(email, salt="recover-key")
    resetLink = url_for("auth_bp.set_new_password", _external=True) + "/" + token

    user = Users.query.filter_by(email=email).first_or_404()

    # Email with this information:
    msg = Message("Password Reset")
    msg.add_recipient(email)
    msg.sender = (current_app.config["APP_NAME"], current_app.config["MAIL_FROM"])
    msg.body = render_template(
        "emails/password-reset.txt",
        user=user,
        appName=current_app.config["APP_NAME"],
        appHome=current_app.config["APP_ROOT_URL"],
        resetLink=resetLink,
    )
    msg.html = render_template(
        "emails/password-reset.html",
        user=user,
        appName=current_app.config["APP_NAME"],
        appHome=current_app.config["APP_ROOT_URL"],
        resetLink=resetLink,
    )
    send_async_email(msg, current_app._get_current_object())


def send_email_with_code(user):
    """Send an email with the verification code.

    Args:
        user (Users): The user object.
    """

    # If last confirmation email was sent more than 60 seconds ago
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    last_sent = user.last_confirmation_codes_sent
    long_enough_since_last_email = last_sent + timedelta(minutes=1) < now

    # If total number of confirmation emails sent is not greater than 5:
    max_email_limit_reached = user.number_of_email_confirmation_codes_sent == 5

    if long_enough_since_last_email and not max_email_limit_reached:
        # Email with this information:
        msg = Message("Verification Code")
        msg.add_recipient(user.email)
        msg.sender = (current_app.config["APP_NAME"], current_app.config["MAIL_FROM"])
        msg.body = render_template(
            "emails/email-verification-code.txt",
            user=user,
            appName=current_app.config["APP_NAME"],
            appHome=current_app.config["APP_ROOT_URL"],
        )
        msg.html = render_template(
            "emails/email-verification-code.html",
            user=user,
            appName=current_app.config["APP_NAME"],
            appHome=current_app.config["APP_ROOT_URL"],
        )
        send_async_email(msg, current_app._get_current_object())

        user.number_of_email_confirmation_codes_sent += 1
        user.last_confirmation_codes_sent = datetime.now(timezone.utc).replace(
            tzinfo=None
        )
        user.save()
        flash(
            f"We have sent your verification code to {user.email}.",
            "info",
        )
    elif max_email_limit_reached:
        flash(
            "We are not able to send more than 5 verification emails. Please contact us if you think you are seeing this message by error.",
            "danger",
        )
    else:
        flash(
            "Please wait for 60 seconds before requesting another email to be sent.",
            "danger",
        )


def send_email_about_subscription_confirmation(user, tier_name):
    """Send an email with the paid subscription confirmation.

    Args:
        user (Users): The user object.
        tier_name (str): The name of the subscription tier.
    """

    # Email with this information:
    msg = Message("Subscription Confirmed")
    msg.add_recipient(user.email)
    msg.sender = (current_app.config["APP_NAME"], current_app.config["MAIL_FROM"])
    msg.body = render_template(
        "emails/email-subscription-confirmed.txt",
        user=user,
        appName=current_app.config["APP_NAME"],
        appHome=current_app.config["APP_ROOT_URL"],
        tier_name=tier_name,
    )
    msg.html = render_template(
        "emails/email-subscription-confirmed.html",
        user=user,
        appName=current_app.config["APP_NAME"],
        appHome=current_app.config["APP_ROOT_URL"],
        tier_name=tier_name,
    )
    send_async_email(msg, current_app._get_current_object())


def send_email_about_subscription_cancellation(user, tier_name, cancellation_date):
    """Send an email with the subscription cancellation information.

    This is the email sent when the user cancels their subscription but the subscription
    is still active until the end of the billing period.

    Args:
        user (Users): The user object.
        tier_name (str): The name of the subscription tier.
        cancellation_date (datetime): The date of cancellation.
    """
    # Email with this information:
    msg = Message("Subscription Canceled")
    msg.add_recipient(user.email)
    msg.sender = (current_app.config["APP_NAME"], current_app.config["MAIL_FROM"])
    msg.body = render_template(
        "emails/email-subscription-canceled.txt",
        user=user,
        appName=current_app.config["APP_NAME"],
        appHome=current_app.config["APP_ROOT_URL"],
        tier_name=tier_name,
        cancellation_date=cancellation_date,
    )
    msg.html = render_template(
        "emails/email-subscription-canceled.html",
        user=user,
        appName=current_app.config["APP_NAME"],
        appHome=current_app.config["APP_ROOT_URL"],
        tier_name=tier_name,
        cancellation_date=cancellation_date,
    )
    send_async_email(msg, current_app._get_current_object())


def send_email_about_subscription_deletion(user, tier_name):
    """Send an email with the subscription deletion information.

    This is the email sent when the subscription has ended.

    Args:
        user (Users): The user object.
        tier_name (str): The name of the subscription tier.
    """

    # Email with this information:
    msg = Message("Subscription Ended")
    msg.add_recipient(user.email)
    msg.sender = (current_app.config["APP_NAME"], current_app.config["MAIL_FROM"])
    msg.body = render_template(
        "emails/email-subscription-deleted.txt",
        user=user,
        appName=current_app.config["APP_NAME"],
        appHome=current_app.config["APP_ROOT_URL"],
        tier_name=tier_name,
    )
    msg.html = render_template(
        "emails/email-subscription-deleted.html",
        user=user,
        appName=current_app.config["APP_NAME"],
        appHome=current_app.config["APP_ROOT_URL"],
        tier_name=tier_name,
    )
    send_async_email(msg, current_app._get_current_object())


# Async emailing - all information is passed in an instance of the Message object
@asyncr
def send_async_email(msg, app):
    """Send an email asynchronously.

    Args:
        msg (Message): The Message object containing email details.
        app (Flask): The Flask application instance.
    """
    with app.app_context():
        mail.send(msg)
