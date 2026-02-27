from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from bson import ObjectId

class User(UserMixin):
    def __init__(self, email, username, fullname, password=None, passport_num=None, _id=None, is_admin=False, temp_password=None, activation_code=None):
        self.email = email
        self.username = username
        self.fullname = fullname
        self.password = password
        self.passport_num = passport_num
        self.id = str(_id)
        self.is_admin = is_admin
        self.temp_password = temp_password
        self.activation_code = activation_code

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            "email": self.email,
            "username": self.username,
            "fullname": self.fullname,
            "password": self.password,
            "passport_num": self.passport_num,
            "is_admin": self.is_admin,
            "temp_password": self.temp_password,
            "activation_code": self.activation_code
        }

class Flight:
    def __init__(self, date, time, departure, destination, cost, duration, availability, unique_code, _id=None):
        self.date = date
        self.time = time
        self.departure = departure
        self.destination = destination
        self.cost = cost
        self.duration = duration
        self.availability = availability
        self.unique_code = unique_code
        self.id = str(_id)

    def to_dict(self):
        return {
            "date": self.date,
            "time": self.time,
            "departure": self.departure,
            "destination": self.destination,
            "cost": self.cost,
            "duration": self.duration,
            "availability": self.availability,
            "unique_code": self.unique_code
        }

class Booking:
    def __init__(self, unique_code_flight, full_name, destination, departure, passport_num, credit_card, date, cost, user_id, _id=None):
        self.unique_code_flight = unique_code_flight
        self.full_name = full_name
        self.destination = destination
        self.departure = departure
        self.passport_num = passport_num
        self.credit_card = credit_card
        self.date = date
        self.cost = cost
        self.user_id = user_id
        self.id = str(_id)

    def to_dict(self):
        return {
            "unique_code_flight": self.unique_code_flight,
            "full_name": self.full_name,
            "destination": self.destination,
            "departure": self.departure,
            "passport_num": self.passport_num,
            "credit_card": self.credit_card,
            "date": self.date,
            "cost": self.cost,
            "user_id": ObjectId(self.user_id)
        }
