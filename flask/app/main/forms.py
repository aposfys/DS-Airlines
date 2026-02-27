from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, Length

class SearchFlightForm(FlaskForm):
    departure = StringField('Departure', validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Search')

class BookingForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    passport_num = StringField('Passport Number', validators=[DataRequired(), Length(min=9, max=9)])
    credit_card = StringField('Credit Card Number', validators=[DataRequired(), Length(min=16, max=16)])
    submit = SubmitField('Book Ticket')

class DestinationForm(FlaskForm):
    destination = StringField('Destination', validators=[DataRequired()])
    submit = SubmitField('Show Bookings')
