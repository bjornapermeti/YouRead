from flask_wtf import Form
from wtforms import (
    TextField,
    PasswordField,
    BooleanField,
    DateField,
    IntegerField,
    DecimalField,
)
from wtforms.fields.html5 import EmailField

from wtforms.validators import DataRequired, Length, Email


class SignupForm(Form):
    name = TextField(
        "e.g. Bjorna Permeti", validators=[DataRequired(), Length(min=4, max=25)]
    )
    email = EmailField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=200)]
    )
    user_type = BooleanField()


class EditAccountForm(Form):
    name = TextField(
        "e.g. Alice Doe", validators=[DataRequired(), Length(min=4, max=25)]
    )
    email = TextField("Email", validators=[DataRequired(), Length(min=6, max=40)])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=200)]
    )
    verify_password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=200)]
    )
    user_type = TextField("admin | normal")


class UpdatePasswordForm(Form):
    old_password = PasswordField(
        "Old Password", validators=[DataRequired(), Length(min=8, max=200)]
    )
    new_password = PasswordField(
        "New Password", validators=[DataRequired(), Length(min=8, max=200)]
    )
    verify_password = PasswordField(
        "Verify New Password", validators=[DataRequired(), Length(min=8, max=200)]
    )


class UpdateEmailForm(Form):
    email = EmailField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=200)]
    )


class UpdateNameForm(Form):
    name = TextField(
        "e.g. Alice Doe", validators=[DataRequired(), Length(min=4, max=25)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=200)]
    )


class LoginForm(Form):
    email = EmailField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
