from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from app.admin import admin
from app.admin.forms import CreateAdminForm, FlightForm, UpdateFlightPriceForm, DeleteFlightForm, UpdatePasswordForm
from app import mongo

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin.route('/create_flight', methods=['GET', 'POST'])
@login_required
@admin_required
def create_flight():
    if current_user.email != "admin@unipi.gr":
        flash("Sorry, you are not allowed to add new flights!", category='error')
        return redirect(url_for('admin.dashboard'))

    form = FlightForm()
    if form.validate_on_submit():
        date_str = str(form.date.data)
        time_str = form.time.data

        # Simple unique code generation
        try:
             # Just taking first letter if available, simplistic but matches legacy slightly
             dep_code = form.departure.data[0] if form.departure.data else 'X'
             dest_code = form.destination.data[0] if form.destination.data else 'X'
             # Using slicing safely
             yy = date_str[2:4] if len(date_str) >= 4 else '00'
             mm = date_str[5:7] if len(date_str) >= 7 else '00'
             dd = date_str[8:10] if len(date_str) >= 10 else '00'
             hh = time_str[0:2] if len(time_str) >= 2 else '00'

             unique_code = f"{dep_code}{dest_code}{yy}{mm}{dd}{hh}"
        except Exception as e:
             flash(f'Error generating unique code: {str(e)}', 'error')
             return render_template('admin/create_flight.html', form=form)

        flight = mongo.db.availableFlights.find_one({"unique_code": unique_code})

        if flight is None:
            new_flight = {
                'date': date_str,
                'time': time_str,
                'departure': form.departure.data,
                'destination': form.destination.data,
                "cost": float(form.cost.data),
                "availability": 220,
                "unique_code": unique_code,
                "duration": form.duration.data
            }
            mongo.db.availableFlights.insert_one(new_flight)
            flash('Flight created!', category='success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('A flight with the same unique code already exists.', category='error')

    return render_template('admin/create_flight.html', form=form)

@admin.route('/update_flight', methods=['GET', 'POST'])
@login_required
@admin_required
def update_flight():
    form = UpdateFlightPriceForm()
    if form.validate_on_submit():
        unique_code = form.unique_code.data
        new_price = form.new_price.data

        flight = mongo.db.availableFlights.find_one({"unique_code": unique_code})

        if flight:
            # Check availability to ensure no one booked it yet (as per requirement)
            # The requirement was strict about empty flight
            if int(flight.get('availability', 0)) == 220:
                 mongo.db.availableFlights.update_one(
                     {"unique_code": unique_code},
                     {"$set": {'cost': new_price}}
                 )
                 flash("Price has been updated!", category='success')
                 return redirect(url_for('admin.dashboard'))
            else:
                flash("This flight can not be updated because it is not empty!", category='error')
        else:
            flash("This code does not match a flight. Try again!", category='error')

    return render_template('admin/update_flight.html', form=form)

@admin.route('/delete_flight', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_flight():
    form = DeleteFlightForm()
    if form.validate_on_submit():
        unique_code = form.unique_code.data
        flight = mongo.db.availableFlights.find_one({"unique_code": unique_code})

        if flight:
            mongo.db.availableFlights.delete_one({"unique_code": unique_code})
            flash("Flight deleted!", category='success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash("Flight does not exist. Try again!", category='error')

    return render_template('admin/delete_flight.html', form=form)

@admin.route('/create_admin', methods=['GET', 'POST'])
@login_required
@admin_required
def create_admin():
    form = CreateAdminForm()
    if form.validate_on_submit():
        new_admin = {
            'email': form.email.data,
            'full name': form.fullname.data,
            'temp_password': form.temp_password.data,
            'password': None
        }
        mongo.db.admins.insert_one(new_admin)
        flash('Admin account created!', category='success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/create_admin.html', form=form)

@admin.route('/update_password', methods=['GET', 'POST'])
@login_required
@admin_required
def update_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        # Update admin password
        mongo.db.admins.update_one(
            {"full name": current_user.fullname},
            { "$set": { 'password': form.password.data, 'temp_password': None } }
        )
        flash('Password updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/update_password.html', form=form)
