# database Makes easier the interaction between sql and python, its a ORM (object relation)
from flask_login import UserMixin
from datetime import datetime,timedelta
from flask_sqlalchemy import SQLAlchemy
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.pool import QueuePool
from flask_login import login_user,logout_user,current_user
from flask import session
from sqlalchemy.ext.declarative import declarative_base # allows to make a class that maps to a table

# initialize the base class ootb ORM
Base = declarative_base()

# initialize the database
db = SQLAlchemy()

# Between two requests the time to wait to change the relay
TIMETOWAIT=10

#import to password hashing
from werkzeug.security import generate_password_hash,check_password_hash

class BaseModel(db.Model, Base):
    __abstract__ = True
    db = None
    
    @classmethod
    def get_all(cls):
        session = cls.db.Session()
        objects = session.query(cls).all()
        session.close()
        return objects
    
    @classmethod
    def new(cls, object):
        print("Creating new object ",object)
        session = cls.db.Session()
        session.add(object)
        session.commit()
        session.close()
        return True
    
    @classmethod
    def new(cls,*args):
        print("Creating new class ",*args)
        session = cls.db.Session()
        session.add(cls(*args))
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
    
class Users(UserMixin,BaseModel):
    __tablename__ = 'users'
    _email = db.Column('email',db.String(100), primary_key=True)
    _date_added = db.Column('date_added',db.DateTime, default=datetime.now)
    last_login = db.Column('last_login',db.DateTime, default=datetime.now)
    _password_hash= db.Column('password_hash',db.String(257),nullable=False)
    _role_id = db.Column('role_id',db.Integer, db.ForeignKey('roles.id'),nullable=False,default=2)
    color = db.Column('color',db.String(20))
    _is_session_active = db.Column('is_session_active',db.Boolean,nullable=False,default=True)
    _is_active= db.Column('is_active',db.Boolean,nullable=False,default=True)
    
    
    def __init__(self,email,password):
        self.email=email
        self.password_hash=password
        self.date_modified=datetime.now()
        self.last_login=datetime.now()
        self.color=str(random.randint(0, 176))+','+str(random.randint(0, 176))+','+str(random.randint(0, 176))
        
    # Setters and getters
    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        self._email = email
        
    @property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = generate_password_hash(password, method='scrypt')

    @property
    def role_id(self):
        return self._role_id

    @role_id.setter
    def role_id(self,role_id):
        self._role_id = role_id

    @property
    def is_session_active(self):
        return self._is_session_active

    @is_session_active.setter
    def is_session_active(self,is_token):
        self._is_session_active = is_token

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self,is_user_active):
        self._is_active = is_user_active
        
    def get_id(self):
           return self.email

    def checkPass(self,password):
        return check_password_hash(self.password_hash,password)
        
    def update_last_login(self):
        self.last_login=datetime.now()
       
    def is_admin_role(self):
        return self.role_id==1
    
    def is_user_role(self):
        return self.role_id==2
    
    @classmethod
    def login(cls,user):
        user.is_session_active = True
        user.update_last_login()
        cls.modify(user)
        login_user(user)
    
    @classmethod
    def logout(cls,user):
        user.update_last_login()
        cls.modify(user)
        user.session_hash = False
        logout_user()
            
    # Get user from db //not initialized in sql server
    @classmethod
    def get(cls,email):
        session = cls.db.Session()
        user = session.query(cls).filter_by(_email=str(email)).first()
        session.close()
        return user

class Roles( BaseModel):
    __tablename__ = 'roles'
    _id = db.Column('id', db.Integer, primary_key=True, unique=True)
    _name = db.Column('name', db.String(100), nullable=False, unique=True)
    date_added = db.Column('date_added',db.DateTime, default=datetime.now)

    def __init__(self, id, name):
        self._id = id
        self._name = name

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        
class Relays(BaseModel):
    __tablename__ = 'relays'
    _id = db.Column('id', db.Integer, primary_key=True, nullable=False)
    _state = db.Column('state', db.Integer, nullable=False)
    _date_modified = db.Column('date_modified', db.DateTime, nullable=False)
    _name = db.Column('name', db.String(100), nullable=False, unique=True)

    def __init__(self,id,name):
        self.id=id
        self.name=name
        self.state=0
        
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
                cls.new(relay)
        return True

class Schedules(BaseModel):
    __tablename__ = 'schedule'
    user_email = db.Column('user_email',db.String(100), db.ForeignKey('users.email'),primary_key=True)
    start_time = db.Column('start_time',db.DateTime,primary_key=True)
    end_time = db.Column('end_time',db.DateTime)
        
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

    @classmethod
    def get_user_schedules(cls,user):
        session = cls.db.Session()
        schedules = session.query(Schedules).filter_by(user_email=user.email).all()
        session.close()
        return schedules
    
    @classmethod
    def get_future_user_schedules(cls,user):
        session = cls.db.Session()
        schedules = session.query(Schedules).filter_by(user_email=user.email).filter(Schedules.start_time>datetime.now()).all()
        session.close()
        return schedules
    
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

    
    