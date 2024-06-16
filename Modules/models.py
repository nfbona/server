# database Makes easier the interaction between sql and python, its a ORM (object relation)
from flask_login import UserMixin,AnonymousUserMixin
from datetime import datetime,timedelta
from flask_sqlalchemy import SQLAlchemy
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.pool import QueuePool
from flask_login import login_user,logout_user
from sqlalchemy.ext.declarative import declarative_base# allows to make a class that maps to a table
from sqlalchemy import and_,or_
import pytz
import hashlib
# initialize the base class ootb ORM
Base = declarative_base()

# initialize the database
db = SQLAlchemy()

# Between two requests the time to wait to change the relay
TIMETOWAIT=10
MINUTS_USUARIS=120

   
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
    
    @property
    def SignUpRequest(self):
        return SignUpRequest
    
    @property
    def LogUsers(self):
        return LogUsers
    
    @property
    def LogRelays(self):
        return LogRelays
    
    @property   
    def LogSchedules(self):
        return LogSchedules
    
    @property
    def LogSignUpRequest(self):
        return LogSignUpRequest
    
    def remove(self):
        self.Session.remove()
        return True

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
        session = cls.db.Session()
        session.add(object)
        session.commit()
        session.close()
        return True
    
    @classmethod
    def new(cls,*args):
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

class CustomAnonymousUser(AnonymousUserMixin):
    def is_current_user_or_admin(self,email):
        return False
    
    def is_token_expired(self):
        return  True
    
    def is_authenticated_and_admin(self):
        return False
    
    def user_event_validation(self,user):
        return False
    
# Set up the login manager


class Users(UserMixin,BaseModel):
    __tablename__ = 'users'
    _email = db.Column('email',db.String(100), primary_key=True)
    _date_added = db.Column('date_added',db.DateTime, default=datetime.now(pytz.timezone('Europe/Madrid')))
    last_login = db.Column('last_login',db.DateTime, default=datetime.now(pytz.timezone('Europe/Madrid')))
    _password_hash= db.Column('password_hash',db.String(256),nullable=False)
    _role_id = db.Column('role_id',db.Integer, db.ForeignKey('roles.id'),nullable=False,default=2)
    _color = db.Column('color',db.String(20))
    _is_session_active = db.Column('is_session_active',db.Boolean,nullable=False,default=True)
    _is_active= db.Column('is_active',db.Boolean,nullable=False,default=True)
    
    
    def __init__(self,email,password,admin=2):
        self.is_active=True
        self.email=email
        self.password_hash=password
        self.date_modified=datetime.now(pytz.timezone('Europe/Madrid'))
        self.last_login=datetime.now(pytz.timezone('Europe/Madrid'))
        self.color=str(random.randint(0, 176))+','+str(random.randint(0, 176))+','+str(random.randint(0, 176))
        self.role_id=admin
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
        self._password_hash = hashlib.scrypt(str(password).encode(), salt=str(self.email).encode(), n=16384,r=8,p=1,dklen=64).hex()

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
        
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self,color):
        self._color=color    
        
    # mandatory method for flask login
    def get_id(self):
        if self.is_active:
            return self.email
        return ""

    def checkPass(self, password):
        return hashlib.scrypt(str(password).encode(), salt=str(self.email).encode(), n=16384,r=8,p=1,dklen=64).hex() == self._password_hash
        
    def update_last_login(self):
        self.last_login=datetime.now(pytz.timezone('Europe/Madrid'))
       
    def is_admin_role(self):
        return self.role_id==1
    
    def is_user_role(self):
        return self.role_id==2
    
    def is_current_user_or_admin(self,email):
        return (email == self.email or self.is_admin_role())
    
    def is_token_expired(self):
        return  (self.is_session_active == False)
    
    def is_authenticated_and_admin(self):
        return self.is_admin_role()
    
    def user_event_validation(self,user):
        return not(self.is_token_expired()) and self.is_current_user_or_admin(user)
        
    @classmethod
    def change_role(cls,user,role_id):
        user.role_id=role_id      
        cls.modify(user)
        return user.role_id==role_id
    
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
        user.is_session_active = False
        logout_user()
            
    # Get user from db //not initialized in sql server
    @classmethod
    def get(cls,email):
        session = cls.db.Session()
        user = session.query(cls).filter_by(_is_active=True).filter_by(_email=str(email)).first()
        session.close()
        return user

    @classmethod
    def get_all(cls):
        session = cls.db.Session()
        users = session.query(cls).filter_by(_is_active=True).all()
        session.close()
        return users

class Roles( BaseModel):
    __tablename__ = 'roles'
    _id = db.Column('id', db.Integer, primary_key=True, unique=True)
    _name = db.Column('name', db.String(100), nullable=False, unique=True)
    date_added = db.Column('date_added',db.DateTime, default=datetime.now(pytz.timezone('Europe/Madrid')))

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
        
    @classmethod
    def get(cls,role_id):
        session = cls.db.Session()
        role = session.query(cls).filter_by(_id=role_id).first()
        session.close()
        return role    
    
class Relays(BaseModel):
    __tablename__ = 'relays'
    _id = db.Column('id', db.Integer, primary_key=True, nullable=False)
    _is_active = db.Column('is_active', db.Boolean,nullable=False,default=False)
    _date_modified = db.Column('date_modified', db.DateTime, nullable=False)
    _name = db.Column('_name', db.String(100), nullable=False, unique=True)

    def __init__(self,id,name):
        self.id=id
        self.name=name
        self.is_active=False
        
    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, is_active):
        self._is_active = is_active
        self._date_modified = datetime.now(pytz.timezone('Europe/Madrid'))

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
    # Get the current time
        now = datetime.now()

        # Calculate the time difference in seconds
        time_diff = (now - self._date_modified).total_seconds()

        # Check if the wait time is satisfied
        return time_diff >= TIMETOWAIT
    @classmethod
    def get(cls,id): 
        session = cls.db.Session()
        relay = session.query(cls).filter_by(_id=id).first()
        session.close()
        return relay
    
    def change_state(self):
        self._is_active = not self.is_active
        return self._is_active

class Schedules(BaseModel):
    __tablename__ = 'schedule'
    user_email = db.Column('user_email',db.String(100), db.ForeignKey('users.email'))
    start_time = db.Column('start_time',db.DateTime)
    end_time = db.Column('end_time',db.DateTime)
    id = db.Column('id',db.String(191),primary_key=True)
        
    def __init__(self,email,start_time,end_time,id):
        self.start_time=start_time
        self.user_email=email
        self.end_time =end_time
        self.id =id

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
    def get_future_schedules(cls):
        session = cls.db.Session()
        schedules = session.query(Schedules).filter(Schedules.end_time>datetime.now(pytz.timezone('Europe/Madrid'))).all()
        session.close()
        return schedules
    
    @classmethod
    def get_past_schedules(cls):
        session = cls.db.Session()
        schedules = session.query(Schedules).filter(Schedules.end_time<=datetime.now(pytz.timezone('Europe/Madrid'))).all()
        session.close()
        return schedules   
    
    @classmethod
    def get_future_user_schedules(cls,email):
        session = cls.db.Session()
        schedules = session.query(Schedules).filter_by(user_email==email).filter(Schedules.end_time>datetime.now(pytz.timezone('Europe/Madrid'))).order_by(Schedules.end_time).all()
        session.close()
        return schedules  
    
    @classmethod
    def delete_all_user_future_schedules(cls,user):
        session = cls.db.Session()
        schedules = cls.get_future_user_schedules(user)
        for schedule in schedules:
            cls.delete(schedule)
        session.close()
        return True
    
    
    @classmethod
    def get_all_schedules_minus_user_future(cls,user):
        session = cls.db.Session()
        schedules = session.query(Schedules).filter(
            or_(
                and_(
                    Schedules.user_email == user.email,
                    Schedules.end_time <= datetime.now(pytz.timezone('Europe/Madrid'))
                ),                
                and_(
                    Schedules.user_email != user.email
                )
            )).all()
        session.close()
        return schedules

    @classmethod
    def get(cls,id):
        session = cls.db.Session()
        schedules = session.query(Schedules).filter(Schedules.id == id).first()
        session.close()
        return schedules
    
    @classmethod
    def get_time_user(cls,user):
        events_from_user=cls.get_future_user_schedules(user.email)
        max_minutes=MINUTS_USUARIS
        
        if events_from_user is None:
            events_from_user=[]
    
        if user.is_user_role():
            for event in events_from_user:
                time=(event.end_time-event.start_time).total_seconds() / 60
                max_minutes=max_minutes-time
                
        elif user.is_admin_role():
            max_minutes=9999999999
        
        return max_minutes

    @classmethod
    def get_overlap(cls, start_time, end_time):
        session = cls.db.Session()
        overlap = session.query(Schedules).filter(
            or_(
                and_(
                    Schedules.start_time >= start_time,
                    Schedules.start_time < end_time
                ),                    
                and_(
                    Schedules.end_time > start_time,
                    Schedules.end_time <= end_time
                ),
                and_(
                    Schedules.start_time <= start_time,
                    Schedules.end_time >= end_time
                )
            )           
        ).all()
        session.close()
        return overlap
    
class SignUpRequest(BaseModel):
    __tablename__ = 'signup_request'
    date = db.Column('date',db.DateTime, default=datetime.now)
    user_email = db.Column('user_email',db.String(100))
    id = db.Column('id',db.Integer, primary_key=True)
    password= db.Column('password',db.String(256),nullable=False)
    
    def __init__(self,email,password):
        self.user_email=email
        self.password=password
        
    @classmethod
    def get(cls,email): 
        session = cls.db.Session()
        relay = session.query(cls).filter_by(user_email=email).first()
        session.close()
        return relay
    
    @classmethod
    def get_all(cls):
        session = cls.db.Session()
        SignUpgs = session.query(cls).order_by(cls.date).all()
        session.close()
        return SignUpgs
 
class Log(BaseModel):
    __abstract__ = True
    datetime = db.Column('datetime',db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Europe/Madrid')))
    id = db.Column('id',db.Integer, primary_key=True)
    action = db.Column('action',db.String(100), nullable=False)
    
class LogUsers(Log):
    __tablename__ = 'log_users'
    user_email = db.Column('user_email',db.String(100), db.ForeignKey('users.email'))

    def __init__(self,user_email,action):
        self.user_email=user_email
        self.action=action
        
    @classmethod
    def get_all_user_logs(cls,email):
        session = cls.db.Session()
        logs = session.query(LogUsers).filter_by(user_email=email).all()
        session.close()
        return logs
    
class LogRelays(Log):
    __tablename__ = 'log_relays'
    user_email = db.Column('user_email',db.String(100),  db.ForeignKey('users.email'))
    relay_id = db.Column('relay_id',db.Integer,  db.ForeignKey('relays.id'))
    
    def __init__(self,user_email,relay_id,action):
        self.user_email=user_email
        self.relay_id=relay_id
        self.action=action
          
    @classmethod
    def get_all_user_logs(cls,email):
        session = cls.db.Session()
        logs = session.query(LogRelays).filter_by(user_email=email).all()
        session.close()
        return logs     
          
class LogSchedules(Log):
    __tablename__ = 'log_schedules'
    user_email = db.Column('user_email',db.String(100), db.ForeignKey('users.email'))
    schedule_id = db.Column('schedule_id',db.String(191),  db.ForeignKey('schedule.id'))
    start_time = db.Column('start_time',db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Europe/Madrid')))
    end_time =db.Column('end_time',db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Europe/Madrid')))
    
    def __init__(self,user_email,schedule_id,action,start_time,end_time):
        self.user_email=user_email
        self.schedule_id=schedule_id
        self.action=action
        self.start_time=start_time
        self.end_time=end_time

class LogSignUpRequest(Log):
    __tablename__ = 'log_signup_request'
    user_accepter = db.Column('user_accepter',db.String(100))
    email = db.Column('user_email',db.String(100), nullable=False)
    
    def __init__(self,user_accepter,email,action):
        self.user_accepter=user_accepter
        self.email=email
        self.action=action
        




