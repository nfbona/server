# database Makes easier the interaction between sql and python, its a ORM (object relation)
from flask_login import UserMixin
from datetime import datetime,timedelta
from flask_sqlalchemy import SQLAlchemy
import random


db = SQLAlchemy()
#import to password hashing
from werkzeug.security import generate_password_hash,check_password_hash

#Model
class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    email = db.Column(db.String(100), primary_key=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash= db.Column(db.String(128),nullable=False)
   # One user can have many roles, referencing an inexisting column in ROles that will be created automatically.
    # key_roles=db.relationship('Roles',backref='user',lazy='dynamic')
    
    # One to one relationship must have a role
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'),nullable=False,default=2)
    color = db.Column(db.String(20))
    
    # create a string
    def __repr__(self):
            return '<Email %r>' % self.email
 
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def checkPass(self,password):
       return check_password_hash(self.password_hash,password)
        
    def __init__(self,email,password_hash):
        self.email=email
        self.password_hash=generate_password_hash(password_hash,"sha256")
        self.date_modified=datetime.now()
        self.last_login=datetime.now()
        color=str(random.randint(0, 176))+','+str(random.randint(0, 176))+','+str(random.randint(0, 176))
        print(color)
        self.color=color
        
    def update_last_login(self):
        self.last_login=datetime.now()
    
    def old_session(self):
        if datetime.now() - self.last_login  > timedelta(hours=24):
            return True
        return False
        
    def get_id(self):
           return (self.email)

class Roles(db.Model, UserMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True,unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False,unique=True)

    def __init__(self,id,name):
        self.id=id
        self.name=name

class Relay(db.Model, UserMixin):
    __tablename__ = 'relays'
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    state = db.Column(db.Integer,nullable=False)
    date_modified = db.Column(db.DateTime,nullable=False)
    name = db.Column(db.String(100), nullable=False,unique=True)
    
    @property
    def Relay(self):
        raise AttributeError('Error')
    
    @Relay.setter
    def status(self,state,name):
        self.state=state
        self.date_modified=datetime.now()
        self.name=name
        
    def __init__(self,id,name):
        self.id=id
        self.name=name
        self.date_modified=datetime.now()
        self.state=0

class Schedule(db.Model, UserMixin):
    __tablename__ = 'schedule'
    user_email = db.Column(db.String(100), db.ForeignKey('users.email'),primary_key=True)
    start_time = db.Column(db.DateTime,primary_key=True)
    end_time = db.Column(db.DateTime)
        
    def __init__(self,email,start_time,end_time):
        self.start_time=start_time
        self.user_email=email
        self.end_time = end_time