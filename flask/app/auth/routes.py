from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, logout_user, current_user
from app import mongo
from app.auth import auth
from app.models import User
from app.auth.forms import LoginForm, RegistrationForm

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user_data = mongo.db.users.find_one({
            '$or': [
                {'email': form.email_or_username.data},
                {'username': form.email_or_username.data}
            ]
        })

        is_admin = False
        if not user_data:
            user_data = mongo.db.admins.find_one({'email': form.email_or_username.data})
            if user_data:
                is_admin = True

        if user_data:
            # Reconstruct User object
            user_obj = User(
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

            password_valid = False

            # Check password
            if is_admin and user_obj.temp_password:
                if str(user_obj.temp_password) == str(form.password.data):
                     password_valid = True
            elif user_obj.check_password(form.password.data):
                password_valid = True
            elif str(user_obj.password) == str(form.password.data): # Fallback for plain text passwords
                password_valid = True

            if password_valid:
                 if user_obj.activation_code:
                     flash('Your account is deactivated.', 'warning')
                 else:
                    login_user(user_obj)
                    next_page = request.args.get('next')
                    if is_admin:
                        # Redirect admin to change password if using temp password
                        if user_obj.temp_password:
                             flash('Please update your password.', 'info')
                             return redirect(url_for('admin.update_password'))
                        return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
                    return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')

    return render_template('auth/login.html', title='Login', form=form)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data,
            fullname=form.fullname.data,
            passport_num=form.passport_num.data
        )
        user.set_password(form.password.data)

        # Insert using to_dict to get dictionary representation
        mongo.db.users.insert_one(user.to_dict())
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html', title='Sign Up', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))
