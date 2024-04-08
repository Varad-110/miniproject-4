from flask import Flask, jsonify, request, Response
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin

import uuid

#Configuring Flask app
app = Flask(__name__)
app.config['secret'] = "secret@123"
MONGO_URI = "mongodb+srv://shreynagda:shrey0308@cluster0.zxdkj5v.mongodb.net/quiz?retryWrites=true&w=majority&appName=Cluster0"
app.config['MONGO_URI'] = MONGO_URI
CORS(app, origins="*")
client = PyMongo(app)
db = client.db
rooms_collection = db.rooms

@app.route("/")
def home(): 
    return jsonify(f"Server running on port 5000")

@app.route("/rooms/get")
def rooms():
    code = request.args.get("code")
    return jsonify(getRoom(code))


@app.route("/rooms/post", methods = ["POST"])
def createRoom():
    data = request.json
    data["questions"] = []
    data["players"] = []
    if not checkRoomCode(data["code"]):
        id = rooms_collection.insert_one(data)
        if id != None:
            return jsonify({"status": 1, "data": {"_id": str(id)}})
        else:
            return jsonify({"status": -1, "data": "Room not created"})
    else:
            return jsonify({"status": -1, "data": "Room code is already in use!"})


@app.route("/rooms/put", methods=["PUT"])
def updateRoom():
    code = request.args.get("code")
    if checkRoomCode(code):
        data = request.json
        id = rooms_collection.find_one_and_update({"code": code}, {"$set": data})
        if id != None:
            return jsonify({"status": 1, "data": "Room update successful!"})
        else:
            return jsonify({"status": -1, "data": "Room update unsuccessful!"})
    else:
        return jsonify({"status": -1, "data": "Invalid Room code"})

@app.route("/rooms/questions/add", methods=["POST"])
def addQuestions():
    code = request.args.get("code")
    if checkRoomCode(code):
        questions = request.json
        id = rooms_collection.find_one_and_update({"code": code}, {"$set": {"questions": questions}})
        if id != None:
            return jsonify({"status": 1, "data": "Questions added successfully!"})
        else:
            return jsonify({"status": -1, "data": "Questions not added!"})
    else:
        return jsonify({"status": -1, "data": "Invalid Room code"})

@app.route("/rooms/players/add", methods=["POST"])
def addPlayer():
    code = request.args.get("code")
    print(code)
    if checkRoomCode(code):
        can_be_added = True
        player = request.json
        player_id = str(uuid.uuid4())
        player["id"] = player_id
        player["score"] = 0
        room = getRoom(code)
        players = room["data"]["players"]
        for i in players:
            if i["name"] == player["name"]:
                can_be_added = False
                break
        if can_be_added:
            players.append(player)
            id = rooms_collection.find_one_and_update({"code": code}, {"$set": {"players": players}})
            if id != None:
                return jsonify({"status": 1, "data": {"id": player_id, "msg": "Player added successfully!"}})
            else:
                return jsonify({"status": -1, "data": "Players not added!"})
        else:
            return jsonify({"status": -1, "data": "Player nickname already in use"})
    else:
        return jsonify({"status": -1, "data": "Invalid Room code"})


@app.route("/rooms/players/delete", methods=["DELETE"])
def deletePlayer():
    code = request.args.get("code")
    name = request.args.get("name")
    if checkRoomCode(code):
        room = getRoom(code)
        players = list(room["data"]["players"])
        for i in players:
            if i["name"] == name:
                # print("Player can be deleted!")
                players.remove(i)
                print(players)
                id = rooms_collection.find_one_and_update({"code": code}, {"$set": {"players": players}})
                if id != None:
                    return jsonify({"status": 1, "data": "Player deleted successfully!"})
                else:
                    return jsonify({"status": -1, "data": "Player couldn't be deleted!"})
    else:
        return jsonify({"status": -1, "data": "Room does not exists"})        
        

@app.route("/rooms/questions/check", methods=["POST"])
def checkAnswer():
    code = request.args.get("code")
    if checkRoomCode(code):
        room = getRoom(code)
        questions = list(room["data"]["questions"])
        players = list(room["data"]["players"])
        number = request.json["number"]
        option = request.json["option"]
        time = request.json["time"]
        player_name = request.json["player_name"]
        for i in questions:
            if i["qno"] == number and i["correct_option"] == option:
                print("Increment score")
                for i in players:
                    if i["name"] == player_name:
                        i["score"] += time
                id = rooms_collection.find_one_and_update({"code": code}, {"$set": {"players": players}})
                return jsonify({"status": 1, "data": "Score updated!"})
            else:
                return jsonify({"status": -1, "data": {"msg": "Wrong Answer!", "correct": i["correct_option"]}})

                
    else:
        return jsonify({"status": -1, "data": "Room doesn't exists"})



@app.route("/rooms/delete")
def deleteRoom():
    code = request.args.get("code")
    if checkRoomCode(code):
        rooms_collection.find_one_and_delete({"code": code})
        return jsonify({"status": 1, "data": "Room {code} deleted successfully!"})
    else:
        return jsonify({"status": -1, "data": "Room {code} does not exist"})

def getRoom(code):
    if checkRoomCode(code):
        data = rooms_collection.find_one({"code": code})
        data["_id"] = str(data["_id"])
        return {"status": 1, "data": data}
    else:
        return {"status": -1, "data": "Room does not exists"}

def checkRoomCode(code):
    if len(list(rooms_collection.find({"code": code}))) > 0: 
        return True
    else:
        return False
