# database Makes easier the interaction between sql and python, its a ORM (object relation)
from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
#import to password hashing
from werkzeug.security import generate_password_hash,check_password_hash

#Model
class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    email = db.Column(db.String(100),  primary_key=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash= db.Column(db.String(128),nullable=False)
    active=db.Column(db.Integer)
    # One user can have many roles, referencing an inexisting column in ROles that will be created automatically.
    # key_roles=db.relationship('Roles',backref='user',lazy='dynamic')
    
    # One to one relationship must have a role
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'),nullable=False,default=2)
    
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
        
    def __init__(self,email,password_hash):
        self.name=email.encode()
        self.password_hash=generate_password_hash(password_hash.encode(),"sha256")
        self.date_modified=datetime.now()
        self.active=0

class Roles(db.Model, UserMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True,unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False,unique=True)

    def __init__(self,id,name):
        self.id=id
        self.name=name.encode()

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
        self.name=name.encode()
        
    def __init__(self,id,name):
        self.id=id
        self.name=name.encode()
        self.date_modified=datetime.now()
        self.state=0

