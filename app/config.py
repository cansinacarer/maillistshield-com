from decouple import config
import pytz
import boto3

import os


# Timezone used in this app
appTimezoneStr = config("TIMEZONE")
appTimezone = pytz.timezone(appTimezoneStr)

# S3 resource to be imported in other modules
# Use s3.meta.client if client object is needed
s3 = boto3.resource(
    "s3",
    endpoint_url=config("S3_ENDPOINT"),
    aws_access_key_id=config("S3_KEY"),
    aws_secret_access_key=config("S3_SECRET"),
)


# Flask app configuration
class Config:

    # Grabs the folder where the script runs
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    # Enable protection against Cross-site Request Forgery
    CSRF_ENABLED = True

    # Application Details
    APP_NAME = config("APP_NAME")
    APP_ROOT_URL = config("APP_ROOT_URL", "https://localhost:5000/")
    TIMEZONE = config("TIMEZONE")
    FLASK_DEBUG = config("FLASK_DEBUG", cast=bool)

    # Self signed certificates for local development
    # Only used when FLASK_DEBUG is True
    FLASK_RUN_CERT = config("FLASK_RUN_CERT")
    FLASK_RUN_KEY = config("FLASK_RUN_KEY")

    # Database
    SQLALCHEMY_DATABASE_URI = config(
        "DATABASE_CONNECTION_STRING",
        default=f"sqlite:///{os.path.join(os.path.dirname(BASEDIR), 'database.db')}",
    )
    SECRET_KEY = config("DATABASE_SECRET_KEY")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 60,
        # To handle disconnects as described here: https://docs.sqlalchemy.org/en/14/core/pooling.html#pool-disconnects
        "pool_pre_ping": True,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Object Storage
    S3_BUCKET_NAME = config("S3_BUCKET_NAME")
    S3_ENDPOINT = config("S3_ENDPOINT")
    S3_KEY = config("S3_KEY")
    S3_SECRET = config("S3_SECRET")

    # Email
    MAIL_FROM = config("MAIL_FROM")
    MAIL_SERVER = config("MAIL_SERVER")
    MAIL_PORT = config("MAIL_PORT", cast=int)
    MAIL_USE_TLS = config("MAIL_USE_TLS", cast=bool)
    MAIL_USE_SSL = config("MAIL_USE_SSL", cast=bool)
    MAIL_USERNAME = config("MAIL_USERNAME")
    MAIL_PASSWORD = config("MAIL_PASSWORD")
    MAIL_DEBUG = config("MAIL_DEBUG", cast=bool)

    # OAuth
    GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET")

    # Stripe
    STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY")
    STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")
