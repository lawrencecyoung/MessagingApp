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

    print(online_users)

    if room_id is None or username is None:
        return
    # socket automatically leaves a room on client disconnect
    # so on client connect, the room needs to be rejoined
    join_room(int(room_id))
    
    # emit("incoming", (f"{username} has connected", "green"), to=int(room_id))

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
def send(username, message, room_id):
    receiver = room.get_other_user(username, room_id)
    if room.get_other_user(username, room_id):
        db.save_message(username, receiver, message)
    emit("incoming", (f"{username}: {message}"), to=room_id)
    
# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(sender_name, receiver_name):
    
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"
    
    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"

    room_id = room.get_room_id(receiver_name)
    print(room_id)
    message_history = db.retrieve_message_history(sender_name, receiver_name)
    for message in message_history:
            emit("incoming", (f"{message['sender_username']}: {message['content']}", "black"), to=request.sid, include_self=True)
    
    if room_id is not None:
        room.join_room(sender_name, room_id)
        join_room(room_id)
        emit("incoming", (f"{sender_name} has joined the room.", "green"), to=room_id, include_self=False)
        
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"))
        return room_id
    else:
        room_id = room.create_room(sender_name, receiver_name)
        join_room(room_id)
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"), to=room_id)
    return room_id

# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)
    room.leave_room(username)

@socketio.on("leave_groupchat")
def leave_groupchat(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=int(room_id)+1000)
    leave_room(int(room_id)+1000)
    room.leave_room(username)

@socketio.on("receive")
def receive(sender, receiver, message, encryptedby):
    db.save_message(sender, receiver, message, encryptedby)

@socketio.on('fetch_friends')
def fetch_friends(username):
    friends = db.get_friends(username)
    
    friend_data = {}
    for friend in friends:
        online_status = 'Online' if friend.username in online_users else 'Offline'
        friend_data[friend.username] = online_status
    emit('friends_fetched', {'friend_data': friend_data})

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

@socketio.on('remove_friend')
def remove_friend(username, friend_username):
    result = db.remove_friend(username, friend_username)
    if result:
        emit('friend_removed', {'message': result})
    else:
        emit('friend_removed', {'message': 'Failed to remove friend.'})

@socketio.on('fetch_articles')
def fetch_articles():
    all_articles = db.get_all_articles()
    articles_data = [{'article_id': article.article_id, 
                      'title': article.title, 
                      'content': article.content,
                      'author_username': article.author_username,
                      'author_role': db.get_user(article.author_username).role,
                      'time_stamp': article.timestamp.strftime("%d/%m/%Y"),
                      } for article in all_articles]
    emit('articles_fetched', {'articles': articles_data})

@socketio.on('create_article')
def create_article(data):
    username = data['username']
    title = data['title']
    content = data['content']
    db.create_article(title, content, username)

@socketio.on('fetch_comments')
def fetch_comments(article_id):
    all_comments = db.get_comments_for_article(article_id)
    comments_data = [{
        'comment_id': comment.comment_id,
        'content': comment.content,
        'author_username': comment.user_username,
        'author_role': db.get_user(comment.user_username).role,
    } for comment in all_comments]
    
    emit('comments_fetched', {'comments': comments_data})

@socketio.on('create_comment')
def create_comment(data):
    article_id = data.get('article_id')
    user_username = data.get('user_username')
    content = data.get('content')
    db.create_comment(article_id, user_username, content)

@socketio.on('delete_article')
def delete_article(article_id):
    db.delete_article(article_id)
    

@socketio.on('modify_article')
def modify_article(data):
    article_id = data.get('article_id')
    title = data.get('title')
    content = data.get('content')

    db.modify_article(article_id, title, content)

@socketio.on('delete_comment')
def delete_comment(article_id, comment_id):
    db.delete_comment(article_id, comment_id)


@socketio.on('fetch_all_students')
def fetch_all_students():
    all_students = db.get_all_students()

    students_data = {}
    for student in all_students:
        online_status = 'Online' if student.username in online_users else 'Offline'
        students_data[student.username] = {
            'mute_status': student.muted,
            'online_status': online_status
        }

    emit('students_fetched', {'students_list': students_data})

@socketio.on('fetch_all_users')
def fetch_all_users():
    all_users = db.get_all_users()
    users_data = {}
    for user in all_users:
        online_status = 'Online' if user.username in online_users else 'Offline'
        users_data[user.username] = {
            'role': user.role,
            'mute_status': user.muted,
            'online_status': online_status
        }
    emit('users_fetched', {'users_list': users_data})

@socketio.on('toggle_mute_status')
def toggle_mute_status(student_username, mute_status):
    db.update_student_mute_status(student_username, mute_status)
    emit('mute_status_updated', {'username': student_username, 'mute_status': mute_status}, broadcast=True)

@socketio.on('delete_user')
def delete_user(username):
    db.delete_user(username)
    print("deleted")

@socketio.on('create_group_chat')
def create_group_chat(data):
    creator = data.get('username')
    groupchat_name = data.get('name')
    members = data.get('members')

    all_members = [creator]
    for i in members:
        all_members.append(i)
    
    db.create_group_chat(groupchat_name, all_members)

@socketio.on('fetch_group_chats')
def fetch_group_chats(username):
    all_groupchats = db.get_user_groupchats(username)
    groupchat_data = [{
        'chat_id': groupchat.chat_id,
        'group_name': groupchat.group_name,
        'participants': db.get_users_in_group_chat(groupchat.chat_id),
    } for groupchat in all_groupchats]

    emit('group_chat_fetched', {'groupchat_list': groupchat_data})

@socketio.on("join_groupchat")
def join_groupchat(sender_name, group_chat_id):
    room.join_room(sender_name, group_chat_id)
    groupchat_name = db.get_groupchat_by_chatid(int(group_chat_id)-1000).group_name
    message_history = db.get_groupchat_messages(int(group_chat_id)-1000)
    for message in message_history:
        emit("incoming", (f"{message.sender_username}: {message.content}", "black"), to=request.sid, include_self=True)

    emit("incoming", (f"{sender_name} has joined the room. Now talking in {groupchat_name}.", "green"), to=group_chat_id)

    return group_chat_id

@socketio.on("send_groupchat")
def send_groupchat(username, message, chat_id):
    group_chat_id = int(chat_id)-1000
    emit("incoming", (f"{username}: {message}"), to=chat_id)
    db.save_groupchat_message(group_chat_id, username, message)

@socketio.on("leave_groupchat")
def leave_groupchat(username, chat_id):
    db.leave_groupchat(username, int(chat_id)) 

@socketio.on("get_users_in_groupchat")
def get_users_in_groupchat(chat_id):
    groupchat = db.get_groupchat_by_chatid(int(chat_id)-1000)
    users = db.get_users_in_group_chat(int(chat_id)-1000)

    for user in users:
        online_status = 'Online' if user[0] in online_users else 'Offline'
        user.append(online_status)
    print(users)
    emit("fetched_users_in_groupchat", users, to=chat_id)

@socketio.on("add_user_to_groupchat")
def add_user_to_groupchat(chat_id, selected_username):
    db.add_user_to_groupchat(selected_username, int(chat_id)-1000)

