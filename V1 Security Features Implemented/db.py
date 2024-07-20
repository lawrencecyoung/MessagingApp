'''
db
database file, containing all the logic to interface with the sql database
'''

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
engine = create_engine("sqlite:///database/main.db", echo=False)

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
def insert_user(username: str, password: str, salt: str):
    with Session(engine) as session:
        user = User(username=username, password=password, salt=salt)
        session.add(user)
        session.commit()

def verify_password(username: str, password: str):
    with Session(engine) as session:
        # Retrieve user record from the database
        user = session.query(User).filter_by(username=username).first()
        if user:
            # Concatenate stored salt with provided password
            salted_password = password + user.salt
            # Hash the salted password
            hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
            # Compare the hashed password with the stored hashed password
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

    
def save_message(sender_username, receiver_username, store_message, encryptedby):
    with Session(engine) as session:
        message = Message(sender_username=sender_username, receiver_username=receiver_username, store_message=store_message, encryptedby=encryptedby)
        session.add(message)
        session.commit()


def retrieve_message_history(sender_username, receiver_username, encryptedby):
    with Session(engine) as session:
        message_history = session.query(Message).filter(
            (((Message.sender_username == sender_username) &
            (Message.receiver_username == receiver_username))|((Message.sender_username == receiver_username) &
            (Message.receiver_username == sender_username))) &
            (Message.encryptedby == encryptedby)  # Filter for messages encrypted by the specified user
        ).order_by(Message.timestamp.asc()).all()
        # Convert each Message object to a dictionary representation
        message_dicts = [
            {
                "id": message.id,
                "sender_username": message.sender_username,
                "receiver_username": message.receiver_username,
                "store_message": message.store_message,  # Assuming the encrypted message is stored in the content field
                "encryptedby": message.encryptedby,  # Assuming sender_encrypted field stores who encrypted the message
                "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Format timestamp as string
            }
            for message in message_history
        ]
        return message_dicts 