# database Makes easier the interaction between sql and python, its a ORM (object relation)
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

from app import db
#import to password hashing
from werkzeug.security import generate_password_hash,check_password_hash



#Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(100), nullable=False,unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash= db.Column(db.String(128),nullable=False)
    # One user can have many roles, referencing an inexisting column in ROles that will be created automatically.
    # key_roles=db.relationship('Roles',backref='user',lazy='dynamic')
    
    # One to one relationship must have a role
    roles_id = db.Column(db.Integer, db.ForeignKey('roles.id'),nullable=False,default=2)
    
    # create a string
    def __repr__(self):
            return '<Email %r>' % self.email
    @property
    def password(self):
        raise AttributeError('Password is not a readable option')
    
    @password.setter
    def password(self,password):
        self._password_hash = generate_password_hash(password)
    
    def checkPass(self,password):
       return check_password_hash(self._password_hash,password)

class Roles(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True,unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False,unique=True)

class Relay(db.Model, UserMixin):
    id= db.Column(db.Integer,primary_key=True,nullable=False,unique=True)
    state= db.Column(db.Boolean,nullable=False)
    date_modified= db.Column(db.DateTime,nullable=False)
    name=db.Column(db.String(100), nullable=False,unique=True)
    
    @property
    def Relay(self):
        raise AttributeError('Error')
    
    @Relay.setter
    def state(self,state,name):
        self.state=state
        self.date_modified=datetime.now()
        self.name=name

