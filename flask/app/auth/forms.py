from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, ValidationError
from app import mongo

class LoginForm(FlaskForm):
    email_or_username = StringField('Email or Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long'),
        Regexp(r'.*\d.*', message='Password must contain at least one number')
    ])
    passport_num = StringField('Passport Number', validators=[
        DataRequired(),
        Length(min=9, max=9, message='Passport number must be exactly 9 characters long'),
        Regexp(r'^[A-Za-z]{2}\d{7}$', message='Passport number must consist of two letters followed by 7 digits')
    ])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = mongo.db.users.find_one({'username': username.data})
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = mongo.db.users.find_one({'email': email.data})
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')
