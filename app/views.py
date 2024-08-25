from flask import render_template, request, redirect
from flask_login import current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from jinja2 import TemplateNotFound
from datetime import datetime

from app import app, lm
from app.models import Users
from app.utilities.error_handlers import error_page


# Variables available in all templates
@app.context_processor
def inject_globals():
    return {
        "APP_NAME": app.config["APP_NAME"],
        "COPYRIGHT": f"2021–{datetime.now().year} HC Digital Solutions Inc.",
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


# Serve favicon in the default route some clients expect
@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("media/favicon.ico")


# App main route + generic routing
@app.route("/", defaults={"path": "index"})
@app.route("/<path>")
def index(path):
    try:
        # Serve the file (if exists) from app/templates/public/PATH.html
        return render_template(f"public/{path}.html", path=path, user=current_user)

    except TemplateNotFound:
        return error_page(404)

    except Exception as e:
        print(f"ERROR 500: {e}")
        return error_page(500)
