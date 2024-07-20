'''
db
database file, containing all the logic to interface with the sql database
'''

from os import renames
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import *

from pathlib import Path

import hashlib
import secrets
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main99.db", echo=False)

# initializes the database
Base.metadata.create_all(engine)

def clear_all_data():
    with Session(engine) as session:
        # Delete all rows from each table
        session.query(User).delete()
        session.query(FriendRequest).delete()
        session.query(Message).delete()
        session.query(friends_table).delete()
        session.commit()

# inserts a user to the database
def insert_user(username: str, password: str, salt: str, role: str):
    with Session(engine) as session:
        user = User(username=username, password=password, salt=salt, role=role)
        session.add(user)
        session.commit()

def verify_password(username: str, password: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        if user:
            salted_password = password + user.salt
            hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
            if hashed_password == user.password:
                return True
    return False

# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)
    
# retrieves friends given username
def get_friends(username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        if user:
            return user.friends
        else:
            return []

# send friend request to a user
def send_friend_request(sender_username: str, receiver_username: str):
    with Session(engine) as session:
        # Check if receiver exists
        receiver = session.query(User).filter_by(username=receiver_username).first()
        friends = get_friends(sender_username)

        for friend in friends:
            if receiver_username == friend.username:
                return "Already friends" 

        if not receiver:
            return "Receiver user does not exist"
        # Check if the friend request already exists
        existing_request = session.query(FriendRequest).filter_by(sender_username=sender_username, receiver_username=receiver_username).first()
        if existing_request:
            return "Friend request already sent or received"
        # Create a new friend request
        friend_request = FriendRequest(sender_username=sender_username, receiver_username=receiver_username)
        session.add(friend_request)
        session.commit()
        return "Friend request sent successfully"

# get received friend requests
def get_received_requests(username: str):
    with Session(engine) as session:
        received_requests = session.query(FriendRequest).filter_by(receiver_username=username).all()
        return received_requests

# get sent friend requests
def get_sent_requests(username: str):
    with Session(engine) as session:
        sent_requests = session.query(FriendRequest).filter_by(sender_username=username).all()
        return sent_requests

# approve or reject friend request
def request_decision(sender_username: str, receiver_username: str, decision: bool):
    with Session(engine) as session:
        # Find the friend request
        friend_request = session.query(FriendRequest).filter_by(sender_username=sender_username, receiver_username=receiver_username).first()
        if friend_request:
            if decision == True:
                # Define the friend relationship
                sender = session.query(User).filter_by(username=sender_username).first()
                receiver = session.query(User).filter_by(username=receiver_username).first()
                sender.friends.append(receiver)
                receiver.friends.append(sender)
                # Delete friend request row
                session.delete(friend_request) 
                session.commit()
                return "Friend request approved"
            elif decision == False:
                session.delete(friend_request)
                session.commit()
                return "Friend request rejected"
        else:
            return "Friend request not found"     

def remove_friend(username: str, friendname: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        friend = session.query(User).filter_by(username=friendname).first()
        if user and friend:
            if friend in user.friends and user in friend.friends:
                user.friends.remove(friend)
                friend.friends.remove(user)
                session.commit()
                return f"{friendname} has been removed from your friends list."
            else:
                return f"{friendname} is not in your friends list."
        else:
            return "User or friend not found."

def save_message(sender_username, receiver_username, content):
    with Session(engine) as session:
        message = Message(sender_username=sender_username, receiver_username=receiver_username, content=content)
        session.add(message)
        session.commit()

def retrieve_message_history(sender_username, receiver_username):
    with Session(engine) as session:
        message_history = session.query(Message).filter(
            (((Message.sender_username == sender_username) &
            (Message.receiver_username == receiver_username))|((Message.sender_username == receiver_username) &
            (Message.receiver_username == sender_username)))
        ).order_by(Message.timestamp.asc()).all()

        message_dicts = [
            {
                "id": message.id,
                "sender_username": message.sender_username,
                "receiver_username": message.receiver_username,
                "content": message.content,
                "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for message in message_history
        ]
        return message_dicts 

def create_article(title, content, author_username):
    with Session(engine) as session:
        author = session.query(User).filter_by(username=author_username).first()
        if author.muted == True:
            return "You have been muted"
        elif author:
            article = Article(title=title, content=content, author=author)
            session.add(article)
            session.commit()
            return article
        else:
            return None

def create_comment(article_id, user_username, content):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=user_username).first()
        article = session.query(Article).filter_by(article_id=article_id).first()

        if user.muted == True:
            return "You have been muted"
        elif user and article:
            comment = Comment(article_id=article_id, user_username=user_username, content=content)
            session.add(comment)
            session.commit()
            return comment
        else:
            return None
        
def get_article(title, author_username):
    with Session(engine) as session:
        article = session.query(Article).join(User).filter(Article.title == title, User.username == author_username).first()
        return article
    
def get_article_by_id(article_id):
    with Session(engine) as session:
        article = session.query(Article).filter_by(article_id=article_id).first()
        return article

def get_comments_for_article(article_id):
    with Session(engine) as session:
        comments = session.query(Comment).filter_by(article_id=article_id).all()
        return comments

def delete_article(article_id):
    with Session(engine) as session:
        session.query(Comment).filter_by(article_id=article_id).delete()
        article = session.query(Article).filter_by(article_id=article_id).first()
        if article:
            session.delete(article)
            session.commit()
            return True
        else:
            return False

def modify_article(article_id, new_title, new_content):
    with Session(engine) as session:
        article = session.query(Article).filter_by(article_id=article_id).first()
        if article:
            article.title = new_title
            article.content = new_content
            session.commit()
            return True
        else:
            return False

def delete_comment(article_id, comment_id):
    with Session(engine) as session:
        comment = session.query(Comment).filter_by(comment_id=comment_id, article_id=article_id).first()
        if comment:
            session.delete(comment)
            session.commit()
            return True
        else:
            return False
        
def update_student_mute_status(username, mute_status):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        if user:
            user.muted = mute_status
            session.commit()
            return True
        else:
            return False

def get_all_articles():
    with Session(engine) as session:
        articles = session.query(Article).all()
        return articles
    
def get_all_students():
    with Session(engine) as session:
        students = session.query(User).filter_by(role="Student").all()
        return students

def get_all_users():
    with Session(engine) as session:
        users = session.query(User).all()
        return users
    
def delete_user(username):
    with Session(engine) as session:
        session.query(FriendRequest).filter(
            (FriendRequest.sender_username == username) |
            (FriendRequest.receiver_username == username)
        ).delete(synchronize_session=False)
        
        session.query(Message).filter(
            (Message.sender_username == username) |
            (Message.receiver_username == username)
        ).delete(synchronize_session=False)

        session.query(Article).filter(Article.author_username == username).delete(synchronize_session=False)
        session.query(Comment).filter(Comment.user_username == username).delete(synchronize_session=False)
        session.query(User).filter(User.username == username).delete(synchronize_session=False)
        
        session.commit()

def create_group_chat(groupchat_name, members):
    with Session(engine) as session:
        new_group_chat = GroupChat(group_name=groupchat_name)
        
        all_members = []
        for member in members:
            user = get_user(member)
            all_members.append(user)
        
        new_group_chat.participants.extend(all_members)
        session.add(new_group_chat)
        session.commit()

def get_groupchat(groupchat_name):
    with Session(engine) as session:
        queried_group_chat = session.query(GroupChat).filter_by(group_name=groupchat_name).first()
        return queried_group_chat

def get_groupchat_by_chatid(chat_id):
    with Session(engine) as session:
        queried_group_chat = session.query(GroupChat).filter_by(chat_id=chat_id).first()
        return queried_group_chat

def get_users_in_group_chat(chat_id):
    with Session(engine) as session:
        member_names = []
        queried_group_chat = session.query(GroupChat).filter_by(chat_id=chat_id).first()
        participants = queried_group_chat.participants
        if queried_group_chat:
            for member in participants:
                member_names.append([member.username, member.role])
            return member_names
        else:
            return []

def save_groupchat_message(group_chat_id, sender, content):
    with Session(engine) as session:
        message = GroupChatMessage(group_chat_id=group_chat_id, sender_username=sender, content=content)
        session.add(message)
        session.commit()

def get_groupchat_messages(group_chat_id):
    with Session(engine) as session:
        messages = session.query(GroupChatMessage).filter_by(group_chat_id=group_chat_id).all()
        return messages

def get_user_groupchats(username):
    with Session(engine) as session:
        user_groupchats = session.query(GroupChat).join(GroupChat.participants).filter_by(username=username).all()
        return user_groupchats

def add_user_to_groupchat(username, group_chat_id):
    with Session(engine) as session:
        user = get_user(username)
        queried_group_chat = session.query(GroupChat).filter_by(chat_id=group_chat_id).first()
        queried_group_chat.participants.append(user)
        session.commit()
      
def leave_groupchat(username, group_chat_id):
    with Session(engine) as session:
        user = get_user(username)
        queried_group_chat = session.query(GroupChat).filter_by(chat_id=group_chat_id).first()
        participants = (queried_group_chat.participants)
        for member in participants:
            if member.username == user.username:
                participants.remove(member)
                session.commit()

def save_groupchat_message(group_chat_id, sender_username, content):
    with Session(engine) as session:
        message = GroupChatMessage(group_chat_id=group_chat_id, sender_username=sender_username, content=content)
        session.add(message)
        session.commit()

def get_groupchat_messages(group_chat_id):
    with Session(engine) as session:
        messages = session.query(GroupChatMessage).filter_by(group_chat_id=group_chat_id).order_by(GroupChatMessage.timestamp.asc()).all()
        return messages
