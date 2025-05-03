from flask import render_template, Blueprint, current_app
from flask_login import current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from jinja2 import TemplateNotFound

from app import lm
from app.models import Users
from app.utilities.error_handlers import error_page

# Create a Blueprint
public_bp = Blueprint("public_bp", __name__)


# provide login manager with load_user callback
# This callback is used to reload the user object from the user ID stored in the session.
@lm.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@public_bp.errorhandler(403)
def page_not_found(e):
    print(f"ERROR 403: {e}")
    return error_page(403)


@public_bp.errorhandler(404)
def page_not_found(e):
    print(f"ERROR 404: {e}")
    return error_page(404)


@public_bp.errorhandler(405)
def page_not_found(e):
    print(f"ERROR 405: {e}")
    return error_page(405)


@public_bp.errorhandler(429)
def rate_limited(e):
    print(f"ERROR 429: {e}")
    return error_page(429)


@public_bp.errorhandler(500)
def server_error(e):
    print(f"ERROR 500: {e}")
    return error_page(500)


# Configure rate limiting
limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["200 per minute", "400 per hour"],
    on_breach=rate_limited,
)


# Serve favicon in the default route some clients expect
@public_bp.route("/favicon.ico")
def favicon():
    """Serve the favicon.ico file."""

    return current_app.send_static_file("media/favicon.ico")


@public_bp.route("/", defaults={"path": "index"})
@public_bp.route("/<path>")
def index(path):
    """Serve the index page or dynamically route for other pages with existing templates.

    Args:
        path (str): The path to the requested page.

    Returns:
        Response: The rendered HTML template for the requested page.
    """
    try:
        # Serve the file (if exists) from app/templates/public/PATH.html
        return render_template(f"public/{path}.html", path=path, user=current_user)

    except TemplateNotFound:
        return error_page(404)

    except Exception as e:
        print(f"ERROR 500: {e}")
        return error_page(500)
