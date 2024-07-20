'''
models
defines sql alchemy data models
also contains the definition for the room class used to keep track of socket.io rooms

Just a sidenote, using SQLAlchemy is a pain. If you want to go above and beyond, 
do this whole project in Node.js + Express and use Prisma instead, 
Prisma docs also looks so much better in comparison

or use SQLite, if you're not into fancy ORMs (but be mindful of Injection attacks :) )
'''

from sqlalchemy import String, Integer, ForeignKey, Column, Table, DateTime, Boolean
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
    
    username = Column(String, primary_key=True)
    password = Column(String, nullable=False)  
    salt = Column(String, nullable=False) 
    role = Column(String, nullable=False)
    muted = Column(Boolean, nullable=False, default=False)

    sent_requests = relationship("FriendRequest", foreign_keys="[FriendRequest.sender_username]")
    received_requests = relationship("FriendRequest", foreign_keys="[FriendRequest.receiver_username]")

    friends = relationship("User", secondary=friends_table, primaryjoin=username==friends_table.c.user_id, secondaryjoin=username==friends_table.c.friend_id, backref="friend_of")

    group_chats = relationship("GroupChat", secondary="user_group_chat", back_populates="participants")

# model to store friend requests
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
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_username])
    receiver = relationship("User", foreign_keys=[receiver_username])


# model to store articles
class Article(Base):
    __tablename__ = "article"
    article_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    author_username = Column(String, ForeignKey('user.username'), nullable=False)
    author = relationship("User", backref="articles")
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)



# model to store comments on articles
class Comment(Base):
    __tablename__ = "comment"
    comment_id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('article.article_id'), nullable=False)
    user_username = Column(String, ForeignKey('user.username'), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

user_group_chat = Table('user_group_chat', Base.metadata,
    Column('user_username', String, ForeignKey('user.username'), primary_key=True),
    Column('chat_id', Integer, ForeignKey('group_chat.chat_id'), primary_key=True)
)

class GroupChat(Base):
    __tablename__ = "group_chat"
    chat_id = Column(Integer, primary_key=True)
    group_name = Column(String, nullable=False)
    participants = relationship("User", secondary=user_group_chat, back_populates="group_chats")

class GroupChatMessage(Base):
    __tablename__ = 'group_chat_message'
    id = Column(Integer, primary_key=True)
    group_chat_id = Column(Integer, ForeignKey('group_chat.chat_id'), nullable=False)
    sender_username = Column(String, ForeignKey('user.username'), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    sender = relationship("User")
    group_chat = relationship("GroupChat")


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
        
    def create_room(self, sender: str, receiver: str) -> int:
        room_id = self.counter.get()
        self.dict[sender] = room_id
        self.dict[receiver] = room_id
        return room_id
    
    def join_room(self,  sender: str, room_id: int) -> int:
        self.dict[sender] = room_id

    def leave_room(self, user):
        if user not in self.dict.keys():
            return
        del self.dict[user]

    def get_room_id(self, user: str):
        if user not in self.dict.keys():
            return None
        return self.dict[user]
    
    def get_other_user(self, username: str, room_id: int) -> str:
        for user, id_ in self.dict.items():
            if id_ == room_id and user != username:
                return user
        return None