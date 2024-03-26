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
from sqlalchemy.ext.declarative import declarative_base # allows to make a class that maps to a table

Base = declarative_base()

db = SQLAlchemy()

# Between two requests the time to wait to change the relay
TIMETOWAIT=10

#import to password hashing
from werkzeug.security import generate_password_hash,check_password_hash

class BaseModel(Base):
    __abstract__ = True
    db = None
    
    @classmethod
    def get_all(cls):
        return db.session.query(cls).all()
    
    @classmethod
    def add(cls,object):
        session = cls.db.Session()
        session.add(object)
        session.commit()
        session.close()
        return True
    
    @classmethod
    def modify(cls,object):
        session = cls.db.Session()
        session.merge(object)
        session.commit()
        session.close()
        return True
    
    @classmethod
    def delete(cls,object):
        session = cls.db.Session()
        session.delete(object)
        session.commit()
        session.close()
        return True
    
    
class Users(db.Model, UserMixin,BaseModel):
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

    
    # Neext functions are used for sql searches
    
    # Get user from db //not initialized in sql server
    @classmethod
    def get(cls,email):
        session = cls.db.Session()
        user = session.query(cls).filter_by(email=email).first()
        session.close()
        return user
    
    @classmethod
    def get_schedules(cls,email):
        session = cls.db.Session()
        schedules = session.query(Schedules).filter_by(user_email=email).all()
        session.close()
        return schedules
    
        
class Roles(db.Model, UserMixin, BaseModel):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True,unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False,unique=True)

    def __init__(self,id,name):
        self.id=id
        self.name=name

class Relays(db.Model, UserMixin, BaseModel):
    __tablename__ = 'relays'
    _id = db.Column('id', db.Integer, primary_key=True, nullable=False)
    _state = db.Column('state', db.Integer, nullable=False)
    _date_modified = db.Column('date_modified', db.DateTime, nullable=False)
    _name = db.Column('name', db.String(100), nullable=False, unique=True)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state
        self._date_modified = datetime.now()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
    
    @property
    def id(self):
        return self._id

    @name.setter
    def id(self, id):
        self._id = id
    
    @property
    def date_modified(self):
        return self._date_modified
    
    def __init__(self,id,name):
        self.id=id
        self.name=name
        self.state=0
        
    def is_wait_time_satisfied(self):
        return (datetime.now()-timedelta(seconds=TIMETOWAIT)) > self.date_modified


    @classmethod
    def get(cls,id): 
        session = cls.db.Session()
        relay = session.query(cls).filter_by(id=id).first()
        session.close()
        return relay

    @classmethod
    def init(cls):
        relays=cls.get_all()
        if not relays:
            for i in range(1,9):
                relay=cls(i,f"Relay {i}")
                cls.add(relay)
        return True



class Schedules(db.Model, UserMixin, BaseModel):
    __tablename__ = 'schedule'
    user_email = db.Column(db.String(100), db.ForeignKey('users.email'),primary_key=True)
    start_time = db.Column(db.DateTime,primary_key=True)
    end_time = db.Column(db.DateTime)
        
    def __init__(self,email,start_time,end_time):
        self.start_time=start_time
        self.user_email=email
        self.end_time = end_time

    @classmethod
    def get_all(cls):
        session = cls.db.Session()
        schedule = session.query(cls).order_by(cls.start_time).all()
        session.close()
        return schedule




class SQLClass:
    def __init__(self, db_password):
        self.uri=f"mysql+pymysql://root:{db_password}@mysql/mysql"
        self.engine = create_engine(self.uri,poolclass=QueuePool)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        BaseModel.db = self

    @property
    def Users(self):
        return Users

    @property
    def Relays(self):
        return Relays

    @property
    def Schedules(self):
        return Schedules

    @property
    def Roles(self):
        return Roles
    
    def remove(self):
        self.Session.remove()
        return True
    

    
    