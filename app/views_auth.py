# Python modules
from cgi import test
from imghdr import tests
from datetime import datetime, timezone
from oauthlib.oauth2 import WebApplicationClient
import requests
import json
import random
import string

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
)
from flask_login import (
    login_user,
    logout_user,
    current_user,
)
from werkzeug.exceptions import HTTPException, NotFound
from jinja2 import TemplateNotFound


# App modules
from app import app, lm, db, bc
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
from app.emails import send_email_with_code, send_email_to_reset_password, ts
from app.utilities.user_registration_actions import new_user_actions_for_email_confirmed
from app.utilities.helpers import generate_n_digit_code
from app.utilities.error_handlers import error_page

app_auth = Blueprint("views_auth", __name__)


# provide login manager with load_user callback
# This callback is used to reload the user object from the user ID stored in the session.
@lm.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Google OAuth 2 client configuration
google_client = WebApplicationClient(app.config["GOOGLE_CLIENT_ID"])


# 403 cases will be redirected to login
@lm.unauthorized_handler
def unauthorized_callback():
    return redirect("/login?next=" + request.path)


# Logout user
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


# Register a new user
@app.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per day", methods=["POST"])
def register():
    # Don't allow logged in users here
    if current_user.is_authenticated:
        flash("You are already registered.", "info")
        return redirect("/app")

    # Declare the registration form
    form = RegisterForm(request.form)

    success = False

    if request.method == "GET":
        return render_template(
            "public/auth/register.html", form=form, user=current_user
        )

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        email = request.form.get("email", "", type=str)
        password = request.form.get("password", "", type=str)
        firstName = request.form.get("firstName", "", type=str)
        lastName = request.form.get("lastName", "", type=str)
        newsletter = "0" if request.form.get("newsletter", "0") == "0" else "1"

        # Log current date
        member_since = datetime.now(timezone.utc).astimezone(appTimezone)
        last_login = datetime.now(timezone.utc).astimezone(appTimezone)

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
        return redirect(url_for("email_confirmation_by_code"))
    else:
        return render_template(
            "public/auth/register.html", form=form, success=success, user=current_user
        )


# Authenticate user
@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per day", methods=["POST"])
def login():

    if request.method == "GET":
        # If user came here with the login with Google button
        if request.args.get("sso") == "google":

            # Single Sign On requests with Google
            google_config = get_google_sso_config()
            endpoint = google_config["authorization_endpoint"]

            # Preserve next url if it exists
            request_uri = google_client.prepare_request_uri(
                endpoint,
                redirect_uri="https://" + request.host + "/login/callback/google",
                scope=["openid", "email", "profile"],
                state=request.args.get("next"),
            )

            return redirect(request_uri)

    # Don't allow logged in users here
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect("/app")

    # Declare the login form
    form = LoginForm(request.form)

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        email = request.form.get("email", "", type=str)
        password = request.form.get("password", "", type=str)

        # filter User out of database through username
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
                    return redirect(url_for("views_private.private_index"))
        else:
            flash("Incorrect username or password. Please try again.", "danger")

    # Preserve next url the user was going before login redirect, if it exists
    next = request.args["next"] if "next" in request.args else "/app"

    return render_template(
        "public/auth/login.html", form=form, user=current_user, next=next
    )


# Authenticate user with the second factor
@app_auth.route("/two-factor", methods=["GET", "POST"])
@limiter.limit("10 per day", methods=["POST"])
def two_factor():

    # Don't allow logged in users here
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect("/app")

    # If the user isn't redirected with a successful login
    if "email" not in session:
        return redirect(url_for("views_auth.login"))

    user = Users.query.filter_by(email=session["email"]).first()

    # This shouldn't happen but if it does:
    if user is None:
        flash("Something went wrong during two factor authentication.", "danger")
        return redirect(url_for("views_auth.login"))

    # Declare the two factor auth form
    form = TwoFactorAuthenticationForm(request.form)

    # If it is a GET request, just show the page
    if request.method == "GET":
        return render_template(
            "public/auth/two-factor-auth.html", form=form, user=current_user
        )

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
            current_user.last_login = datetime.now(timezone.utc).astimezone(appTimezone)
            current_user.save()
            if "next" in request.args:
                return redirect(request.args["next"])
            else:
                return redirect(url_for("views_private.private_index"))
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


# email verification by sending the user an email with a code
@app.route("/email-confirmation", methods=["GET", "POST"])
def email_confirmation_by_code():
    codeMatched = True

    if not current_user.is_authenticated:
        flash("Please login before verifying your email address.", "info")
        return redirect(
            url_for("login") + "?next=" + url_for("email_confirmation_by_code")
        )
    elif current_user.email_confirmed == 0:
        # Verification code
        code = current_user.email_confirmation_code

        # Declare the login form
        form = EmailConfirmationForm(request.form)

        # If it is a GET request, just show the page
        if request.method == "GET":
            if "resend" in request.args:
                send_email_with_code(current_user)
            return render_template(
                "public/auth/email-confirm.html", form=form, user=current_user
            )

        if form.validate_on_submit():
            for i in range(0, 6):
                codeMatched = codeMatched and request.form["code" + str(i)] == code[i]
            if codeMatched:
                # Run the new user actions
                new_user_actions_for_email_confirmed(current_user)

                # change user attribute in the db
                current_user.email_confirmed = 1
                current_user.save()
                # Flash conformation
                flash(
                    "Thank you for confirming your email address!", category="success"
                )

                return redirect(url_for("views_private.private_index"))
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
        return redirect(url_for("views_private.private_index"))


# Password Reset
@app.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("1 per day", methods=["POST"])
def password_reset():
    # Declare the login form
    form = ResetPassword(request.form)

    if request.method == "GET":
        return render_template(
            "public/auth/password-reset.html", form=form, user=current_user
        )

    if form.validate_on_submit():
        email = request.form.get("email", "", type=str)
        user = Users.query.filter_by(email=email).first()

        if user:
            send_email_to_reset_password(email)

    #  Whatever happens, redirect to the information page without telling what happened
    return redirect(url_for("password_reset_requested"))


# password reset requested
@app.route("/password-reset-requested")
def password_reset_requested():
    return render_template(
        "public/auth/password-reset-requested.html", user=current_user
    )


# Set new password
@app.route("/set-new-password", methods=["GET", "POST"], defaults={"token": ""})
@app.route("/set-new-password/<token>", methods=["GET", "POST"])
def set_new_password(token):
    try:
        email = ts.loads(token, salt="recover-key", max_age=86400)
    except:
        abort(404)

    form = SetNewPassword()

    if form.validate_on_submit():
        user = Users.query.filter_by(email=email).first_or_404()

        user.password = bc.generate_password_hash(form.password.data).decode("utf8")

        db.session.add(user)
        db.session.commit()

        flash(
            "Your password has been reset successfully. Please login with your new password.",
            "info",
        )
        return redirect(url_for("login"))

    return render_template(
        "public/auth/new-password.html", form=form, user=current_user
    )


def get_google_sso_config():
    return requests.get(
        "https://accounts.google.com/.well-known/openid-configuration"
    ).json()


@app_auth.route("/login/callback/google", methods=["GET", "POST"])
def login_callback_google():
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
    token_url, headers, body = google_client.prepare_token_request(
        token_endpoint,
        authorization_response="https://" + request.host + request.full_path,
        redirect_url="https://" + request.host + request.path,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(app.config["GOOGLE_CLIENT_ID"], app.config["GOOGLE_CLIENT_SECRET"]),
    )

    # Parse the tokens
    google_client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_config["userinfo_endpoint"]
    uri, headers, body = google_client.add_token(userinfo_endpoint)
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
            member_since = datetime.now(timezone.utc).astimezone(appTimezone)

            # Log them in
            login_user(found_user, remember=True)
            current_user.last_login = datetime.now(timezone.utc).astimezone(appTimezone)
            current_user.save()

            flash("Logged in with Google successfully!", category="success")

        # If we didn't have a record for this user
        else:
            # Assign them a random password
            letter_set = string.ascii_lowercase
            random_password = "".join(random.choice(letter_set) for i in range(16))

            # Log current date
            member_since = datetime.now(timezone.utc).astimezone(appTimezone)
            last_login = datetime.now(timezone.utc).astimezone(appTimezone)

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
        return redirect(url_for("login"))
