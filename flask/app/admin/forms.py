from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, FloatField, PasswordField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError
from app import mongo

class CreateAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    fullname = StringField('Full Name', validators=[DataRequired()])
    temp_password = StringField('Temporary Password', validators=[DataRequired()])
    submit = SubmitField('Create Admin')

    def validate_email(self, email):
        admin = mongo.db.admins.find_one({'email': email.data})
        if admin:
             raise ValidationError('An admin with this email already exists.')

class FlightForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    time = StringField('Time', validators=[DataRequired()])
    departure = StringField('Departure', validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired()])
    cost = FloatField('Cost', validators=[DataRequired(), NumberRange(min=0)])
    duration = StringField('Duration', validators=[DataRequired()])
    submit = SubmitField('Create Flight')

class UpdateFlightPriceForm(FlaskForm):
    unique_code = StringField('Unique Code', validators=[DataRequired()])
    new_price = FloatField('New Price', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Update Price')

class DeleteFlightForm(FlaskForm):
    unique_code = StringField('Unique Code', validators=[DataRequired()])
    submit = SubmitField('Delete Flight')

class UpdatePasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Update Password')
