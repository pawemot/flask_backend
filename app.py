import threading
from flask import Flask, json, request, jsonify, session
import schedule
import time
from database import db
from show_json import show_json
from bson import ObjectId
from flask_cors import CORS
from get_weather import get_weather
from werkzeug.security import generate_password_hash, check_password_hash
import re
from regex_pw import password_regex, email_regex
from session_expiration import session_expiration
from datetime import datetime, timedelta


app = Flask(__name__)

cors = CORS(app, support_credentials = True)
app.config['CORS_HEADERS'] = 'Content-Type'

app.secret_key = "3244o32koppokmnkjnsew1"
app.permanent_session_lifetime = timedelta(minutes=1)

@app.route("/create-travel", methods = ["GET","POST"])
def create_travel():
    if 'email' in session:
        title = request.json["title"]
        price = request.json["price"]
        country = request.json["country"]
        desc = request.json["desc"]
        image = request.json["image"]

        travel_exist= db.travels.find_one({"title":title})

        if travel_exist:
            return show_json("Dodana wycieczka istnieje", 405 , False)

        db.travels.insert_one( {
            "title" : title,
            "price" : price,
            "country" : country,
            "desc" : desc,
            "image" : image
        })

        print(title)
        return show_json("Udało się dodać wycieczkę", 200, True)
    else:
        return show_json("Odmowa dostępu", 401, False)
@app.route("/show-travels", methods = ["GET"])
def show_travels():
    data = db.travels.find({})
    all_travels = []
    for item in data:
        item['_id'] = str(item['_id'])
        all_travels.append(item)
    print(all_travels)
    if all_travels:
        return show_json("Udało się wczytać wycieczki", 200, True, all_travels)
    else: 
        return show_json("Nie udało się wczytać danych", 405, False)
    
@app.route("/single-travel/<id>")
def single_travel(id):
    try:    
        travel = list(db.travels.find({"_id":ObjectId(id)}))[0]
        travel["_id"] = str(travel['_id'])
    
        return show_json("Znaleziono podróż",200,True,travel) 
    except Exception as e:
        print(e)
        return show_json("Nie udało się odnaleźć podróży", 404, False)
    
@app.route("/edit-travel/<id>", methods = ["PUT"])
def edit_travel(id):
    try:
        travel_json = request.json

        travel = db.travels.update_one({"_id":ObjectId(id)},{"$set":travel_json})

        if travel.modified_count == 1:
            return show_json("Zaktualizowano",200,True)
        else:
            return show_json("Nie odnaleziono wycieczki",404,False)
        
    except Exception as e:
        print(e)
        return show_json("Nie odnaleziono wycieczki",404,False)
    
@app.route("/delete-travel/<id>", methods = ["DELETE"])
def delete_travel(id):
    try:
        travel = db.travels.delete_one({"_id" : ObjectId(id)})
        return show_json("Usunięto",200,True)
        
    except Exception as e:
        print(e)
        return show_json("Nie odnaleziono wycieczki",404,False)

# def download_weather_data():
#     get_weather()
#     threading.Timer(600.0, download_weather_data).start()

# download_weather_data()

# schedule.every(5).minutes.do(get_weather)

# while True:
#         schedule.run_pending()
#         time.sleep(1) 

@app.route("/show-weather")
def show_weather():
     data = db.weather.find({})
     weather = []
     for item in data:
        item['_id'] = str(item['_id'])
        weather.append(item)

     return show_json("Udało się pobrać dane",200,True,weather) 


#/////////////////////////////////////////////////
# Rejestracja
@app.route("/register", methods = ["POST"])
def register():
    username = request.json['username']
    email = request.json["email"]
    password = request.json['password']
    hashed_password = generate_password_hash(password)
    if db.users.find_one({'username':username}):
        return show_json("Użytkownik o podanej nazwie już istnieje", 400, False)
    if db.users.find_one({'email' : email}):
        return show_json('Email został już użyty', 400, False)
    if re.fullmatch(password_regex, password) is None:
        return show_json("Hasło musi zawierać małą, dużą literę, cyfrę i minimum 8 znaków.", 400, False)
    if re.fullmatch(email_regex, email) is None:
        return show_json("Podaj poprawny adres email.", 400, False)
    new_user = {"username" : username,
                         "email" : email,
                         "password" : hashed_password}
    db.users.insert_one(new_user)
    new_user['_id'] = str(new_user['_id'])
    return show_json("Utworzono konto",201 , True, new_user)

# Logowanie
@app.route("/login", methods = ['POST'])
def login():
    password = request.json['password']
    email = request.json['email']

    user_exist = db.users.find_one({'email':email})
    if user_exist is None:
        return show_json("Błędny adres email", 404, False)
    
    password_check = check_password_hash(user_exist['password'], password)
    if password_check == False:
        return show_json("Nie poprawne hasło", 404, False)
    expiration = session_expiration(app)
    session['email'] = email
    session['date'] = (datetime.now() + expiration).strftime("%H:%M:%S")
    return show_json("Poprawnie zalogowano", 200, True, email) 
    

@app.route("/whoami")
def whoami():
    if 'email' in session:  
        user = session['email']
        return show_json("Informacje o użytkowniku", 200, True, user)
    else: 
        return show_json("Odmowa dostępu", 401, False)
@app.route("/logout")
def logout():
    session.pop('email', None)
    return show_json("Wylogowano", 200, True)

@app.route("/dashboard")
def dashboard():
    if "email" in session:
        travels = db.travels.aggregate([{"$project":{"_id":0}}])
        weather = db.weather.aggregate([{"$project":{"_id":0}}])
        user = db.users.find_one({"email":session["email"]})
        user["_id"] = str(user["_id"])

        return show_json("Przyznano dostęp",200,True, {
            "travels": list(travels),
            "weather":list(weather),
            "user":user
        })
    else:
        return show_json("Odmowa dostępu",401,False)

 
#/////////////////////////////////////////////////

