'''
socket_routes
file containing all the routes related to socket.io
'''


from flask_socketio import join_room, emit, leave_room
from flask import request


try:
    from __main__ import socketio
except ImportError:
    from app import socketio

from models import *

import db

room = Room()

online_users = set()
# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on('connect')
def connect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")

    online_users.add(username)
    
    if room_id is None or username is None:
        return
    # socket automatically leaves a room on client disconnect
    # so on client connect, the room needs to be rejoined
    join_room(int(room_id))
    
    emit("incoming", (f"{username} has connected", "green"), to=int(room_id))

# event when client disconnects
# quite unreliable use sparingly
@socketio.on('disconnect')
def disconnect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    emit("incoming", (f"{username} has disconnected", "red"), to=int(room_id))

@socketio.on('userdisconnect')
def disconnect(username):
    online_users.remove(username)

# send message event handler
@socketio.on("send")
def send(username, message, stored_message, encryptedby, room_id, HMAC):
    receiver = room.get_other_user(username, room_id)
    if room.get_other_user(username, room_id):
        db.save_message(username, receiver, stored_message, encryptedby)
    emit("receiving", (f"{username}: {message}", HMAC), to=room_id, include_self=True)
    
# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(sender_name, receiver_name, publicKey, DHpublicKey):    
    friends = db.get_friends(sender_name)
    
    are_friends = False
    for friend in friends:
        if friend.username == receiver_name:
            are_friends = True
    if sender_name == receiver_name:
        return "Cannot open room with yourself!"
    
    if are_friends == False:
        return "Not friends!"
    
    is_online = False
    for user in online_users:
        if user == receiver_name:
            is_online = True
    if is_online == False:
        return "User currently not online!"
    
    
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"
    
    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"

    room_id = room.get_room_id(receiver_name)

    message_history = db.retrieve_message_history(sender_name, receiver_name, sender_name)

    # if the user is already inside of a room 
    if room_id is not None:
        room.join_room(sender_name, room_id)
        join_room(room_id)

        # emit to everyone in the room except the sender
        emit("incoming", (f"{sender_name} has joined the room.", "green"), to=room_id, include_self=False)
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"))
        
        # emit public keys to each other
        creator_name, creatorpublicKey, creatorDHpublickey = room.get_public_key_and_creator(room_id)
        emit("publicKeyBroadcast", (creator_name, creatorpublicKey, creatorDHpublickey), room=room_id, include_self=True)
        emit("publicKeyBroadcast", (sender_name, publicKey, DHpublicKey), room=room_id, include_self=False)


        for message in message_history:
            emit("incoming", (f"{message['sender_username']}: {message['store_message']}", "black"), to=room_id, include_self=True)
        return room_id

    # if the user isn't inside of any room, 
    # perhaps this user has recently left a room
    # or is simply a new user looking to chat with someone

    room_id = room.create_room(sender_name, receiver_name, sender_name, publicKey, DHpublicKey)
    # creatorpublicKey = room.get_public_key_and_creator(room_id)
    # print(creatorpublicKey)

    emit("publicKeyBroadcast", (sender_name, publicKey, DHpublicKey), room=room_id, include_self=False)

    join_room(room_id)
    emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"), to=room_id)
    return room_id

# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)
    room.leave_room(username)

@socketio.on("receive")
def receive(sender, receiver, message, encryptedby):
    db.save_message(sender, receiver, message, encryptedby)

@socketio.on('fetch_friends')
def fetch_friends(username):
    friends = db.get_friends(username)
    friend_usernames = [friend.username for friend in friends]
    emit('friends_fetched', {'friend_usernames': friend_usernames})

# Socket event for sending friend requests
@socketio.on('send_friend_request')
def send_friend_request(sender_username, receiver_username):
    result = db.send_friend_request(sender_username, receiver_username)
    emit('friend_request_sent', {'message': result})

@socketio.on('get_sent_friend_requests')
def get_sent_friend_requests(username):
    sent_requests = db.get_sent_requests(username)
    sent_requests_data = [{'id': request.id, 'receiver': request.receiver_username} for request in sent_requests]
    emit('sent_friend_requests', {'sent_requests': sent_requests_data})

@socketio.on('get_received_friend_requests')
def get_received_friend_requests(username):
    received_requests = db.get_received_requests(username)
    received_requests_data = [{'id': request.id, 'sender': request.sender_username} for request in received_requests]
    emit('received_friend_requests', {'received_requests': received_requests_data})

@socketio.on('friend_request_decision')
def handle_friend_request_decision(data):
    sender = data.get('sender')
    receiver = data.get('receiver')
    decision = data.get('decision')
    
    result = db.request_decision(sender, receiver, decision)
    emit('friend_request_decision_result', {'message': result})


