# database Makes easier the interaction between sql and python, its a ORM (object relation)
from flask_login import UserMixin
from datetime import datetime,timedelta
from flask_sqlalchemy import SQLAlchemy
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.pool import QueuePool
from flask_login import login_user,logout_user
from flask import session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

db = SQLAlchemy()

# Between two requests the time to wait to change the relay
TIMETOWAIT=10

#import to password hashing
from werkzeug.security import generate_password_hash,check_password_hash

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    email = db.Column(db.String(100), primary_key=True)
    date_added = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime, default=datetime.now)
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
        self.password_hash = generate_password_hash(password, method='scrypt')
    
    def checkPass(self,password):
       return check_password_hash(self.password_hash,password)
        
    def __init__(self,email,password_hash):
        self.email=email
        self.password_hash=generate_password_hash(password_hash,"sha256")
        self.date_modified=datetime.now()
        self.last_login=datetime.now()
        self.color=str(random.randint(0, 176))+','+str(random.randint(0, 176))+','+str(random.randint(0, 176))
        
    def update_last_login(self):
        self.last_login=datetime.now()
        
    def get_id(self):
           return (self.email)
       
    def is_admin_role(self):
        return self.role_id==1
    
    def is_user_role(self):
        return self.role_id==2
    
    def login(self):
        session['user'] = self.email
        login_user(self)
        self.update_last_login()
        
    def logout(self):
        session.pop('user', None)
        logout_user()
        self.update_last_login()
        
    def is_same_user(self,email):
        return self.email==email
        
class Roles(db.Model, UserMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True,unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False,unique=True)

    def __init__(self,id,name):
        self.id=id
        self.name=name

class Relays(db.Model, UserMixin):
    __tablename__ = 'relays'
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    state = db.Column(db.Integer,nullable=False)
    date_modified = db.Column(db.DateTime,nullable=False)
    name = db.Column(db.String(100), nullable=False,unique=True)
    
    @property
    def Relays(self):
        raise AttributeError('Error')
    
    @Relays.setter
    def state(self,state):
        self.state=state
        self.date_modified=datetime.now()

    @Relays.setter
    def name(self,name):
        self.name=name
    
    def __init__(self,id,name):
        self.id=id
        self.name=name
        self.date_modified=datetime.now()
        self.state=0
        
    def wait_time_satisfied(self):
        return (datetime.now()-timedelta(seconds=TIMETOWAIT)) > self.date_modified

class Schedules(db.Model, UserMixin):
    __tablename__ = 'schedule'
    user_email = db.Column(db.String(100), db.ForeignKey('users.email'),primary_key=True)
    start_time = db.Column(db.DateTime,primary_key=True)
    end_time = db.Column(db.DateTime)
        
    def __init__(self,email,start_time,end_time):
        self.start_time=start_time
        self.user_email=email
        self.end_time = end_time
        
        

class SQLClass:
    def __init__(self, db_password):
        self.uri=f"mysql+pymysql://root:{db_password}@mysql/mysql"
        self.engine = create_engine(self.uri,poolclass=QueuePool)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    @property
    def Users(self):
        return Users

    def get_user(self,email):
        session = self.Session()
        user = session.query(Users).filter_by(email=email).first()
        session.close()
        return user

    def get_roles(self):
        session = self.Session()
        roles = session.query(Roles).order_by(Roles.date_added)
        session.close()
        return roles
    
    def get_relays(self):
        session = self.Session()
        relays = session.query(Relays).order_by(Relays.id)
        session.close()
        return relays
    
    def get_relay(self,id): 
        session = self.Session()
        relay = session.query(Relays).filter_by(id=id).first()
        session.close()
        return relay

    def get_schedule(self):
        session = self.Session()
        schedule = session.query(Schedules).order_by(Schedules.start_time).all()
        session.close()
        return schedule
    
    def get_schedule_user(self,email):
        session = self.Session()
        schedule = session.query(Schedules).filter_by(user_email=email).order_by(Schedules.start_time)
        session.close()
        return schedule

    def add_object(self,object):
        session = self.Session()
        session.add(object)
        session.commit()
        session.close()
        return True
    
    def modify_object(self,object):
        session = self.Session()
        session.merge(object)
        session.commit()
        session.close()
        return True
    
    def delete_object(self,object):
        session = self.Session()
        session.delete(object)
        session.commit()
        session.close()
        return True
    
    def remove(self):
        self.Session.remove()
        return True
    
    def init_relays(self):
        relays=self.get_relays()
        if not relays:
            for i in range(1,9):
                relay=Relay(i,f"Relay {i}")
                self.add_object(relay)
        return True
    
    
class BaseModel(Base):
    __abstract__ = True
    
    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()