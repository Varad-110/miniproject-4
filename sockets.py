from flask_socketio import SocketIO, send, emit, join_room, leave_room
from app import app

socket = SocketIO(app, cors_allowed_origins='*')

# @socket.on("connect")
# def connect():
#     send({"msg": f"Client connected!"})


# @socket.on("disconnect")
# def disconnect():
#     send({"msg": f"Client disconnected!"})

@socket.on("message")
def handle_message(data):
    print("message", data)
    send(data, broadcast=True)


@socket.on("join")
def on_join(data):
    name = data["name"]
    room = data["room"]
    print("joined", data)
    join_room(room)
    if name == "host":
        send(f"Room {room} created!", to=room, broadcast=True)
    else:
        send(f"{name} joined the room {room}", to=room, broadcast=True)


@socket.on("start")
def start(data):
    room = data["room"]
    print(room)
    send("start", to=room, broadcast=True)