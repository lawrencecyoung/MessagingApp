'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for, session, jsonify
from flask_socketio import SocketIO
import db
import secrets
import os


# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

app.debug = True

# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)

# don't remove this!!
import socket_routes

# index page
@app.route("/")
def index():
    return render_template("index.jinja")

# login page
@app.route("/login")
def login():    
    return render_template("login.jinja")

# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password")

    user =  db.get_user(username)
    if user is None:
        return "Error: User does not exist!"
    validated = db.verify_password(username, password)
    if validated != True:
        return "Error: Password does not match!"
    if validated == True:
        session['username'] = username
        return url_for('home')

# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)
    username = request.json.get("username")
    password = request.json.get("password")
    salt = request.json.get("salt")
    role = request.json.get("role")


    if db.get_user(username) is None:
        db.insert_user(username, password, salt, role)
        session['username'] = username
        return url_for('home')
    return "Error: User already exists!"


# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# home page, where the messaging app is
@app.route("/home")
def home():
    username = session.get('username')
    if username is None:
        abort(404)
    role = db.get_user(username).role
    muted = db.get_user(username).muted
    return render_template("home.jinja", username=username, role=role, muted=muted)

@app.route("/repo")
def repo():
    username = session.get('username')
    if username is None:
        abort(404)
    role = db.get_user(username).role
    muted = db.get_user(username).muted
    return render_template("repo.jinja", username=username, role=role, muted=muted)

@app.route("/friend_requests")
def friend_requests():
    username = session.get('username')
    if username is None:
        abort(404)
    role = db.get_user(username).role
    return render_template("friend_requests.jinja", username=username, role=role)

@app.route("/create_article")
def create_article():
    username = session.get('username')
    if username is None:
        abort(404)
    role = db.get_user(username).role
    return render_template("create_article.jinja", username=username, role=role)

@app.route("/article/<int:article_id>")
def article(article_id):
    username = session.get('username')
    if username is None:
        abort(404)
    role = db.get_user(username).role
    muted = db.get_user(username).muted
    article = db.get_article_by_id(article_id)
    author_role = db.get_user(article.author_username).role
    timestamp = article.timestamp.strftime("%d/%m/%Y")
    if article is None:
        return "Article not found", 404
    return render_template("article.jinja", article=article, username=username, role=role, author_role=author_role, muted = muted, timestamp=timestamp)

@app.route("/modify_article/<int:article_id>")
def modify_article(article_id):
    username = session.get('username')
    if username is None:
        abort(404)
    role = db.get_user(username).role
    article = db.get_article_by_id(article_id)
    if article is None:
        return "Article not found", 404
    return render_template("modify_article.jinja", article=article, username=username, role=role)

@app.route("/private_message/<username>/<friend_username>")
def private_message(username, friend_username):
    username = session.get('username')
    if username is None:
        abort(404)
    role = db.get_user(username).role
    muted = db.get_user(username).muted
    return render_template("private_message.jinja", username=username, friend_username=friend_username, role=role, muted = muted)


@app.route("/create_group_chat")
def create_group_chat():
    username = session.get('username')
    if username is None:
        abort(404)
    role = db.get_user(username).role
    return render_template("create_group_chat.jinja", username=username, role=role)


@app.route("/groupchat_message/<username>/<groupchat_name>")
def groupchat_message(username, groupchat_name):
    username = session.get('username')
    if username is None:
        abort(404)
    role = db.get_user(username).role
    chat_id = db.get_groupchat(groupchat_name).chat_id
    muted = db.get_user(username).muted
    return render_template("groupchat_message.jinja", username=username, role=role, chat_id = chat_id, groupchat_name=groupchat_name, muted = muted)

if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True, host='127.0.0.1', port=5000, ssl_context=('./certs/info2222.test.crt', './certs/info2222.test.key'))