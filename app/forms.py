"""WTForms form definitions for the Mail List Shield application.

This module defines Flask-WTF form classes for user authentication,
profile management, and API key creation.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import (
    StringField,
    TextAreaField,
    SubmitField,
    PasswordField,
    DateField,
    IntegerField,
    BooleanField,
    RadioField,
)
from wtforms.validators import Email, NumberRange, InputRequired, DataRequired, Length


class LoginForm(FlaskForm):
    """Form for user login.

    Attributes:
        email: Email address field with validation.
        password: Password field with validation.
    """

    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


class RegisterForm(FlaskForm):
    """Form for new user registration.

    Attributes:
        email: Email address field with validation.
        password: Password field with validation.
        firstName: First name field (required).
        lastName: Last name field (optional).
        newsletter: Newsletter subscription checkbox.
    """

    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    firstName = StringField("First Name", validators=[DataRequired()])
    lastName = StringField("Last Name")
    newsletter = BooleanField("Subscribe")


class EmailConfirmationForm(FlaskForm):
    """Form for email confirmation code entry.

    Contains 6 individual fields for each digit of the confirmation code.

    Attributes:
        code0-code5: Individual digit fields for the 6-digit confirmation code.
    """

    code0 = StringField("code0", validators=[InputRequired()])
    code1 = StringField("code1", validators=[InputRequired()])
    code2 = StringField("code2", validators=[InputRequired()])
    code3 = StringField("code3", validators=[InputRequired()])
    code4 = StringField("code4", validators=[InputRequired()])
    code5 = StringField("code5", validators=[InputRequired()])


class ResetPassword(FlaskForm):
    """Form for requesting a password reset.

    Attributes:
        email: Email address field for the account to reset.
    """

    email = StringField("Email", validators=[DataRequired(), Email()])


class SetNewPassword(FlaskForm):
    """Form for setting a new password after reset.

    Attributes:
        password: New password field with validation.
    """

    password = PasswordField("password", validators=[DataRequired()])


class ProfileDetailsForm(FlaskForm):
    """Form for updating user profile details.

    Attributes:
        firstName: First name field (required).
        lastName: Last name field (optional).
        newsletter: Newsletter subscription checkbox.
    """

    firstName = StringField("First Name", validators=[DataRequired()])
    lastName = StringField("Last Name")
    newsletter = BooleanField("Subscribe")


class TwoFactorAuthenticationForm(FlaskForm):
    """Form for two-factor authentication code entry.

    Contains 6 individual fields for each digit of the TOTP code.

    Attributes:
        code0-code5: Individual digit fields for the 6-digit TOTP code.
    """

    code0 = StringField("code0", validators=[InputRequired()])
    code1 = StringField("code1", validators=[InputRequired()])
    code2 = StringField("code2", validators=[InputRequired()])
    code3 = StringField("code3", validators=[InputRequired()])
    code4 = StringField("code4", validators=[InputRequired()])
    code5 = StringField("code5", validators=[InputRequired()])


class CreateAPIKeyForm(FlaskForm):
    """Form for creating a new API key.

    Attributes:
        label: Optional label for identifying the API key.
        expires_at: Optional expiration date for the key.
        submit: Submit button.
    """

    label = StringField("Label", validators=[Length(max=120)])
    expires_at = DateField(
        "Expiration Date (optional)", format="%Y-%m-%d", validators=[]
    )
    submit = SubmitField("Create API Key")
