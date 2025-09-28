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
        self.user_id = user.id
        self.key_hash = key_hash
        self.label = label
        self.expires_at = expires_at

    def check_key(self, key_plain):
        return bc.check_password_hash(self.key_hash, key_plain)

    def delete_key(self):
        db.session.delete(self)
        db.session.commit()
        return True

    def save(self):
        # inject self into db session
        db.session.add(self)

        # commit change and save the object
        db.session.commit()

        return self


class BatchJobs(db.Model):
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
        super().__init__(*args, **kwargs)
        self.generate_job_uid()

    def generate_job_uid(self):
        while True:
            new_uid = str(uuid.uuid4())[:6]
            existing_job = BatchJobs.query.filter_by(uid=new_uid).first()
            if not existing_job:
                self.uid = new_uid
                break

    def generate_results_download_link(self):
        if self.results_file:
            return generate_download_link(
                bucket_name=current_app.config["S3_BUCKET_NAME"],
                key=self.results_file,
                s3=s3,
            )
        else:
            return None

    def __repr__(self):
        return self.uid


class Tiers(db.Model):
    __tablename__ = "Tiers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    label = db.Column(db.String(120))
    stripe_price_id = db.Column(db.String(120))

    # We use this to access the users object from the tier object
    users = db.relationship("Users", back_populates="tier")

    def __repr__(self):
        return self.name


class Users(db.Model, UserMixin):
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
        return str(self.id) + " - " + str(self.user)

    def save(self):
        # inject self into db session
        db.session.add(self)

        # commit change and save the object
        db.session.commit()

        return self

    def avatar(self, size=256):
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
        return self.google_avatar_url != None

    def totp(self):
        secret = self.totp_secret
        totp = pyotp.TOTP(secret)

        # The provisioning url
        provisioning_url = totp.provisioning_uri(
            name=self.email, issuer_name=current_app.config["APP_NAME"]
        )

        # Return the secret and the qr code url:
        return secret, qrcode_img_src(provisioning_url)

    def totp_match(self, code):
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(code)

    def totp_reset_secret(self):
        self.totp_secret = pyotp.random_base32()
        self.save()

    def folder_size(self):
        size = user_folder_size(self)
        return readable_file_size(size)

    def folder_quota(self):
        return readable_file_size(500 * 1024 * 1024)

    def folder_usage_percentage(self):
        return int(user_folder_size(self) / (500 * 1024 * 1024) * 100)

    def add_credits(self, amount):
        self.credits += amount
        self.save()

    def deduct_credits(self, amount):
        self.credits -= amount
        self.save()
