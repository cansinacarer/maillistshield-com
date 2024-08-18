from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_sslify import SSLify
from flask_cors import CORS
from decouple import UndefinedValueError

# Stripe
import stripe

import sys


# Initialize the flask app
app = Flask(__name__)

# Load the Config object
try:
    from app.config import Config

    app.config.from_object(Config)

except UndefinedValueError:
    print("Please make sure you have all the required environment variables set.")
    sys.exit()

# Flask Modules
mail = Mail(app)
db = SQLAlchemy(app)
bc = Bcrypt(app)
lm = LoginManager()
lm.init_app(app)

# SSL
sslify = SSLify(app)

# Enable CORS for all routes
CORS(
    app,
    resources={r"/*": {"origins": [app.config["APP_ROOT_URL"]]}},
    supports_credentials=False,
)

# Setup database
from app import models

try:
    with app.app_context():
        db.create_all()

        # Create the default tier for all users
        from app.models import Tiers

        # If there are no tiers in the database, create the default tiers
        if Tiers.query.count() == 0:
            default_tier = Tiers(name="free", label="Free")
            db.session.add(default_tier)
            db.session.commit()
            print(" * Default tiers created successfully.")

except Exception as e:
    print("Error creating the database tables.")
    print(e)
    sys.exit()

# Stripe setup
stripe.api_key = app.config["STRIPE_SECRET_KEY"]

# Import the Blueprints and register them
from app.views_private import app_private
from app.views_auth import app_auth

app.register_blueprint(app_private, url_prefix="/app")
app.register_blueprint(app_auth, url_prefix="/")


# --- THE FOLLOWING SHOULD REMAIN AT THE END ---

# Import routing, models and start the app
from app import views
from app.models import Tiers
