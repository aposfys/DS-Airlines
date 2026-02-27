from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from config import config
from app.models import User
from bson import ObjectId

mongo = PyMongo()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    mongo.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Check users collection
        user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        is_admin = False

        # Check admins collection if not found
        if not user_data:
             user_data = mongo.db.admins.find_one({'_id': ObjectId(user_id)})
             if user_data:
                 is_admin = True

        if user_data:
             return User(
                email=user_data.get('email'),
                username=user_data.get('username') or user_data.get('full name'),
                fullname=user_data.get('fullname') or user_data.get('full name'),
                password=user_data.get('password'),
                passport_num=user_data.get('passport_num'),
                _id=user_data.get('_id'),
                is_admin=is_admin,
                temp_password=user_data.get('temp_password'),
                activation_code=user_data.get('activation_code')
            )
        return None

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from app.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app
