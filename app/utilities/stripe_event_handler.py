import datetime

from app.config import appTimezone
from app.models import Users, Tiers


def is_subscription_event(event):
    return event.type[:21] == "customer.subscription"


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

    # If it is a subscription event, try to parse user and tier
    if is_subscription_event(event):
        subscription = event.data.object

        # Get the Stripe customer and price_id
        customer_id = subscription["customer"]
        price_id = subscription["items"]["data"][0]["price"]["id"]

        # Try to get the user and tier based on customer_id and price_id
        user_matched = user_from_stripe_customer_id(customer_id)
        tier_matched = tier_from_stripe_price_id(price_id)

        # Are we canceling the subscription now?
        if event.type == "customer.subscription.deleted":
            print(f"Subscription is canceled immediately for customer_id {customer_id}")
            user_matched.tier_id = 1
            user_matched.cancel_at = None
            # TODO: Transactional email

        elif event.type == "customer.subscription.updated":
            # Is the update about an upcoming cancellation?
            if subscription["cancel_at_period_end"]:
                cancellation_date = datetime.datetime.fromtimestamp(
                    subscription["current_period_end"]
                ).astimezone(appTimezone)
                print(f"Subscription will be canceled on {cancellation_date}")
                user_matched.cancel_at = cancellation_date
                # TODO: Transactional email

            # Is the update about a tier change? Including from free to paid.
            if subscription["cancel_at"] is None:
                print(f"Updating {user_matched.email}'s tier to {tier_matched.label}.")
                # Update the user's tier
                user_matched.tier_id = tier_matched.id

                # Clear any prior cancellation date if it exists
                user_matched.cancel_at = None

        else:
            print(f"Unhandled subscription event: {event.type}")

        # In any case, Save the changes made above
        user_matched.save()
