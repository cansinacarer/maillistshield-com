# Flask modules
from flask import Blueprint, render_template, request, url_for, redirect, flash, jsonify
from flask_login import (
    login_required,
    current_user,
)
from jinja2 import TemplateNotFound
import datetime

# Stripe
import stripe
import stripe.webhook

# App modules
from app import app
from app.forms import ProfileDetailsForm
from app.models import Users, Tiers
from app.utilities.object_storage import generate_upload_link_profile_picture
from app.utilities.error_handlers import error_page
from app.utilities.stripe_event_handler import handle_stripe_event

# Instantiate the Blueprint
app_private = Blueprint("views_private", __name__)


# Custom date format filter
# In Jinja, we can use this filter like: {{ charge.created | dateformat }}
def dateformat(value, format="%B %d, %Y"):
    return datetime.datetime.fromtimestamp(value).strftime(format)


app.jinja_env.filters["dateformat"] = dateformat


def timeformat(value, format="%I:%M %p"):
    return datetime.datetime.fromtimestamp(value).strftime(format)


app.jinja_env.filters["timeformat"] = timeformat


# For testing the rendering of email templates
@app_private.route("/admin/email-test/<email>")
@login_required
def email_test(email):
    try:
        return render_template(
            f"emails/{email}.html",
            user=current_user,
            appName=app.config["APP_NAME"],
            appHome=app.config["APP_ROOT_URL"],
            resetLink=url_for("set_new_password", _external=True) + "/dummyToken",
        )

    except TemplateNotFound:
        return "Email template not found.", 404


# Webhook endpoints for external services to give us updates
@app_private.route("/webhook/<path>", methods=["POST"])
def webhook(path):
    try:
        match path:
            # The endpoint where stripe sends the webhook events
            case "stripe":

                # Verify that the incoming request is from Stripe
                try:
                    event = stripe.webhook.Webhook.construct_event(
                        request.data.decode("utf-8"),
                        request.headers.get("Stripe-Signature", None),
                        app.config["STRIPE_WEBHOOK_SECRET"],
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


# Billing pages routing
@app_private.route("/billing", defaults={"path": "billing"}, methods=["GET", "POST"])
@app_private.route("/billing/<path>", methods=["GET", "POST"])
@login_required
def billing(path):
    # Redirect to email confirmation
    if current_user.email_confirmed != 1:
        flash(
            "Please confirm your email address first by entering the confirmation code we have emailed you.",
            "error",
        )
        return redirect(url_for("email_confirmation_by_code"))

    try:
        match path:
            case "success":
                # This is only informational, we process the membership change with the webhook events
                flash("Your payment has been successful.", "success")
                return redirect(
                    url_for(
                        "views_private.billing",
                    )
                )

            case "cancel":
                # This is only informational, we process the membership change with the webhook events
                flash("Your payment has been canceled.", "danger")
                return redirect(
                    url_for(
                        "views_private.billing",
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
                            return redirect(url_for("views_private.billing"))

                    except Exception as e:
                        print(f"Error while parsing the numberOfCredits requested: {e}")
                        flash("Invalid tier selected.", "danger")
                        return redirect(request.referrer)

                    checkout_session = stripe.checkout.Session.create(
                        customer=current_user.stripe_customer_id,
                        line_items=[
                            {
                                "price_data": {
                                    "unit_amount": app.config[
                                        "STRIPE_PRODUCT_UNIT_COST"
                                    ],
                                    "currency": "usd",
                                    "product": app.config[
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
                        success_url=app.config["APP_ROOT_URL"]
                        + url_for("views_private.billing")
                        + "/success",
                        cancel_url=app.config["APP_ROOT_URL"]
                        + url_for("views_private.billing")
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
                            "views_private.billing",
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
                            "views_private.billing",
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
                        success_url=app.config["APP_ROOT_URL"]
                        + url_for("views_private.billing")
                        + "/success",
                        cancel_url=app.config["APP_ROOT_URL"]
                        + url_for("views_private.billing")
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
                            "views_private.billing",
                        )
                    )

                return redirect(checkout_session.url, code=303)

            case _:
                customer_id = current_user.stripe_customer_id
                charges = None
                if customer_id != None:
                    charges = stripe.Charge.list(
                        customer=customer_id, status="succeeded"
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


# Account pages routing
@app_private.route("/account", defaults={"path": "account"}, methods=["GET", "POST"])
@app_private.route("/account/<path>", methods=["GET", "POST"])
@login_required
def account(path):
    # Redirect to email confirmation
    if current_user.email_confirmed != 1:
        flash(
            "Please confirm your email address first by entering the confirmation code we have emailed you.",
            "error",
        )
        return redirect(url_for("email_confirmation_by_code"))
    try:
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
                form = ProfileDetailsForm()
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
                form = ProfileDetailsForm()
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


# Generic private pages routing
@app_private.route("/", defaults={"path": "index"})
@app_private.route("/<path>")
@login_required
def private_index(path):
    # Redirect to email confirmation
    if current_user.email_confirmed != 1:
        flash(
            "Please confirm your email address first by entering the confirmation code we have emailed you.",
            "error",
        )
        return redirect(url_for("email_confirmation_by_code"))

    try:
        # Serve the file (if exists) from app/templates/private/PATH.html
        return render_template(f"private/{path}.html", path=path, user=current_user)

    except TemplateNotFound:
        return error_page(404)

    except:
        return error_page(500)
