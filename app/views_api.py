# Flask modules
from flask import (
    Blueprint,
    abort,
    jsonify,
    make_response,
    request,
)


# App modules
from app import csrf
from app.models import Users, APIKeys
from app.views import limiter
from app.config import appTimezone
from app.utilities.validation import validate_email

api_bp = Blueprint("api_bp", __name__)


def invalid_api_key_response():
    """
    Abort the request with a 403 error for invalid API keys.

    We standardize the error response to avoid leaking information about
    why the API key is invalid.
    """
    abort(
        make_response(
            jsonify(
                {
                    "status": "error",
                    "message": "Invalid API key.",
                }
            ),
            403,
        )
    )


def no_api_key_response():
    """
    Abort the request with a 401 error for missing API keys.
    """
    abort(
        make_response(
            jsonify(
                {
                    "status": "error",
                    "message": "API key is missing. Please provide an API key in the 'x-api-key' header.",
                }
            ),
            401,
        )
    )


def no_json_body_response():
    """
    Abort the request with a 415 Unsupported Media Type error for missing JSON body.
    """
    abort(
        make_response(
            jsonify(
                {
                    "status": "error",
                    "message": "No JSON body provided. Please provide a valid JSON payload.",
                }
            ),
            415,
        )
    )


def missing_key_in_json_response(key_name):
    """
    Abort the request with a 400 Bad Request error for missing keys in JSON body.
    """
    abort(
        make_response(
            jsonify(
                {
                    "status": "error",
                    "message": f"Missing '{key_name}' in JSON payload. Please include it.",
                }
            ),
            400,
        )
    )


def insufficient_credit_response():
    """
    Abort the request with a 402 Payment Required error for insufficient credits.
    """
    abort(
        make_response(
            jsonify(
                {
                    "status": "error",
                    "message": "Insufficient credits to perform this action. Please top up your account.",
                }
            ),
            402,
        )
    )


def validate_request_json(request):
    """
    Validate that the request has JSON content type and a JSON body.

    Abort the request with appropriate error responses if validation fails.
    """
    # Check if the request has JSON content type
    if request.content_type != "application/json":
        no_json_body_response()

    # Check if the request has a JSON payload
    if not request.json:
        no_json_body_response()


def get_user_from_api_key(request):
    """
    Fetch the user associated with the provided API key.

    All repeated error handling is abstracted into this function.
    """

    # Get the API key from the request headers
    api_key = request.headers.get("x-api-key")
    if not api_key:
        no_api_key_response()

    # Fetch all active API keys from the database
    all_keys = APIKeys.query.filter_by(is_active=True).all()
    if not all_keys:
        invalid_api_key_response()

    # Check if the provided API key matches any stored hashed keys
    matching_key = None
    for key in all_keys:
        if key.check_key(api_key):
            matching_key = key
            break

    if not matching_key:
        invalid_api_key_response()

    # Fetch the user associated with the matching API key
    user = (
        Users.query.filter_by(id=matching_key.user_id).first() if matching_key else None
    )
    if not user:
        invalid_api_key_response()
    return user


def successful_validation_response(result):
    """
    Return a standardized successful validation response.
    """
    # If the user want a single level response ...
    single_level_requested = request.json.get("single_level_response", False) == True

    # ... return the result dict in a single level
    if single_level_requested:
        return result

    # Otherwise, return the result with status and message
    return make_response(
        jsonify(
            {
                "status": "success",
                "message": "Email address is validated and 1 credit is deducted from your account.",
                "result": result,
            }
        ),
        200,
    )


@api_bp.route("/test", methods=["GET", "POST"])
@limiter.limit("50 per hour", methods=["GET", "POST"])
@csrf.exempt
def api_test():
    """
    A test API endpoint that requires an API key.

    This endpoint forgives requests without their content-type
    set to application/json, because it doesn't read your request body.
    """

    if request.method == "GET":
        return (
            "Please use POST requests to interact with the API.",
            405,
        )

    if request.method == "POST":
        # We forgive non-JSON POST requests for this test endpoint

        # Find the user associated with the provided API key
        # (Error handling is abstracted into the function)
        user = get_user_from_api_key(request)

        # Say hello to the user
        return {
            "status": "success",
            "message": f"Hello, {user.firstName}! Good news: your API key works.",
            "note": "We have not checked your content type, but for the validation endpoints, you will need to send a JSON body.",
        }


@api_bp.route("/get-credit-balance", methods=["POST"])
@limiter.limit("50 per hour", methods=["POST"])
@csrf.exempt
def get_credit_balance():
    """
    The API endpoint to get the user's credit balance.

    This endpoint forgives requests without their content-type
    set to application/json, because it doesn't read your request body.
    """
    # Find the user associated with the provided API key
    # (Error handling is abstracted into the function)
    user = get_user_from_api_key(request)

    return {
        "status": "success",
        "message": "Credit balance retrieved successfully.",
        "balance": user.credits,
    }


@api_bp.route("/validate-single", methods=["POST"])
@limiter.limit("50 per hour", methods=["POST"])
@csrf.exempt
def validate_single():
    """
    The API endpoint to validate a single email address.

    This endpoint requires the request content-type to be application/json
    and a JSON body with an "email" key.

    Optionally, the request JSON can include a boolean key "single_level_response".
    If set to true, the API will return the validation result in a single-level dictionary.
    Otherwise, and by default, the response includes status and message keys.
    """

    # Validate the request JSON
    validate_request_json(request)

    # Find the user associated with the provided API key
    # (Error handling is abstracted into the function)
    user = get_user_from_api_key(request)

    # Check if the user has enough credits
    if user.credits < 1:
        insufficient_credit_response()

    # Try to process the validation request
    try:
        email = request.json.get("email", None)
        if not email:
            missing_key_in_json_response("email")

        # Process the validation request
        validation_worker_response = validate_email(email)
        if validation_worker_response:
            # Deduct a credit from the user as we are giving them a result
            user.deduct_credits(1)

            # Return the response from the worker
            return successful_validation_response(validation_worker_response)
        else:
            print("Validation response from the worker is None")
            return {
                "status": "error",
                "message": "Unable to process the validation request due to an issue with our validation system.",
            }, 503  # Service Unavailable

    except Exception as e:
        print(f"Validation request failed: {e}")
        return {
            "status": "error",
            "message": "Internal server error during email validation.",
        }, 500
