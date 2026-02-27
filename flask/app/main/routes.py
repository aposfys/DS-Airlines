from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from bson import ObjectId
from datetime import date
from . import main
from .forms import SearchFlightForm, BookingForm, DestinationForm
from app import mongo
from app.models import Booking

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/search_flight', methods=['GET', 'POST'])
@login_required
def search_flight():
    form = SearchFlightForm()
    flights_list = []

    if form.validate_on_submit():
        flights = mongo.db.availableFlights.find({
            "departure": form.departure.data,
            "destination": form.destination.data,
            "date": str(form.date.data)
        })

        for f in flights:
            flight = {
                'date': f.get("date"),
                'time': f.get("time"),
                'departure': f.get("departure"),
                'destination': f.get("destination"),
                'cost': f.get("cost"),
                'duration': f.get("duration"),
                'availability': f.get("availability"),
                'unique_code': f.get("unique_code")
            }
            flights_list.append(flight)

    return render_template('main/search_flight.html', form=form, flights=flights_list)

@main.route('/book_ticket/<unique_code>', methods=['GET', 'POST'])
@login_required
def book_ticket(unique_code):
    flight = mongo.db.availableFlights.find_one({'unique_code': unique_code})
    if not flight:
        flash("This flight does not exist.", category='error')
        return redirect(url_for('main.search_flight'))

    form = BookingForm()
    # Pre-fill form with user data if available
    if request.method == 'GET':
        form.full_name.data = current_user.fullname
        form.passport_num.data = current_user.passport_num

    if form.validate_on_submit():
        if int(flight['availability']) > 0:

            new_booking = {
                'unique_code_flight': unique_code,
                'full_name': form.full_name.data,
                'destination': flight['destination'],
                'departure': flight['departure'],
                'passport_num': form.passport_num.data,
                'credit_card': form.credit_card.data,
                'date': str(date.today()),
                'cost': flight['cost'],
                "user_id": ObjectId(current_user.get_id())
            }

            mongo.db.bookings.insert_one(new_booking)
            mongo.db.availableFlights.update_one(
                {'unique_code': unique_code},
                {'$set': {'availability': int(flight['availability']) - 1}}
            )

            flash('Ticket booked successfully!', 'success')
            return redirect(url_for('main.show_all_bookings'))
        else:
            flash("This flight has no empty seats!", category='error')
            return redirect(url_for('main.search_flight'))

    return render_template('main/book_ticket.html', form=form, flight=flight)

@main.route('/my_bookings')
@login_required
def show_all_bookings():
    sort_order = request.args.get('sort', 'desc')
    sort_direction = -1 if sort_order == 'desc' else 1

    bookings_cursor = mongo.db.bookings.find(
        {"user_id": ObjectId(current_user.get_id())}
    ).sort("date", sort_direction)

    bookings = []
    for b in bookings_cursor:
        b['booking_id'] = str(b['_id'])
        bookings.append(b)

    return render_template('main/my_bookings.html', bookings=bookings)

@main.route('/cancel_booking/<booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = mongo.db.bookings.find_one({'_id': ObjectId(booking_id), "user_id": ObjectId(current_user.get_id())})

    if booking:
        mongo.db.bookings.delete_one({"_id": ObjectId(booking_id)})

        # Optionally, increase availability of the flight
        mongo.db.availableFlights.update_one(
            {'unique_code': booking['unique_code_flight']},
            {'$inc': {'availability': 1}}
        )

        flash(f"Booking cancelled. Refund will be processed to card ending in {booking['credit_card'][-4:]}.", 'success')
    else:
        flash("Booking not found or access denied.", 'error')

    return redirect(url_for('main.show_all_bookings'))

@main.route('/deactivate_account', methods=['POST'])
@login_required
def deactivate_account():
    import random
    # Generate a random activation code
    code = random.randint(100000000000, 100000001000)

    mongo.db.users.update_one(
        {"_id": ObjectId(current_user.get_id())},
        { "$set": { "activation_code": code } }
    )

    # Log the user out
    from flask_login import logout_user
    logout_user()

    flash(f"Your account has been deactivated! Your activation code is {code}. Use it to reactivate your account!", 'warning')
    return redirect(url_for('main.home'))

@main.route('/activate_account', methods=['GET', 'POST'])
def activate_account():
    if request.method == 'POST':
        code = request.form.get('activation_code')
        try:
            code = int(code)
        except ValueError:
            flash("Invalid code format.", 'error')
            return redirect(url_for('main.activate_account'))

        user = mongo.db.users.find_one({"activation_code": code})

        if user:
            mongo.db.users.update_one(
                {"_id": user['_id']},
                {"$set": {'activation_code': None}}
            )
            flash("Your account has been activated! Please login.", 'success')
            return redirect(url_for('auth.login'))
        else:
            flash("Invalid activation code!", 'error')

    return render_template('main/activate_account.html')
