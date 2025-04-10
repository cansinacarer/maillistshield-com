import datetime

from app.config import appTimezone
from app.models import Users, Tiers
from app.emails import (
    send_email_about_subscription_confirmation,
    send_email_about_subscription_cancellation,
    send_email_about_subscription_deletion,
)


def is_subscription_event(event):
    return event.type[:21] == "customer.subscription"


def is_checkout_completed_event(event):
    return event.type == "checkout.session.completed"


def user_from_stripe_customer_id(customer_id):
    user_matched = Users.query.filter_by(stripe_customer_id=customer_id).first()

    if user_matched is None:
        raise Exception(f"App user not found for customer_id {customer_id}.")

    return user_matched


def tier_from_stripe_price_id(price_id):
    tier_matched = Tiers.query.filter_by(stripe_price_id=price_id).first()

    if tier_matched is None:
        raise Exception(f"Tier not found for price_id {price_id}.")

    return tier_matched


def handle_stripe_event(event):
    # If it is a credit purchase event, try to parse user and update credits
    if is_checkout_completed_event(event):
        # Get the Stripe customer and find the matching user
        customer_id = event.data.object["customer"]
        user_matched = user_from_stripe_customer_id(customer_id)

        # Update the user's credits
        quantity = event.data.object.metadata.quantity
        user_matched.credits = user_matched.credits + int(quantity)
        user_matched.save()

    # If it is a subscription event, try to parse user and tier
    if is_subscription_event(event):
        subscription = event.data.object

        # Get the Stripe customer and find the matching user
        customer_id = subscription["customer"]
        user_matched = user_from_stripe_customer_id(customer_id)

        # Get the price_id and find the matching tier
        price_id = subscription["items"]["data"][0]["price"]["id"]
        tier_matched = tier_from_stripe_price_id(price_id)

        # Are we canceling the subscription now?
        if event.type == "customer.subscription.deleted":
            # Send the email about subscription ending while we can still read the tier
            send_email_about_subscription_deletion(user_matched, tier_matched)

            # Change the tier to the first level
            user_matched.tier_id = 1
            user_matched.cancel_at = None

        elif event.type == "customer.subscription.updated":
            # Is the update about an upcoming cancellation?
            if subscription["cancel_at_period_end"]:
                cancellation_date = datetime.datetime.fromtimestamp(
                    subscription["current_period_end"]
                ).astimezone(appTimezone)
                user_matched.cancel_at = cancellation_date

                # Send email about subscription cancellation
                send_email_about_subscription_cancellation(
                    user_matched, tier_matched, cancellation_date
                )

            # Is the update about a tier change? Including from free to paid.
            if subscription["cancel_at"] is None:
                # Update the user's tier
                # TODO: Check if they had a subscription to a better tier before cancellation, if yes, keep that until that ends, then switch to new tier
                user_matched.tier_id = tier_matched.id

                # Send email about subscription confirmation
                send_email_about_subscription_confirmation(user_matched, tier_matched)

                # Clear any prior cancellation date if it exists
                user_matched.cancel_at = None

        else:
            print(f"Unhandled subscription event: {event.type}")

        # In any case, Save the changes made above
        user_matched.save()
