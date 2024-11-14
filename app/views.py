from flask import render_template, request, redirect, Response, jsonify
from flask_login import login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from jinja2 import TemplateNotFound
from datetime import datetime

from app import app, lm, db
from app.models import Users, BatchJobs
from app.utilities.validation import validate_email
from app.utilities.error_handlers import error_page
from app.utilities.object_storage import generate_upload_link_validation_file


# Variables available in all templates
@app.context_processor
def inject_globals():
    return {
        "APP_NAME": app.config["APP_NAME"],
        "COPYRIGHT": f"2021–{datetime.now().year} - {app.config['APP_NAME']}",
    }


# Redirect pages with trailing slashes to versions without
# Applies to other Blueprints like app_private as well
@app.before_request
def remove_trailing_slash():
    if request.path != "/" and request.path != "/app/" and request.path.endswith("/"):
        return redirect(request.path[:-1])


# provide login manager with load_user callback
# This callback is used to reload the user object from the user ID stored in the session.
@lm.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.errorhandler(403)
def page_not_found(e):
    print(f"ERROR 403: {e}")
    return error_page(403)


@app.errorhandler(404)
def page_not_found(e):
    print(f"ERROR 404: {e}")
    return error_page(404)


@app.errorhandler(405)
def page_not_found(e):
    print(f"ERROR 405: {e}")
    return error_page(405)


@app.errorhandler(429)
def rate_limited(e):
    print(f"ERROR 429: {e}")
    return error_page(429)


@app.errorhandler(500)
def server_error(e):
    print(f"ERROR 500: {e}")
    return error_page(500)


# Configure rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per minute", "400 per hour"],
    on_breach=rate_limited,
)


def is_user_logged_in():
    return current_user.is_authenticated


# Serve favicon in the default route some clients expect
@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("media/favicon.ico")


@app.route("/robots.txt")
def robots():
    return Response(
        "User-agent: *\nDisallow: /",
        mimetype="text/plain",
    )


@app.route("/validate-file", defaults={"path": "upload"}, methods=["GET", "POST"])
@app.route("/validate-file/<path>", methods=["GET", "POST"])
@login_required
@limiter.limit("40 per day")
def validate_file(path):
    match path:
        # Authorize front end to upload to the bucket
        case "getSignedRequest":
            return generate_upload_link_validation_file(
                current_user, request.args.get("file_type"), request.args.get("file")
            )
        # Create a job record after file is uploaded
        case "recordBatchFileDetails":
            print(request.args.get("file"))
            print(request.args.get("email-column"))
            print(request.args.get("headers"))
            job = BatchJobs(
                user=current_user,
                uploaded_file=request.args.get("file"),
                email_column=request.args.get("email-column"),
                header_row=1 if request.args.get("headers") == "true" else 0,
            )
            db.session.add(job)
            db.session.commit()
            return jsonify({"success": "Job is recorded"})

    return jsonify({"error": "File upload failed"}), 500


@app.route("/validate", methods=["POST"])
@limiter.limit(
    f'{app.config["MLS_MAX_ANONYMOUS_USAGE_PER_IP"]} per day',
    exempt_when=is_user_logged_in,
)
def validate():
    # Grab the email from the request
    email = request.form.get("email")

    # Process the validation request
    # At this point, the user is either logged in and has credits,
    # or is an anonymous user and can only do this until the limit is reached
    try:
        response = validate_email(email)
        if response:
            # If user is logged in, use their credits
            if is_user_logged_in():
                if current_user.email_confirmed != 1:
                    return "", 403

                # Deduct credits from the user
                # We waited until here to ensure we are delivering a result before deducting a credit
                if current_user.credits > 0:
                    current_user.deduct_credits(1)
                else:
                    return "", 402

            # Return the response from the worker
            return response, 200
        else:
            print("Validation response from the worker is None")
            return "", 500
    except Exception as e:
        print(f"Validation request failed: {e}")
        return "", 500


# App main route + generic routing
@app.route("/", defaults={"path": "index"})
@app.route("/<path>")
def index(path):
    try:
        # Serve the file (if exists) from app/templates/public/PATH.html
        return render_template(
            f"public/{path}.html",
            path=path,
            user=current_user,
            MLS_FREE_CREDITS_FOR_NEW_ACCOUNTS=app.config[
                "MLS_FREE_CREDITS_FOR_NEW_ACCOUNTS"
            ],
        )

    except TemplateNotFound:
        return error_page(404)

    except Exception as e:
        print(f"ERROR 500: {e}")
        return error_page(500)
