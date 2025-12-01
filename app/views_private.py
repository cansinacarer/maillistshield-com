"""Private views and routes for authenticated users.

This module defines the routes that require authentication, including
the user dashboard, billing, account settings, API key management,
admin pages, and webhook endpoints.
"""

# Flask modules
from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    jsonify,
    current_app,
)
from flask_login import (
    login_required,
    current_user,
)
from jinja2 import TemplateNotFound

# Stripe
import stripe

# App modules
from app import csrf, db
from app.forms import ProfileDetailsForm, CreateAPIKeyForm
from app.models import Users, Tiers, BatchJobs, APIKeys
from app.utilities.object_storage import generate_upload_link_profile_picture
from app.utilities.error_handlers import error_page
from app.utilities.stripe_event_handler import handle_stripe_event
from app.utilities.helpers import generate_api_key_and_hash

# Instantiate the Blueprint
private_bp = Blueprint("private_bp", __name__)


@private_bp.route("/download-results/<jobuid>", methods=["GET"])
def download_results(jobuid):
    """The view function that serves the batch validation result files.

    Args:
        jobuid (str): The part of the requested endpoint after /download-results/.
    """

    # If no jobuid is provided, return 404
    if not jobuid:
        return error_page(404)

    # If anonymous user, return 404
    if current_user.is_anonymous:
        return error_page(404)

    # Get the job with the provided jobuid that belongs to the current user
    job = (
        db.session.query(BatchJobs)
        .filter_by(user_id=current_user.id, uid=jobuid)
        .first()
    )

    # If the jobuid provided doesn't belong to the current user,
    # return 404, not 403 because I don't want to let them know of a match
    if not job:
        return error_page(404)

    # If the job is not completed or doesn't have a results file, return 404
    if job.status != "file_completed" or not job.results_file:
        return error_page(404)

    # Generate a pre-signed download link for the results file
    try:
        download_link = job.generate_results_download_link()
        if download_link:
            return redirect(download_link)
        else:
            print(f"Job with id {job.id} doesn't have a results file to download.")
            return error_page(500)
    except Exception as e:
        print(f"Error generating the download link for job with id {job.id}: {e}")
        return error_page(500)


@private_bp.route("/webhook/<path>", methods=["POST"])
@csrf.exempt
def webhook(path):
    """The view function for the webhook endpoint.

    Args:
        path (str): The part of the requested endpoint after /webhook/.

    Returns:
        Response: A JSON response indicating success or failure.

    Note:
        Webhook endpoints for external services to give us updates.
        Currently, this endpoint is used to receive webhook events from Stripe.
    """
    try:
        match path:
            # The endpoint where stripe sends the webhook events
            case "stripe":
                # Verify that the incoming request is from Stripe
                try:
                    event = stripe.webhook.Webhook.construct_event(
                        request.data.decode("utf-8"),
                        request.headers.get("Stripe-Signature", None),
                        current_app.config["STRIPE_WEBHOOK_SECRET"],
                    )
                    handle_stripe_event(event)

                except ValueError:
                    return error_page(400)

                except stripe.error.SignatureVerificationError:
                    print(
                        "Requests with invalid signature are hitting the stripe webhook!"
                    )
                    return error_page(400)

                except Exception as e:
                    print(
                        f"Unhandled error while processing Stripe webhook request: {e}"
                    )
                    return error_page(500)

                # Return a response to acknowledge the receipt of the event
                finally:
                    return jsonify("success=True"), 200

            # Non-existent webhook path
            case _:
                return error_page(404)

    except Exception as e:
        print(f"Error when processing a webhook request: {e}")
        return error_page(500)


@private_bp.route("/api-keys", defaults={"path": "api-keys"}, methods=["GET", "POST"])
@private_bp.route("/api-keys/<path>", methods=["GET", "POST"])
@login_required
def api_keys(path):
    """The view function for the page for managing API keys.

    Args:
        path: The sub-path for API key actions ('create', 'revoke', or 'api-keys').

    Returns:
        Response: The rendered template or JSON response for the action.
    """

    # Redirect to email confirmation
    if current_user.email_confirmed != 1:
        flash(
            "Please confirm your email address first by entering the confirmation code we have emailed you.",
            "error",
        )
        return redirect(url_for("auth_bp.email_confirmation_by_code"))

    # Declare the API key creation form
    form = CreateAPIKeyForm()

    if path == "api-keys" and request.method == "GET":
        return render_template(
            "private/api_keys/api_keys.html",
            user=current_user,
            form=form,
            path=path,
            new_key=None,
        )

    if request.method == "POST":
        # Handle the POST requests to create or revoke endpoints
        match path:
            case "revoke":
                # Check if request has JSON data
                if not request.is_json:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "message": "Content-Type must be application/json",
                            }
                        ),
                        400,
                    )

                try:
                    key_id = request.json.get("key_id", None)
                    if not key_id:
                        return (
                            jsonify({"success": False, "error": "Invalid key ID"}),
                            400,
                        )

                    api_key = APIKeys.query.filter_by(
                        id=key_id, user_id=current_user.id
                    ).first()

                    if not api_key or not api_key.is_active:
                        return (
                            jsonify(
                                {
                                    "success": False,
                                    "error": "API key not found or already revoked",
                                }
                            ),
                            404,
                        )

                    api_key.is_active = False
                    api_key.save()

                    return jsonify({"success": True}), 200
                except Exception as e:
                    print(f"Error revoking API key: {e}")
                    return (
                        jsonify({"success": False, "error": "Internal server error"}),
                        500,
                    )

            case "create":
                try:
                    # Generate a new API key and its hash
                    new_key, key_hash = generate_api_key_and_hash()

                    # Prepare expiration date
                    expires_at = form.expires_at.data if form.expires_at.data else None

                    api_key = APIKeys(
                        user=current_user,
                        key_hash=key_hash,
                        label=request.form.get("label", None, type=str),
                        expires_at=expires_at,
                    )
                    api_key.save()
                    flash(
                        f"New API key created successfully. Please save the API key now, as it won't be shown again: {new_key}",
                        "success",
                    )
                    flash(
                        "If you lose your API key, please revoke it below and create a new one.",
                        "info",
                    )
                    return redirect(url_for("private_bp.api_keys"))
                except Exception as e:
                    print(f"Error creating a new API key: {e}")
                    flash(
                        "An error occurred while creating a new API key. Please try again later.",
                        "danger",
                    )
                    return redirect(url_for("private_bp.api_keys"))

    # If the path doesn't match any known routes, return 404
    # This catches both GET and POST requests with unknown paths
    return error_page(404)


@private_bp.route("/billing", defaults={"path": "billing"}, methods=["GET", "POST"])
@private_bp.route("/billing/<path>", methods=["GET", "POST"])
@login_required
def billing(path):
    """The view function for the billing pages' routing.

    Args:
        path (str): The part of the requested endpoint after /billing/.

    Returns:
        Response: The rendered template for the requested billing page.
    """

    # Redirect to email confirmation
    if current_user.email_confirmed != 1:
        flash(
            "Please confirm your email address first by entering the confirmation code we have emailed you.",
            "error",
        )
        return redirect(url_for("auth_bp.email_confirmation_by_code"))

    try:
        match path:
            case "success":
                # This is only informational, we process the membership change with the webhook events
                flash("Your payment has been successful.", "success")
                return redirect(
                    url_for(
                        "private_bp.billing",
                    )
                )

            case "cancel":
                # This is only informational, we process the membership change with the webhook events
                flash("Your payment has been canceled.", "danger")
                return redirect(
                    url_for(
                        "private_bp.billing",
                    )
                )

            # Redirect to the Stripe for purchase
            case "purchase-credits":
                if request.method != "POST":
                    return error_page(400)

                try:
                    # If the user doesn't have a stripe_customer_id, create a new customer
                    if current_user.stripe_customer_id == None:
                        customer = stripe.Customer.create(
                            email=current_user.email,
                            name=current_user.firstName + " " + current_user.lastName,
                        )
                        current_user.stripe_customer_id = customer.id
                        current_user.save()

                    # Based on the tier selected, select the price
                    try:
                        creditsRequested = request.form.get("numberOfCredits")

                        # Validate the number of credits
                        if not creditsRequested.isdigit():
                            flash("Invalid number of credits selected.", "danger")
                            return redirect(url_for("private_bp.billing"))

                    except Exception as e:
                        print(f"Error while parsing the numberOfCredits requested: {e}")
                        flash("Invalid tier selected.", "danger")
                        return redirect(request.referrer)

                    checkout_session = stripe.checkout.Session.create(
                        customer=current_user.stripe_customer_id,
                        line_items=[
                            {
                                "price_data": {
                                    "unit_amount": current_app.config[
                                        "STRIPE_CREDIT_UNIT_COST"
                                    ],
                                    "currency": "usd",
                                    "product": current_app.config[
                                        "STRIPE_PRODUCT_ID_FOR_CREDITS"
                                    ],
                                },
                                "quantity": int(creditsRequested),
                            }
                        ],
                        metadata={
                            # Save the number of credits requested in the metadata
                            # So that we can update the user's credits in the webhook
                            # Otherwise, Stripe doesn't tell us how many credits were purchased
                            "quantity": int(creditsRequested),
                        },
                        payment_intent_data={
                            # The description shown in the list of charges
                            "description": f"Purchase of {creditsRequested} credits",
                        },
                        mode="payment",
                        payment_method_types=["card"],
                        success_url=current_app.config["APP_ROOT_URL"]
                        + url_for("private_bp.billing")
                        + "/success",
                        cancel_url=current_app.config["APP_ROOT_URL"]
                        + url_for("private_bp.billing")
                        + "/cancel",
                        automatic_tax={"enabled": True},
                        customer_update={
                            "address": "auto",  # Automatically update the customer's address
                        },
                    )
                except Exception as e:
                    flash(
                        "An error occurred while processing your payment. Please try again later.",
                        "danger",
                    )
                    print(
                        f"An error occurred while creating the Stripe checkout session:\n{e}"
                    )
                    return redirect(
                        url_for(
                            "private_bp.billing",
                        )
                    )

                return redirect(checkout_session.url, code=303)

            # Redirect to the Stripe for subscription
            case "billing-portal":
                if request.method != "POST":
                    return error_page(400)
                try:
                    checkout_session = stripe.billing_portal.Session.create(
                        customer=current_user.stripe_customer_id,
                        return_url=request.referrer,
                    )
                except Exception as e:
                    flash(
                        "An error occurred while processing your payment. Please try again later.",
                        "danger",
                    )
                    print(
                        f"An error occurred while creating the Stripe billing_portal session:\n{e}"
                    )
                    return redirect(
                        url_for(
                            "private_bp.billing",
                        )
                    )

                return redirect(checkout_session.url, code=303)

            # Redirect to the Stripe checkout page
            case "checkout":
                if request.method != "POST":
                    return error_page(400)

                try:
                    # If the user doesn't have a stripe_customer_id, create a new customer
                    if current_user.stripe_customer_id == None:
                        customer = stripe.Customer.create(
                            email=current_user.email,
                            name=current_user.firstName + " " + current_user.lastName,
                        )
                        current_user.stripe_customer_id = customer.id
                        current_user.save()

                    # Based on the tier selected, select the price
                    try:
                        tierRequested = request.form.get("tier")
                        tierMatched = Tiers.query.filter_by(name=tierRequested).first()
                        price_id = tierMatched.stripe_price_id
                    except Exception as e:
                        print(f"Error while matching the tier: {e}")
                        flash("Invalid tier selected.", "danger")
                        return redirect(request.referrer)

                    checkout_session = stripe.checkout.Session.create(
                        customer=current_user.stripe_customer_id,
                        line_items=[
                            {
                                "price": price_id,
                                "quantity": 1,
                            }
                        ],
                        mode="subscription",
                        payment_method_types=["card"],
                        success_url=current_app.config["APP_ROOT_URL"]
                        + url_for("private_bp.billing")
                        + "/success",
                        cancel_url=current_app.config["APP_ROOT_URL"]
                        + url_for("private_bp.billing")
                        + "/cancel",
                        automatic_tax={"enabled": True},
                        customer_update={
                            "address": "auto",  # Automatically update the customer's address
                        },
                    )
                except Exception as e:
                    flash(
                        "An error occurred while processing your payment. Please try again later.",
                        "danger",
                    )
                    print(
                        f"An error occurred while creating the Stripe checkout session:\n{e}"
                    )
                    return redirect(
                        url_for(
                            "private_bp.billing",
                        )
                    )

                return redirect(checkout_session.url, code=303)

            case _:
                customer_id = current_user.stripe_customer_id
                charges = None
                if customer_id != None:
                    charges = stripe.Charge.list(
                        customer=customer_id, status="succeeded", limit=100
                    )

                return render_template(
                    f"private/billing/{path}.html",
                    user=current_user,
                    path=path,
                    tiers=Tiers.query.all(),
                    charges=charges,
                )
    except TemplateNotFound:
        return error_page(404)
    except Exception as e:
        print(f"ERROR 500: {e}")
        return error_page(500)


@private_bp.route("/account", defaults={"path": "account"}, methods=["GET", "POST"])
@private_bp.route("/account/<path>", methods=["GET", "POST"])
@login_required
def account(path):
    """The view function for the account pages routing.

    Args:
        path (str): The part of the requested endpoint after /account/.

    Returns:
        Response: The rendered template for the requested account page.
    """

    # Redirect to email confirmation
    if current_user.email_confirmed != 1:
        flash(
            "Please confirm your email address first by entering the confirmation code we have emailed you.",
            "error",
        )
        return redirect(url_for("auth_bp.email_confirmation_by_code"))
    try:
        # Declare the registration form
        form = ProfileDetailsForm()
        match path:
            case "upload-profile-pic":
                return generate_upload_link_profile_picture(
                    current_user,
                    request.args.get("file_type"),
                )

            case "enable_totp":
                if request.method == "POST":
                    otp = request.form["otp"]
                    print(f"Checking code ({otp}): {current_user.totp_match(otp)}")
                    if current_user.totp_match(otp):
                        current_user.totp_enabled = 1
                        current_user.save()
                        flash("Two-factor authentication has been enabled.", "info")
                    else:
                        flash("Invalid code. Please try again.", "danger")
                    return redirect(request.referrer)
                else:
                    return ""

            case "disable_totp":
                if request.method == "POST":
                    if current_user.totp_enabled == 1:
                        current_user.totp_reset_secret()
                        current_user.totp_enabled = 0
                        current_user.save()
                        flash("Two-factor authentication has been disabled.", "info")
                    else:
                        flash(
                            "Two-factor authentication is already disabled.", "danger"
                        )
                    return redirect(request.referrer)
                else:
                    return ""

            case "" | "account":
                if request.method == "POST":
                    # If bucket upload request returns 200, JS calls this endpoint
                    # Then we set the avatar_uploaded flag to True,
                    # so that user.avatar() serves the image from the bucket
                    if request.form.get("profile-pic-updated") == "yes":
                        try:
                            current_user.avatar_uploaded = True
                            current_user.save()
                            return "success", 200
                        except:
                            return "failed", 500

                    # If the profile details form is submitted
                    if form.validate_on_submit():
                        current_user.firstName = request.form.get(
                            "firstName", "", type=str
                        )
                        current_user.lastName = request.form.get(
                            "lastName", "", type=str
                        )
                        current_user.newsletter = (
                            1 if request.form.get("newsletter") == "y" else 0
                        )
                        current_user.save()

                return render_template(
                    f"private/account/{path}.html",
                    user=current_user,
                    form=form,
                    path=path,
                )
            case _:
                return render_template(
                    f"private/account/{path}.html",
                    user=current_user,
                    form=form,
                    path=path,
                )
    except TemplateNotFound:
        return error_page(404)
    except Exception as e:
        print(f"ERROR 500: {e}")
        return error_page(500)


@private_bp.route("/admin", defaults={"path": "admin"}, methods=["GET", "POST"])
@private_bp.route("/admin/<path:path>", methods=["GET", "POST"])
@login_required
def admin(path):
    """The view function for the admin privileged pages' routing.

    path:path is used to catch all paths, including those with multiple slashes (/)

    Args:
        path (str): The part of the requested endpoint after /admin/.

    Returns:
        Response: The rendered template for the requested admin page.
    """

    # If this user is not admin, return 403
    if current_user.role != "admin":
        return error_page(403)

    # If this is an email rendering path
    if path[:6] == "email/":
        # Try to render the email template
        email_template = path[6:]
        try:
            return render_template(
                f"emails/{email_template}.html",
                user=current_user,
                appName=current_app.config["APP_NAME"],
                appHome=current_app.config["APP_ROOT_URL"],
                resetLink=url_for("auth_bp.set_new_password", _external=True)
                + "/dummyToken",
            )
        except TemplateNotFound:
            return "Email template not found.", 404

    # Try to find the matching admin page template
    try:
        # If the path matches a template, return the template
        return render_template(
            f"private/admin/{path}.html", path=path, user=current_user
        )

    except TemplateNotFound:
        return error_page(404)
    except Exception as e:
        print(f"ERROR 500: {e}")
        return error_page(500)


# Generic private pages routing
@private_bp.route("/", defaults={"path": "index"})
@private_bp.route("/<path>")
@login_required
def private_index(path):
    """The view function for the private pages routing.

    This is the fallback view function for all private pages at /app/.

    Args:
        path (str): The part of the requested endpoint after /app/.

    Returns:
        Response: The rendered template for the requested private page.
    """

    # Redirect to email confirmation
    if current_user.email_confirmed != 1:
        flash(
            "Please confirm your email address first by entering the confirmation code we have emailed you.",
            "error",
        )
        return redirect(url_for("auth_bp.email_confirmation_by_code"))

    try:
        # Serve the file (if exists) from app/templates/private/PATH.html
        return render_template(f"private/{path}.html", path=path, user=current_user)

    except TemplateNotFound:
        return error_page(404)

    except Exception as e:
        print(f"ERROR 500: {e}")
        return error_page(500)
