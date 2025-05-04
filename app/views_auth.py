# Python modules
from datetime import datetime, timezone
import requests
import json
import random
import string
from itsdangerous import URLSafeTimedSerializer

# Flask modules
from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    abort,
    session,
    current_app,
)
from flask_login import (
    login_user,
    logout_user,
    current_user,
)
from werkzeug.exceptions import HTTPException, NotFound
from jinja2 import TemplateNotFound


# App modules
from app import lm, db, bc, csrf
from app.models import Users
from app.forms import (
    LoginForm,
    RegisterForm,
    EmailConfirmationForm,
    ResetPassword,
    SetNewPassword,
    TwoFactorAuthenticationForm,
)
from app.views import limiter
from app.config import appTimezone
from app.emails import send_email_with_code, send_email_to_reset_password
from app.utilities.user_registration_actions import new_user_actions_for_email_confirmed
from app.utilities.helpers import generate_n_digit_code
from app.utilities.error_handlers import error_page
from app.utilities.recaptcha import verify_recaptcha

auth_bp = Blueprint("auth_bp", __name__)


@lm.user_loader
def load_user(user_id):
    """This function is used to load the user object from the user ID stored in the session.

    Args:
        user_id (str): The ID of the user to load.

    Returns:
        Users: The user object from the db corresponding to the user ID.
    """
    return Users.query.get(int(user_id))


@lm.unauthorized_handler
def unauthorized_callback():
    """This function is used to handle unauthorized access to protected routes.

    403 cases will be redirected to login
    """
    return redirect("/login?next=" + request.path)


@auth_bp.route("/logout")
def logout():
    """This function is used to log out the user and redirect them to the login page."""
    logout_user()
    return redirect(url_for("auth_bp.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per day", methods=["POST"])
def register():
    """The view function for the registration page."""

    # Don't allow logged in users here
    if current_user.is_authenticated:
        flash("You are already registered.", "info")
        return redirect("/app")

    # Declare the form
    form = RegisterForm(request.form)

    success = False

    if request.method == "GET":
        return render_template(
            "public/auth/register.html", form=form, user=current_user
        )

    # Check if both http method is POST, form is valid, and csrf token is valid
    if form.validate_on_submit():
        # Verify reCAPTCHA
        recaptcha_response = request.form.get("g-recaptcha-response")
        recaptcha_verified = verify_recaptcha(recaptcha_response, request.remote_addr)

        if not recaptcha_verified:
            flash(
                'Please check the box next to the phrase "I\'m not a robot".', "danger"
            )
            return render_template(
                "public/auth/register.html", form=form, success=False, user=current_user
            )

        # assign form data to variables
        email = request.form.get("email", "", type=str)
        password = request.form.get("password", "", type=str)
        firstName = request.form.get("firstName", "", type=str)
        lastName = request.form.get("lastName", "", type=str)
        newsletter = "0" if request.form.get("newsletter", "0") == "0" else "1"

        # Log current date
        member_since = datetime.now(timezone.utc).replace(tzinfo=None)
        last_login = datetime.now(timezone.utc).replace(tzinfo=None)

        # filter User out of database through user email
        user_by_email = Users.query.filter_by(email=email).first()

        if user_by_email:
            flash("Error: User exists!", "danger")

        else:
            pw_hash = bc.generate_password_hash(password).decode("utf8")
            tier_id = 1
            email_confirmation_code = generate_n_digit_code(6)

            user = Users(
                email,
                pw_hash,
                tier_id,
                firstName,
                lastName,
                newsletter,
                member_since,
                last_login,
                email_confirmation_code,
            )

            user.save()
            success = True

    else:
        flash("Please make sure you fill all the required fields.", "danger")

    if success:
        login_user(user, remember=True)
        send_email_with_code(current_user)
        return redirect(url_for("auth_bp.email_confirmation_by_code"))
    else:
        return render_template(
            "public/auth/register.html", form=form, success=success, user=current_user
        )


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per day", methods=["POST"])
def login():
    """The view function for the login page."""

    # Don't allow logged in users here
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect("/app")

    if request.method == "GET":
        # If user came here with the login with Google button
        if request.args.get("sso") == "google":
            # Single Sign On requests with Google
            google_config = get_google_sso_config()
            endpoint = google_config["authorization_endpoint"]

            # Preserve next url if it exists
            request_uri = current_app.google_client.prepare_request_uri(
                endpoint,
                redirect_uri="https://" + request.host + "/login/callback/google",
                scope=["openid", "email", "profile"],
                state=request.args.get("next"),
            )

            return redirect(request_uri)

    # Declare the form
    form = LoginForm(request.form)

    # Check if both http method is POST, form is valid, and csrf token is valid
    if form.validate_on_submit():
        # Verify reCAPTCHA
        recaptcha_response = request.form.get("g-recaptcha-response")
        recaptcha_verified = verify_recaptcha(recaptcha_response, request.remote_addr)

        if not recaptcha_verified:
            flash(
                'Please check the box next to the phrase "I\'m not a robot".', "danger"
            )
            return render_template(
                "public/auth/login.html", form=form, success=False, user=current_user
            )

        # Assign form data to variables
        email = request.form.get("email", "", type=str)
        password = request.form.get("password", "", type=str)

        # Filter User out of database through username
        user = Users.query.filter_by(email=email).first()
        if user and bc.check_password_hash(user.password, password):
            # If the user have two factor auth enabled, redirect for that
            if user.totp_enabled == 1:
                session["email"] = user.email
                redirect_url = "/two-factor"

                if "next" in request.args:
                    redirect_url += "?next=" + request.args["next"]
                return redirect(redirect_url)

            # Otherwise log them in
            else:
                login_user(user)
                current_user.last_login = datetime.now(timezone.utc).astimezone(
                    appTimezone
                )
                current_user.save()
                if "next" in request.args:
                    return redirect(request.args["next"])
                else:
                    return redirect(url_for("private_bp.private_index"))
        else:
            flash("Incorrect username or password. Please try again.", "danger")

    # Preserve next url the user was going before login redirect, if it exists
    next = request.args["next"] if "next" in request.args else "/app"

    return render_template(
        "public/auth/login.html", form=form, user=current_user, next=next
    )


@auth_bp.route("/two-factor", methods=["GET", "POST"])
@limiter.limit("10 per day", methods=["POST"])
def two_factor():
    """The view function for the two factor authentication page."""

    # Don't allow logged in users here
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect("/app")

    # If the user isn't redirected with a successful login
    if "email" not in session:
        return redirect(url_for("auth_bp.login"))

    user = Users.query.filter_by(email=session["email"]).first()

    # This shouldn't happen but if it does:
    if user is None:
        flash("Something went wrong during two factor authentication.", "danger")
        return redirect(url_for("auth_bp.login"))

    # Declare the form
    form = TwoFactorAuthenticationForm(request.form)

    # If it is a GET request, just show the page
    if request.method == "GET":
        return render_template(
            "public/auth/two-factor-auth.html", form=form, user=current_user
        )

    # Check if both http method is POST, form is valid, and csrf token is valid
    if form.validate_on_submit():
        entered_code = ""
        try:
            for i in range(0, 6):
                entered_code += request.form["code" + str(i)]
        except:
            flash("Please enter a valid code before submitting.", "danger")
            return render_template(
                "public/auth/two-factor-auth.html", form=form, user=current_user
            )

        codeMatched = user.totp_match(entered_code)
        if codeMatched:
            login_user(user)
            current_user.last_login = datetime.now(timezone.utc).replace(tzinfo=None)
            current_user.save()
            if "next" in request.args:
                return redirect(request.args["next"])
            else:
                return redirect(url_for("private_bp.private_index"))
        else:
            flash("This code was not correct.", "danger")
            return render_template(
                "public/auth/two-factor-auth.html", form=form, user=current_user
            )
    else:
        flash("Please enter a valid code before submitting.", "danger")
        return render_template(
            "public/auth/two-factor-auth.html", form=form, user=current_user
        )


@auth_bp.route("/email-confirmation", methods=["GET", "POST"])
def email_confirmation_by_code():
    """The view function for the email verification page."""

    codeMatched = True

    if not current_user.is_authenticated:
        flash("Please login before verifying your email address.", "info")
        return redirect(
            url_for("auth_bp.login")
            + "?next="
            + url_for("auth_bp.email_confirmation_by_code")
        )
    elif current_user.email_confirmed == 0:
        # Verification code
        code = current_user.email_confirmation_code

        # Declare the form
        form = EmailConfirmationForm(request.form)

        # If it is a GET request, just show the page
        if request.method == "GET":
            if "resend" in request.args:
                send_email_with_code(current_user)
            return render_template(
                "public/auth/email-confirm.html", form=form, user=current_user
            )

        # Check if both http method is POST, form is valid, and csrf token is valid
        if form.validate_on_submit():
            for i in range(0, 6):
                codeMatched = codeMatched and request.form["code" + str(i)] == code[i]
            if codeMatched:
                # Run the new user actions
                new_user_actions_for_email_confirmed(current_user)

                # Change user attribute in the db
                current_user.email_confirmed = 1
                current_user.save()

                # Flash conformation
                flash(
                    "Thank you for confirming your email address!", category="success"
                )

                return redirect(url_for("private_bp.private_index"))
            else:
                flash("This code was not correct.", "danger")
                return render_template(
                    "public/auth/email-confirm.html", form=form, user=current_user
                )
        else:
            flash("Please enter a valid code before submitting.", "danger")
            return render_template(
                "public/auth/email-confirm.html", form=form, user=current_user
            )
    else:
        flash("Your email address is already confirmed.", "info")
        return redirect(url_for("private_bp.private_index"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("1 per day", methods=["POST"])
def password_reset():
    """The view function for the password reset page."""

    # Declare the form
    form = ResetPassword(request.form)

    if request.method == "GET":
        return render_template(
            "public/auth/password-reset.html", form=form, user=current_user
        )

    # Check if both http method is POST, form is valid, and csrf token is valid
    if form.validate_on_submit():
        email = request.form.get("email", "", type=str)
        user = Users.query.filter_by(email=email).first()

        if user:
            send_email_to_reset_password(email)

    #  Whatever happens, redirect to the information page without telling what happened
    return redirect(url_for("auth_bp.password_reset_requested"))


@auth_bp.route("/password-reset-requested")
def password_reset_requested():
    """The view function for the password reset requested page."""

    return render_template(
        "public/auth/password-reset-requested.html", user=current_user
    )


@auth_bp.route("/set-new-password", methods=["GET", "POST"], defaults={"token": ""})
@auth_bp.route("/set-new-password/<token>", methods=["GET", "POST"])
def set_new_password(token):
    """The view function for the set new password page.

    Args:
        token (str): The token from the forgot password email, used to verify the user.
    """

    try:
        ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        email = ts.loads(token, salt="recover-key", max_age=86400)
    except:
        abort(404)

    # Declare the form
    form = SetNewPassword()

    # Check if both http method is POST, form is valid, and csrf token is valid
    if form.validate_on_submit():
        user = Users.query.filter_by(email=email).first_or_404()

        user.password = bc.generate_password_hash(form.password.data).decode("utf8")

        db.session.add(user)
        db.session.commit()

        flash(
            "Your password has been reset successfully. Please login with your new password.",
            "info",
        )
        return redirect(url_for("auth_bp.login"))

    return render_template(
        "public/auth/new-password.html", form=form, user=current_user
    )


def get_google_sso_config():
    """Get the Google SSO configuration.

    Returns:
        dict: The Google SSO configuration.
    """
    return requests.get(
        "https://accounts.google.com/.well-known/openid-configuration"
    ).json()


@auth_bp.route("/login/callback/google", methods=["GET", "POST"])
@csrf.exempt
def login_callback_google():
    """The view function for the Google login callback.

    This is the page that Google redirects to after the Google authentication attempt.
    """

    # Don't allow logged in users here
    if current_user.is_authenticated and current_user.is_connected_google():
        flash("You are already logged in.", "info")
        return redirect("/app")

    # Handling the case where the callback has an error arg
    if request.args.get("error") is not None:
        print(
            "Error on callback, redirecting to login.\nError from Google: ",
            request.args.get("error"),
        )
        flash("Google authentication was not completed. Please try again.", "danger")
        return redirect("/login")

    # Get authorization code Google sent back to you
    code = request.args.get("code")
    google_config = get_google_sso_config()
    token_endpoint = google_config["token_endpoint"]

    # Prepare and send a request to get tokens!
    token_url, headers, body = current_app.google_client.prepare_token_request(
        token_endpoint,
        authorization_response="https://" + request.host + request.full_path,
        redirect_url="https://" + request.host + request.path,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(
            current_app.config["GOOGLE_CLIENT_ID"],
            current_app.config["GOOGLE_CLIENT_SECRET"],
        ),
    )

    # Parse the tokens
    current_app.google_client.parse_request_body_response(
        json.dumps(token_response.json())
    )

    userinfo_endpoint = google_config["userinfo_endpoint"]
    uri, headers, body = current_app.google_client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    user_info_json = userinfo_response.json()

    if user_info_json["email_verified"]:
        google_user_email = user_info_json.get("email", "")
        google_user_picture = user_info_json.get("picture", "")
        google_user_given_name = user_info_json.get("given_name", "")
        google_user_family_name = user_info_json.get("family_name", "")

        # Is this email already registered?
        # Covers both the people signed up with email and the people logged in with social before
        found_user = Users.query.filter_by(email=google_user_email).first()
        if found_user:
            # Update their missing info - These would be missing for email sign-up
            if found_user.google_avatar_url == None:
                found_user.google_avatar_url = google_user_picture
            if not found_user.email_confirmed == 1:
                found_user.email_confirmed = 1
                flash("Your email address is verified!", category="success")
            if found_user.firstName == None:
                found_user.firstName = google_user_given_name
            if found_user.lastName == None:
                found_user.lastName = google_user_family_name
            db.session.commit()

            # Log current date
            member_since = datetime.now(timezone.utc).replace(tzinfo=None)

            # Log them in
            login_user(found_user, remember=True)
            current_user.last_login = datetime.now(timezone.utc).replace(tzinfo=None)
            current_user.save()

            flash("Logged in with Google successfully!", category="success")

        # If we didn't have a record for this user
        else:
            # Assign them a random password
            letter_set = string.ascii_lowercase
            random_password = "".join(random.choice(letter_set) for i in range(16))

            # Log current date
            member_since = datetime.now(timezone.utc).replace(tzinfo=None)
            last_login = datetime.now(timezone.utc).replace(tzinfo=None)

            # Register them as new user
            new_user = Users(
                email=google_user_email,
                password=bc.generate_password_hash(random_password).decode("utf8"),
                tier_id=1,
                firstName=google_user_given_name,
                lastName=google_user_family_name,
                newsletter=0,
                member_since=member_since,
                last_login=last_login,
                email_confirmation_code=generate_n_digit_code(6),
            )
            db.session.add(new_user)
            db.session.commit()
            user = Users.query.filter_by(email=google_user_email).first()

            # Run the new user actions
            new_user_actions_for_email_confirmed(user)
            login_user(user, remember=True)

            # We know Google confirmed their email already
            if not user.email_confirmed == 1:
                user.email_confirmed = 1
                user.google_avatar_url = google_user_picture
                user.save()

            flash(
                "Your account is created successfully.",
                category="success",
            )

        # We preserved the next page to go to after login in the oauth state earlier, reading it back here
        next = request.args.get("state", "/app")
        return redirect(next)
    else:
        flash(
            "Your Google email not available or not verified by Google. Please set up your Google email first or try using a different email address.",
            "danger",
        )
        return redirect(url_for("auth_bp.login"))
