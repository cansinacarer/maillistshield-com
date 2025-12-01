"""Database models for the Mail List Shield application.

This module defines the SQLAlchemy ORM models for the application's database,
including user accounts, API keys, batch validation jobs, and subscription tiers.
"""

from datetime import datetime, timezone, timedelta
from email.policy import default
from hashlib import md5
import pyotp
import uuid

from flask import current_app
from flask_login import UserMixin

from app import db, bc
from app.config import s3, appTimezone
from app.utilities.object_storage import generate_download_link, user_folder_size
from app.utilities.qr import qrcode_img_src
from app.utilities.helpers import readable_file_size


class APIKeys(db.Model):
    """Table for storing API keys associated with user accounts.

    API keys are hashed before storage for security. Each key belongs to a single
    user and can be active or revoked.

    Attributes:
        id: Primary key.
        user_id: Foreign key to the Users table.
        key_hash: Bcrypt hash of the API key.
        label: Optional user-provided label for the key.
        created_at: Timestamp when the key was created.
        expires_at: Optional expiration timestamp.
        last_used: Timestamp of the last API call using this key.
        is_active: Whether the key is currently active.
    """

    __tablename__ = "APIKeys"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False)
    key_hash = db.Column(db.String(64), nullable=False)
    label = db.Column(db.String())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    last_used = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def __init__(self, user, key_hash, label=None, expires_at=None):
        """Initialize a new API key.

        Args:
            user: The user object this key belongs to.
            key_hash: The bcrypt hash of the API key.
            label: Optional label for identifying the key.
            expires_at: Optional expiration datetime.
        """
        self.user_id = user.id
        self.key_hash = key_hash
        self.label = label
        self.expires_at = expires_at

    def check_key(self, key_plain):
        """Verify if a plaintext key matches this key's hash.

        Args:
            key_plain: The plaintext API key to verify.

        Returns:
            bool: True if the key matches, False otherwise.
        """
        return bc.check_password_hash(self.key_hash, key_plain)

    def delete_key(self):
        """Delete this API key from the database.

        Returns:
            bool: True if deletion was successful.
        """
        db.session.delete(self)
        db.session.commit()
        return True

    def update_last_used(self):
        """Update the last_used timestamp to the current time."""
        self.last_used = datetime.now(timezone.utc).astimezone(appTimezone)
        self.save()

    def save(self):
        """Save the current state of this API key to the database.

        Returns:
            APIKeys: The saved API key instance.
        """
        # inject self into db session
        db.session.add(self)

        # commit change and save the object
        db.session.commit()

        return self


class BatchJobs(db.Model):
    """Table for batch email validation jobs.

    Tracks the status and metadata of batch validation jobs, including
    uploaded files, processing status, and results.

    Attributes:
        id: Primary key.
        uid: Unique 6-character identifier for the job.
        user_id: Foreign key to the Users table.
        user: Relationship to the user who created the job.
        status: Current status of the job.
        original_file_name: Original name of the uploaded file.
        uploaded_file: Path to the uploaded file in object storage.
        accepted_file: Path to the accepted/processed file.
        results_file: Path to the results file in object storage.
        row_count: Number of rows in the uploaded file.
        last_pick_row: Last row processed by the worker.
        last_pick_time: Timestamp of the last worker pick.
        source: Source of the job (e.g., 'web', 'api').
        header_row: Row number containing headers (0 or 1).
        email_column: Name of the column containing email addresses.
        uploaded: Timestamp when the file was uploaded.
        started: Timestamp when processing started.
        finished: Timestamp when processing finished.
        result: Final result summary.
    """

    __tablename__ = "BatchJobs"

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.id"))
    user = db.relationship("Users", backref="batch_jobs")
    status = db.Column(db.String(), nullable=False, default="pending_start")
    original_file_name = db.Column(db.String(), nullable=False)
    uploaded_file = db.Column(db.String(), nullable=False)
    accepted_file = db.Column(db.String(), nullable=True)
    results_file = db.Column(db.String(), nullable=True)
    row_count = db.Column(db.Integer)
    last_pick_row = db.Column(db.BigInteger, default=0)
    last_pick_time = db.Column(
        db.DateTime(),
        nullable=False,
        default=datetime.now(timezone.utc).astimezone(appTimezone),
    )
    source = db.Column(db.String(), nullable=False, default="web")
    header_row = db.Column(db.Integer, nullable=False)
    email_column = db.Column(db.String())
    uploaded = db.Column(
        db.DateTime(),
        nullable=False,
        default=datetime.now(timezone.utc).astimezone(appTimezone),
    )
    started = db.Column(
        db.DateTime(),
        nullable=True,
    )
    finished = db.Column(db.DateTime(), nullable=True)
    result = db.Column(db.String(), nullable=True)

    def __init__(self, *args, **kwargs):
        """Initialize a new batch job and generate a unique ID."""
        super().__init__(*args, **kwargs)
        self.generate_job_uid()

    def generate_job_uid(self):
        """Generate a unique 6-character identifier for this job.

        Ensures uniqueness by checking against existing jobs in the database.
        """
        while True:
            new_uid = str(uuid.uuid4())[:6]
            existing_job = BatchJobs.query.filter_by(uid=new_uid).first()
            if not existing_job:
                self.uid = new_uid
                break

    def generate_results_download_link(self):
        """Generate a pre-signed download URL for the results file.

        Returns:
            str: A pre-signed URL for downloading the results file,
                or None if no results file exists.
        """
        if self.results_file:
            return generate_download_link(
                bucket_name=current_app.config["S3_BUCKET_NAME"],
                key=self.results_file,
                s3=s3,
            )
        else:
            return None

    def __repr__(self):
        """Return a string representation of the batch job.

        Returns:
            str: The unique identifier of the job.
        """
        return self.uid


class Tiers(db.Model):
    """Table for subscription tiers.

    Defines the available subscription tiers and their associated
    Stripe price IDs.

    Attributes:
        id: Primary key.
        name: Internal name of the tier.
        label: Display label for the tier.
        stripe_price_id: Associated Stripe price ID for subscriptions.
        users: Relationship to users on this tier.
    """

    __tablename__ = "Tiers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    label = db.Column(db.String(120))
    stripe_price_id = db.Column(db.String(120))

    # We use this to access the users object from the tier object
    users = db.relationship("Users", back_populates="tier")

    def __repr__(self):
        """Return a string representation of the tier.

        Returns:
            str: The name of the tier.
        """
        return self.name


class Users(db.Model, UserMixin):
    """Table for user accounts.

    Stores user account information including authentication credentials,
    profile data, subscription status, and security settings.

    Attributes:
        id: Primary key.
        email: Unique email address for the user.
        password: Bcrypt-hashed password.
        role: User role (e.g., 'user', 'admin').
        stripe_customer_id: Associated Stripe customer ID.
        tier_id: Foreign key to the subscription tier.
        credits: Number of validation credits available.
        tier: Relationship to the user's subscription tier.
        cancel_at: Scheduled subscription cancellation date.
        firstName: User's first name.
        lastName: User's last name.
        newsletter: Newsletter subscription status.
        member_since: Account creation timestamp.
        last_login: Last login timestamp.
        email_confirmation_code: Code for email verification.
        last_confirmation_codes_sent: Last time a confirmation code was sent.
        number_of_email_confirmation_codes_sent: Count of confirmation codes sent.
        email_confirmed: Whether the email is confirmed (0 or 1).
        google_avatar_url: URL to Google avatar if using OAuth.
        avatar_uploaded: Whether a custom avatar was uploaded.
        totp_secret: Secret key for TOTP two-factor authentication.
        totp_enabled: Whether TOTP is enabled (0 or 1).
        api_keys: Relationship to user's API keys.
    """

    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255))
    role = db.Column(db.String(50), default="user")

    stripe_customer_id = db.Column(db.String(50))

    # Define the Foreign Key
    tier_id = db.Column(db.Integer, db.ForeignKey("Tiers.id"))

    credits = db.Column(
        db.BigInteger, default=current_app.config["MLS_FREE_CREDITS_FOR_NEW_ACCOUNTS"]
    )

    # We use this to access the tier object from the user object
    # E.g. current_user.tier.name
    tier = db.relationship("Tiers", back_populates="users")
    cancel_at = db.Column(db.DateTime())

    firstName = db.Column(db.String())
    lastName = db.Column(db.String())

    newsletter = db.Column(db.Integer)

    member_since = db.Column(db.DateTime())
    last_login = db.Column(db.DateTime())

    email_confirmation_code = db.Column(db.String(20))
    last_confirmation_codes_sent = db.Column(
        db.DateTime(),
        default=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=10),
    )
    number_of_email_confirmation_codes_sent = db.Column(db.Integer, default=0)
    email_confirmed = db.Column(db.Integer, default=0)

    google_avatar_url = db.Column(db.String())
    avatar_uploaded = db.Column(db.Boolean(), default=False)

    totp_secret = db.Column(db.String(32), default=pyotp.random_base32())
    totp_enabled = db.Column(db.Integer, default=0)

    api_keys = db.relationship(
        "APIKeys", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def __init__(
        self,
        email,
        password,
        tier_id,
        firstName,
        lastName,
        newsletter,
        member_since,
        last_login,
        email_confirmation_code,
    ):
        """Initialize a new user account.

        Args:
            email: The user's email address.
            password: The bcrypt-hashed password.
            tier_id: The ID of the subscription tier.
            firstName: The user's first name.
            lastName: The user's last name.
            newsletter: Newsletter subscription status.
            member_since: Account creation timestamp.
            last_login: Last login timestamp.
            email_confirmation_code: Code for email verification.
        """
        self.email = email
        self.password = password
        self.tier_id = tier_id
        self.firstName = firstName
        self.lastName = lastName
        self.newsletter = newsletter
        self.member_since = member_since
        self.last_login = last_login
        self.email_confirmation_code = email_confirmation_code

    def __repr__(self):
        """Return a string representation of the user.

        Returns:
            str: The user ID and email.
        """
        return str(self.id) + " - " + str(self.user)

    def save(self):
        """Save the current state of this user to the database.

        Returns:
            Users: The saved user instance.
        """
        # inject self into db session
        db.session.add(self)

        # commit change and save the object
        db.session.commit()

        return self

    def avatar(self, size=256):
        """Get the URL for the user's avatar image.

        Returns the avatar from uploaded file, Google OAuth, or Gravatar
        in order of priority.

        Args:
            size: The size of the avatar image in pixels.

        Returns:
            str: URL to the user's avatar image.
        """
        # If the user has uploaded an avatar, we return the s3 link
        if self.avatar_uploaded:
            url = generate_download_link(
                bucket_name=current_app.config["S3_BUCKET_NAME"],
                key=f"profile-pictures/{self.id}.png",
                s3=s3,
            )

        # If the user has a google avatar, we return that
        elif not self.google_avatar_url == None:
            url = self.google_avatar_url

        # Otherwise we return a gravatar
        else:
            email_hashed = md5(self.email.encode("utf-8")).hexdigest()
            url = f"https://www.gravatar.com/avatar/{email_hashed}?d=mp&s={str(size)}"
        return url

    def is_connected_google(self):
        """Check if the user has connected their Google account.

        Returns:
            bool: True if Google account is connected, False otherwise.
        """
        return self.google_avatar_url != None

    def totp(self):
        """Get the TOTP secret and QR code for two-factor authentication setup.

        Returns:
            tuple: A tuple containing (secret, qr_code_data_uri).
        """
        secret = self.totp_secret
        totp = pyotp.TOTP(secret)

        # The provisioning url
        provisioning_url = totp.provisioning_uri(
            name=self.email, issuer_name=current_app.config["APP_NAME"]
        )

        # Return the secret and the qr code url:
        return secret, qrcode_img_src(provisioning_url)

    def totp_match(self, code):
        """Verify a TOTP code against the user's secret.

        Args:
            code: The 6-digit TOTP code to verify.

        Returns:
            bool: True if the code is valid, False otherwise.
        """
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(code)

    def totp_reset_secret(self):
        """Generate a new TOTP secret for the user.

        This invalidates any existing authenticator app configurations.
        """
        self.totp_secret = pyotp.random_base32()
        self.save()

    def folder_size(self):
        """Get the human-readable size of the user's storage folder.

        Returns:
            str: The folder size with appropriate units (e.g., '5 MB').
        """
        size = user_folder_size(self)
        return readable_file_size(size)

    def folder_quota(self):
        """Get the human-readable storage quota for the user.

        Returns:
            str: The storage quota (currently fixed at 500 MB).
        """
        return readable_file_size(500 * 1024 * 1024)

    def folder_usage_percentage(self):
        """Calculate the percentage of storage quota used.

        Returns:
            int: The usage percentage (0-100).
        """
        return int(user_folder_size(self) / (500 * 1024 * 1024) * 100)

    def add_credits(self, amount):
        """Add validation credits to the user's account.

        Args:
            amount: The number of credits to add.
        """
        self.credits += amount
        self.save()

    def deduct_credits(self, amount):
        """Deduct validation credits from the user's account.

        Args:
            amount: The number of credits to deduct.
        """
        self.credits -= amount
        self.save()
