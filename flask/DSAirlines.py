import random
from pymongo import MongoClient
import os
from flask import Flask, jsonify, request, render_template ,redirect, url_for, flash, session
from bson.objectid import ObjectId
from datetime import date


# Connect to the local MongoDB
mongodb_hostname = os.environ.get("MONGO_HOSTNAME","localhost")
client = MongoClient('mongodb://'+mongodb_hostname+':27017/')

# Initiate Flask App
app = Flask(__name__)

# DS Airlines database
db = client['DSAirlines']
# users collection (these are the simple users)
users = db['users']
#admins collection
admins = db['admins']
# available flights collection
availableFlights = db['availableFlights']
# reserved flights collection
bookings = db['bookings']


# create the first admin
first_admin = admins.find_one({'email':"admin@unipi.gr"})
if first_admin is None:
    admins.insert_one({'email':"admin@unipi.gr", 'full name': "Admin", 'temp_password': "pass123", 'password': None })

# SERVICES
# welcome page
@app.route('/')
def welcome():
    if 'username' in session:
        flash('You are logged in as ' + session['username'], category='info')

    return render_template('welcome.html')

# SIMPLE USERS
# check if current loged in user is a simple user (not an admin)
def user_check():
    user = users.find_one({"username":session['username']})
    if user!= None:
        return True
    else:
        return False

# sign up endpoint
@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    #POST request
    if request.method == 'POST':
        # data from the form
        email = request.form.get('email')
        username = request.form.get('username')
        fullname =  request.form.get('fullname')
        password = request.form.get('password')
        passport_num = request.form.get('passport_num')

        # password check
        if len(password) < 8:
            flash('The password you provided is too small. Try a password with at least 8 characters!', category='error')
            return render_template('sign_up.html')
        if not any(char.isdigit() for char in password):
            flash('The password you provided has no numbers. Try a password with at least 1 number!', category='error')
            return render_template('sign_up.html')

        # passport number check
        if len(passport_num) != 9:
            flash('The passport number is not the correct size. Try again!', category='error')
            flash('Note: The passport number consists of two characters followed by 7 digits. ', category='info')
            return render_template('sign_up.html')
        if not passport_num[2:9].isdigit():
            flash('The passport number is incorrect. Try again!', category='error')
            flash('Note: The passport number consists of two characters followed by 7 digits. ', category='info')
            return render_template('sign_up.html')
        if not passport_num[0:2].isalpha():
            flash('The passport number is incorrect. Try again!', category='error')
            flash('Note: The passport number consists of two characters followed by 7 digits. ', category='info')
            return render_template('sign_up.html')

        # check if there is a user with this email already
        user_email = users.find_one({"email": email})
        # check if the username is already beeing used
        user_username = users.find_one({"username":username})
        # check if the number of the password is already registered to another user
        user_passport_num = users.find_one({"passport_num":passport_num})

        if (user_email is None) and (user_username is None) and (user_passport_num is None):
            new_user = {'email' : email, 'username' : username, 'fullname': fullname, 'password': password, 'passport_num':passport_num, 'activation_code':None}
            users.insert_one(new_user)
            flash('Account created!', category='success')
            return redirect(url_for('login'))
        elif user_email:
            flash('A user with this email already exists. Try again!', category='error')
            return render_template('sign_up.html')
        elif user_username:
            flash('A user with this username already exists. Try again!', category='error')
            return render_template('sign_up.html')
        elif user_passport_num:
            flash('A user with this passport number already exists.Try again!', category='error')
            return render_template('sign_up.html')

    # GET request
    else:
        return render_template('sign_up.html')

# login endpoint        
@app.route('/login', methods= ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('e_or_u') # e_or_u is short for email or password (because we dont know what the user provided) 
        username = request.form.get('e_or_u')
        password =  request.form.get('password')

        user_email = users.find_one({"email":email})
        user_username = users.find_one({"username":username})

        #login with email
        if user_email:
            if user_email['activation_code'] is None:
                user_email_password = user_email['password']
                if str(user_email_password) == str(password):
                    flash("Succesfull login!", category='success')
                    session['username'] = user_email['username']
                    return redirect(url_for('menu'))
                else:
                    flash("Invalid password. Try again!", category= 'error')
                    return redirect(url_for('login'))
            else:
                flash("You account is deactivated!", category='error')
                return redirect(url_for('welcome'))
        
        #login with username
        elif user_username:
            
            if isinstance(user_username['activation_code'], type(None)):
            
                user_username_password = user_username['password']
                if str(user_username_password) == str(password):
                    session['username'] = user_username['username']
                    flash("Succesfull login!", category='success')
                    return redirect(url_for('menu'))
                else:
                    flash("Invalid password. Try again!", category= 'error')
                    return redirect(url_for('login'))
            else:
                flash("Your account has been deactivated!", category='error')
                return redirect(url_for('welcome'))
        
        #user does not exist
        else:
            flash("Invalid username or email. Try again!", category= 'error')
            return redirect(url_for('login'))
    else:
        #if user is already loged in
        if ("username" in session) and user_check():
            return redirect(url_for('menu'))
        return render_template('login.html')

# menu for simple users endpoint
@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if ("username" in session) and user_check():
        return render_template('menu.html')
    else:
        flash("Login first!", category='error')
        return redirect(url_for('login'))

# search flight endpoint
@app.route('/search_flight', methods=['GET','POST'])
def search_flight():
    if ("username" in session) and user_check():
        if request.method == 'POST':
            departure = request.form.get('departure') 
            destination = request.form.get('destination')
            date = request.form.get('date')

            flights = availableFlights.find(filter={"departure": departure , "destination": destination, "date": date })
            flights_list=[]
            for f in flights:
                flight = {'date':f["date"], 'time':f["time"], 'departure':f["departure"], 'destination':f["destination"], 'cost':f["cost"], 'duration':f["duration"], 'availability':f["availability"], 'unique_code':f["unique_code"]}
                flights_list.append(flight)
            return jsonify(flights_list)
            
        else: 
            return render_template('search_flight.html')           

    else:
        flash("Login first!", category='error')
        return redirect(url_for('login'))
    
# book a ticket endpoint
@app.route('/book_ticket', methods=['GET','POST'])
def book_ticket():
    
    if ("username" in session) and user_check():
        if request.method == 'POST':
            unique_code = request.form.get('unique_code')
            full_name = request.form.get('full_name')
            passport_num = request.form.get('passport_num')
            credit_card = request.form.get('credit_card')

            if len(credit_card) != 16:
                flash("Credit card number is not valid. Try again!",category='error')
                return redirect(url_for('menu'))
            else:
                flight = availableFlights.find_one({'unique_code':unique_code})
                if flight:
                    if int(flight['availability']) > 0:
                        
                        user = users.find_one({"username":session['username']})

                        _id = bookings.insert_one({'unique_code_flight' : unique_code, 'full_name': full_name, 'destination':flight['destination'], 'departure':flight['departure'], 'passport_num': passport_num, 'credit_card':credit_card, 'date': str(date.today()) , 'cost': flight['cost'],"user_id":user['_id']}).inserted_id
                        availableFlights.update_one({'unique_code':unique_code}, {'$set':{'availability':int(flight['availability'])-1}})
                        
                        booking = bookings.find_one({'_id': _id})
                        if booking:
                            booking = {'unique_code_flight':booking["unique_code_flight"],'full_name':booking["full_name"], 'passport_num':booking["passport_num"], 'credit_card':booking['credit_card'], 'date': booking['date'] , 'cost': flight['cost'], 'booking_id':str(_id)}
                            return jsonify(booking)
                    else:
                        flash("This flight has no empty seats!", categore='error')
                        return redirect(url_for('menu'))
                else:
                    flash("This flight does not exist.", category='error')
                    return redirect(url_for('menu'))
        else: 
            return render_template('book_ticket.html')           

    else:
        flash("Login first!", category='error')
        return redirect(url_for('login'))


# show booking
@app.route('/show_booking', methods= ['GET', 'POST'])
def show_booking():
    
    if ("username" in session) and user_check():
        if request.method == 'POST':
            booking_id = request.form.get('booking_id')
            user = users.find_one({"username":session['username']})

            booking = bookings.find_one({'_id': ObjectId(booking_id), "user_id":user['_id']})
            if booking:
                booking = {'booking_id': str(booking["_id"]),'unique_code_flight':booking["unique_code_flight"],'full_name':booking["full_name"], 'passport_num':booking["passport_num"], 'credit_card':booking['credit_card'], 'date': booking['date'] , 'cost': booking['cost'], "user_id": str(user['_id'])}
                return jsonify(booking)
            else:
                flash("This booking does not exist!", category='error')
                return redirect(url_for('menu'))
        else: 
            return render_template('show_booking.html')           

    else:
        flash("Login first!", category='error')
        return redirect(url_for('login'))

# cancel booking
@app.route('/cancel_booking', methods= ['GET', 'POST'])
def cansel_booking():
    
    if ("username" in session) and user_check():
        if request.method == 'POST':
            booking_id = request.form.get('booking_id')
            user = users.find_one({"username":session['username']})

            booking = bookings.find_one({'_id': ObjectId(booking_id), "user_id":user['_id']})
            if booking:
                credit_card = booking['credit_card']
                booking =  bookings.delete_one({"_id": ObjectId(booking_id), "user_id":user['_id']})
                flash("Booking was deleted succesfully!", category='success')
                flash("You will get a refund on this card: " + credit_card + ".", category='success')
                return redirect(url_for('menu'))
            else:
                flash("This booking does not exist!", category='error')
                return redirect(url_for('menu'))
        else: 
            return render_template('cancel_booking.html')           

    else:
        flash("Login first!", category='error')
        return redirect(url_for('login'))

# show all bookings
@app.route('/show_all_bookings', methods= ['GET', 'POST'])
def show_all_bookings():
    
    if ("username" in session) and user_check():
        if request.method == 'POST':
            
            user = users.find_one({"username":session['username']})

            if request.form['choice'] == 'Oldest to newest':
                all_bookings = bookings.find(filter={"user_id":user['_id']}, sort=[("date", 1)])
                bookings_list =[]
                for b in all_bookings:
                    booking = {'booking_id': str(b["_id"]),'unique_code_flight':b["unique_code_flight"],'full_name':b["full_name"], 'passport_num':b["passport_num"], 'credit_card':b['credit_card'], "user_id": str(user['_id'])}
                    bookings_list.append(booking)
                return jsonify(bookings_list)
            elif request.form['choice'] == 'Newest to oldest':
                all_bookings = bookings.find(filter={"user_id":user['_id']}, sort=[("date", -1)])
                bookings_list =[]
                for b in all_bookings:
                    booking = {'booking_id': str(b["_id"]),'unique_code_flight':b["unique_code_flight"],'full_name':b["full_name"], 'passport_num':b["passport_num"], 'credit_card':b['credit_card'], "user_id": str(user['_id'])}
                    bookings_list.append(booking)
                return jsonify(bookings_list)

        else: 
            return render_template('show_all_bookings.html')           

    else:
        flash("Login first!", category='error')
        return redirect(url_for('login'))


# show bookings with greater and lesser cost
@app.route('/show_bookings_cost', methods= ['GET', 'POST'])
def show_bookings_cost():
    
    if ("username" in session) and user_check():
        if request.method == 'POST':
            
            user = users.find_one({"username":session['username']})

            # sort bookings by cost and date
            sorted_bookings =  bookings.find(filter={"user_id":user['_id']}, sort=[("cost", 1), ("date", -1)])
            #to check that there is at least one document
            booking_check = bookings.find_one(filter={"user_id":user['_id']})

            bookings_list=[]
            if booking_check:
                for b in sorted_bookings:
                    booking = {'booking_id':str(b["_id"]),'unique_code_flight':b["unique_code_flight"],'full_name':b["full_name"], 'passport_num':b["passport_num"], 'credit_card':b['credit_card'], 'date': b['date'] , 'cost': b['cost'], "user_id": str(b['user_id'])}
                    bookings_list.append(booking)

                return jsonify({'priciest booking':bookings_list[-1], 'cheapest_booking':bookings_list[0]})
            else:
                flash("No bookings were found!", category='error')
                return redirect(url_for('menu'))

    else:
        flash("Login first!", category='error')
        return redirect(url_for('login'))

#show all bookings for a destination
@app.route('/show_bookings_destination', methods= ['GET', 'POST'])
def show_bookings_destination():
    
    if ("username" in session) and user_check():
        if request.method == 'POST':
            
            destination = request.form.get('destination')

            user = users.find_one({"username":session['username']})
            all_bookings = bookings.find({"destination":destination, "user_id":user['_id']})
            #to check that there is at least one document
            booking_check = bookings.find_one({"destination":destination, "user_id":user['_id']})

            if booking_check:
                bookings_list=[]
                for b in all_bookings:
                    booking = {'booking_id':str(b["_id"]),'unique_code_flight':b["unique_code_flight"],'full_name':b["full_name"], 'passport_num':b["passport_num"], 'credit_card':b['credit_card'], 'date': b['date'] , 'cost': b['cost'], "user_id": str(b['user_id'])}
                    bookings_list.append(booking)
                return jsonify(bookings_list)
            else:
                flash("There are no bookings for this destination. Try again!", category='error')
                return redirect(url_for('menu'))
                
        else: 
            return render_template('show_bookings_destination.html')           

    else:
        flash("Login first!", category='error')
        return redirect(url_for('login'))

# deactivate account endpoint
# all numbers with 12digits - they will be used as activation codes
codes = [*range(100000000000, 100000001000, 1)]
@app.route('/deactivate_account', methods= ['GET', 'POST'])
def deactivate_account():
    
    if ("username" in session) and user_check():
        if request.method == 'POST':
            
            user = users.find_one({"username":session['username']})

            global codes

            #choose an activation code
            activation_code = random.sample(codes, 1)
            users.update_one({"_id": user['_id']}, { "$set": { "activation_code": activation_code[0] } }) 
            flash("You account has been deactivated! Your activation code is " + str(activation_code[0]) + " use it to reactivate your account!",  category='success')
            codes.remove(activation_code[0])
            return redirect(url_for('menu'))       

    else:
        flash("Login first!", category='error')
        return redirect(url_for('login'))

# activate your account endpoint
@app.route('/activate_account', methods= ['GET', 'POST'])
def activate_account():
    
    if request.method == 'POST':
        
        activation_code =  request.form.get('activation_code')

        user = users.find_one({"activation_code":int(activation_code)})

        if user:
            users.update_one({"_id":user['_id']}, {"$set":{'activation_code':None}} ) 
            flash("You account has been activated!", category='success')
            return redirect(url_for('welcome'))
        else:
            flash("Invalid activation code!", category='error')
            return redirect(url_for('welcome'))    
    else: 
        return render_template('activate_account.html')  


# ADMINS
#function to ckeck if current logged in user is an admin
def admin_check():
    user = admins.find_one({"full name":session['username']})
    if user!= None:
        return True
    else:
        return False
        
#login as a admin endpoint
@app.route('/login_admin', methods= ['GET', 'POST'])
def login_admin():
    if request.method == 'POST':

        email = request.form.get('email')
        password =  request.form.get('password')

        admin = admins.find_one({"email":email})
        
        if admin:
            if admin["temp_password"] == None: #if temp password is None then this admin has logged in before and there is no need to replace the password

                if admin['password'] == password:
                    flash("Succesfull login!", category='success')
                    session['username'] = admin['full name']
                    return redirect(url_for('menu_admin'))
                else:
                    flash("Invalid password. Try again!", category= 'error')
                    return redirect(url_for('login_admin'))
            else: 
                # this admin loges in for the first time
                if admin['temp_password'] == password: #admin provided the correct temporary password
                    session['username'] = admin['full name']
                    return redirect(url_for('update_password')) #admin has to change the password
                else:
                    flash("Invalid temporary password. Try again!", category= 'error')
                    return redirect(url_for('login_admin'))
        
        #user does not exist
        else:
            flash("This admin does not exist!", category= 'error')
            return redirect(url_for('login_admin'))
    else:
        #if admin is already logged in
        if ("username" in session) and admin_check():
            return redirect(url_for('menu_admin'))
        
        #GET method
        return render_template('login_admin.html')

# update password for new admins
@app.route('/update_password', methods = ['POST', 'GET'])
def update_password():
    if ("username" in session) and admin_check():
        if request.method == 'POST':
            password = request.form.get('password') # get the new password
            admins.update_one({"full name": session["username"]}, { "$set": { 'password': password } }) # update password
            admins.update_one({"full name": session["username"]}, { "$set": { 'temp_password': None } }) #set temporary password to None so that the system will know that this admin has logged in before and uses an updated password
            return redirect(url_for('menu_admin'))
        else: 
            return render_template('update_password.html')           

    else:
        flash("Login first!", category='error')
        return redirect(url_for('login_admin'))

# menu for admins endpoint
@app.route('/menu_admin', methods= ['GET'])
def menu_admin():
    if ("username" in session) and admin_check():
        return render_template('menu_admin.html')
    else:
        flash("Login first!", category='error')
        return redirect(url_for('login_admin'))

# create new admin endpoint
@app.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    if ("username" in session) and admin_check():
        if request.method == 'POST':
            # data from the form
            email = request.form.get('email')
            fullname =  request.form.get('fullname')
            temp_password = request.form.get('temp_password')

            admin = admins.find_one({"email": email})

            if admin is None:
                new_admin = {'email' : email, 'full name': fullname, 'temp_password': temp_password, 'password': None}
                admins.insert_one(new_admin)
                flash('Account created!', category='success')
                return redirect(url_for('menu_admin'))
            else:
                flash('An admin with this email already exists.', category='error')
                return redirect(url_for('menu_admin'))
        # for a GET request
        else:
            return render_template('create_admin.html')
    else:
        flash("Login first!", category='error')
        return redirect(url_for('login_admin'))


# create flight endpoint
@app.route('/create_flight', methods=['GET', 'POST'])
def create_flight():
    if ("username" in session) and admin_check():
        admin = admins.find_one({"full name": session['username']}) # current logged in admin
        if admin['email'] == "admin@unipi.gr":
            if request.method == 'POST':
                # data from the form
                date = request.form.get('date')
                time =  request.form.get('time')
                departure = request.form.get('departure')
                destinaton = request.form.get('destination')
                cost = request.form.get('cost')
                duration = request.form.get('duration')
                availability = 220
                unique_code = departure[0]+destinaton[0]+date[2:4]+date[5:7]+date[8:10]+time[0:2]

                flight = availableFlights.find_one({"unique_code": unique_code})

                if flight is None:
                    new_flight = {'date' : date, 'time': time, 'departure': departure, 'destination': destinaton, "cost":cost, "availability":availability, "unique_code":unique_code, "duration":duration}
                    availableFlights.insert_one(new_flight)
                    flash('Flight created!', category='success')
                    return redirect(url_for('menu_admin'))
                else:
                    flash('A flight with the same unique code already exists.', category='error')
                    return redirect(url_for('menu_admin'))
            # for a GET request
            else:
                return render_template('create_flight.html')
        else:
            flash("Sorry, you are not allowed to add new flights!", category='error')
            return redirect(url_for('menu_admin'))
    else:
        flash("Login first!", category='error')
        return redirect(url_for('login_admin'))

# update flight's price
@app.route('/update_flight', methods=['GET', 'POST'])
def update_flight():
    if ("username" in session) and admin_check():
        if request.method == 'POST':
            
            unique_code = request.form.get('unique_code')
            new_price = request.form.get('new_price')

            flight = availableFlights.find_one({"unique_code":unique_code})

            if flight:
                if flight['availability'] == 220:
                    if float(new_price) > 0: 
                        availableFlights.update_one({"unique_code": unique_code }, { "$set": { 'price': new_price } })
                        flash("Price has been updated!", category='success')
                        return redirect(url_for('menu_admin'))
                    else:
                        flash("This price is not valid. Try again!", category='error')
                        return redirect(url_for('menu_admin'))
                else:
                    flash("This flight can not be updates because it is not empty!", category='error')
                    return redirect(url_for('menu_admin'))
            else:
                flash("This code does not match a flight. Try again!", category='error' )
                return redirect(url_for('menu_admin'))
        else:
            #GET method
            return render_template('update_flight.html')
    else:
        flash("Login first!", category='error')
        return redirect(url_for('login_admin'))

# delete flight
@app.route('/delete_flight', methods=['GET', 'POST'])
def delete_flight():
    if ("username" in session) and admin_check():
        if request.method == 'POST':
            unique_code = request.form.get('unique_code')

            flight = availableFlights.find_one({"unique_code":unique_code})

            if flight:
                availableFlights.delete_one({"unique_code":unique_code})
                flash("Flight deleted!", category='success')
                return redirect(url_for('menu_admin'))
            else:
                flash("Flight does not exist. Try again!", category='error')
                return redirect(url_for('menu_admin'))
        else:
            #GET method
            return render_template('delete_flight.html')
    else:
        flash("Login first!", category='error')
        return redirect(url_for('login_admin'))

#logout for admins and simple users
@app.route("/logout", methods=['GET'])
def logout():
    if "username" in session:
        #GET method
        session.pop("username", None)
        return render_template('welcome.html')
    else:
        flash("Login first!", category='error')
        return redirect(url_for('welcome'))    



# Run Flask App
if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run(debug=True, host='0.0.0.0', port=5000)