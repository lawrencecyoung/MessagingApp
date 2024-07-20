'''
models
defines sql alchemy data models
also contains the definition for the room class used to keep track of socket.io rooms

Just a sidenote, using SQLAlchemy is a pain. If you want to go above and beyond, 
do this whole project in Node.js + Express and use Prisma instead, 
Prisma docs also looks so much better in comparison

or use SQLite, if you're not into fancy ORMs (but be mindful of Injection attacks :) )
'''

from sqlalchemy import String, Integer, ForeignKey, Column, Table, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Dict, Tuple
from datetime import datetime

# data models
class Base(DeclarativeBase):
    pass

# Define friends table
friends_table = Table('friends', Base.metadata,
    Column('user_id', String, ForeignKey('user.username')),
    Column('friend_id', String, ForeignKey('user.username'))
)    

# model to store user information
class User(Base):
    __tablename__ = "user"
    
    # looks complicated but basically means
    # I want a username column of type string,
    # and I want this column to be my primary key
    # then accessing john.username -> will give me some data of type string
    # in other words we've mapped the username Python object property to an SQL column of type String 

    username = Column(String, primary_key=True)
    password = Column(String, nullable=False)   
    salt = Column(String, nullable=False)

    # Define relationship for sent/received friend requests
    sent_requests = relationship("FriendRequest", foreign_keys="[FriendRequest.sender_username]")
    received_requests = relationship("FriendRequest", foreign_keys="[FriendRequest.receiver_username]")

    # Define relationship for friends
    friends = relationship("User", secondary=friends_table, primaryjoin=username==friends_table.c.user_id, secondaryjoin=username==friends_table.c.friend_id, backref="friend_of")
    

# Data model to store friend requests (sent/received)
class FriendRequest(Base):
    __tablename__ = 'friend_requests'
    id = Column(Integer, primary_key=True)
    sender_username = Column(String, ForeignKey('user.username'), nullable=False)
    receiver_username = Column(String, ForeignKey('user.username'), nullable=False)


# Define message model
class Message(Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    sender_username = Column(String, ForeignKey('user.username'), nullable=False)
    receiver_username = Column(String, ForeignKey('user.username'), nullable=False)
    store_message = Column(String, nullable=False)
    encryptedby = Column(String, nullable=False)

    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Define relationship for sender and receiver
    sender = relationship("User", foreign_keys=[sender_username])
    receiver = relationship("User", foreign_keys=[receiver_username])
    



# stateful counter used to generate the room id
class Counter():
    def __init__(self):
        self.counter = 0
    
    def get(self):
        self.counter += 1
        return self.counter

# Room class, used to keep track of which username is in which room
class Room():
    def __init__(self):
        self.counter = Counter()
        self.dict: Dict[str, int] = {}
        self.public_keys: Dict[int, Tuple[str, str]] = {}
        
    def create_room(self, sender: str, receiver: str, creator_name: str, creatorPublicKey: str, creatorDHpublickey: str) -> int:
        room_id = self.counter.get()
        self.dict[sender] = room_id
        self.dict[receiver] = room_id
        self.public_keys[room_id] = (creator_name, creatorPublicKey, creatorDHpublickey)
        return room_id
    
    def join_room(self,  sender: str, room_id: int) -> int:
        self.dict[sender] = room_id

    def leave_room(self, user):
        if user not in self.dict.keys():
            return
        del self.dict[user]

    # gets the room id from a user
    def get_room_id(self, user: str):
        if user not in self.dict.keys():
            return None
        return self.dict[user]
    
    def get_other_user(self, username: str, room_id: int) -> str:
        for user, id_ in self.dict.items():
            if id_ == room_id and user != username:
                return user
        return None
    
    def get_public_key_and_creator(self, room_id: int) -> Tuple[str, str, str]:
        creator_name, public_key, DHpublicKey = self.public_keys.get(room_id, (None, None))
        return creator_name, public_key, DHpublicKey
    