from flask import Flask, json, request, jsonify

from database import db
from show_json import show_json
from bson import ObjectId
from flask_cors import CORS


app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/create-travel", methods = ["GET","POST"])
def create_travel():
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
