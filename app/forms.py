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
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    firstName = StringField("First Name", validators=[DataRequired()])
    lastName = StringField("Last Name")
    newsletter = BooleanField("Subscribe")


class EmailConfirmationForm(FlaskForm):
    code0 = StringField("code0", validators=[InputRequired()])
    code1 = StringField("code1", validators=[InputRequired()])
    code2 = StringField("code2", validators=[InputRequired()])
    code3 = StringField("code3", validators=[InputRequired()])
    code4 = StringField("code4", validators=[InputRequired()])
    code5 = StringField("code5", validators=[InputRequired()])


class ResetPassword(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])


class SetNewPassword(FlaskForm):
    password = PasswordField("password", validators=[DataRequired()])


class ProfileDetailsForm(FlaskForm):
    firstName = StringField("First Name", validators=[DataRequired()])
    lastName = StringField("Last Name")
    newsletter = BooleanField("Subscribe")


class TwoFactorAuthenticationForm(FlaskForm):
    code0 = StringField("code0", validators=[InputRequired()])
    code1 = StringField("code1", validators=[InputRequired()])
    code2 = StringField("code2", validators=[InputRequired()])
    code3 = StringField("code3", validators=[InputRequired()])
    code4 = StringField("code4", validators=[InputRequired()])
    code5 = StringField("code5", validators=[InputRequired()])


class CreateAPIKeyForm(FlaskForm):
    label = StringField("Label", validators=[Length(max=120)])
    expires_at = DateField(
        "Expiration Date (optional)", format="%Y-%m-%d", validators=[]
    )
    submit = SubmitField("Create API Key")
