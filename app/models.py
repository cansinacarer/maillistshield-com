from datetime import datetime, timezone, timedelta
from email.policy import default
from hashlib import md5
import pyotp

from flask_login import UserMixin

from app import app, db
from app.config import s3, appTimezone
from app.utilities.object_storage import generate_download_link, user_folder_size
from app.utilities.qr import qrcode_img_src
from app.utilities.helpers import readable_file_size


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
    password = db.Column(db.String(500))
    role = db.Column(db.String(50), default="user")

    stripe_customer_id = db.Column(db.String(50))

    # Define the Foreign Key
    tier_id = db.Column(db.Integer, db.ForeignKey("Tiers.id"))

    credits = db.Column(db.BigInteger, default=0)

    # We use this to access the tier object from the user object
    # E.g. current_user.tier.name
    tier = db.relationship("Tiers", back_populates="users")
    cancel_at = db.Column(db.DateTime())

    firstName = db.Column(db.String(120))
    lastName = db.Column(db.String(120))

    newsletter = db.Column(db.Integer)

    member_since = db.Column(db.DateTime())
    last_login = db.Column(db.DateTime())

    email_confirmation_code = db.Column(db.String(20))
    last_confirmation_codes_sent = db.Column(
        db.DateTime(),
        default=datetime.now(timezone.utc).astimezone(appTimezone)
        - timedelta(minutes=10),
    )
    number_of_email_confirmation_codes_sent = db.Column(db.Integer, default=0)
    email_confirmed = db.Column(db.Integer, default=0)

    google_avatar_url = db.Column(db.String(500))
    avatar_uploaded = db.Column(db.Boolean(), default=False)

    totp_secret = db.Column(db.String(32), default=pyotp.random_base32())
    totp_enabled = db.Column(db.Integer, default=0)

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
                bucket_name=app.config["S3_BUCKET_NAME"],
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
            name=self.email, issuer_name=app.config["APP_NAME"]
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
