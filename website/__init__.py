# Import necessary modules
from flask import Flask, redirect, url_for
from dotenv import dotenv_values
from datetime import timedelta,datetime
from flask_login import LoginManager, current_user
from Modules.models import db, SQLClass,CustomAnonymousUser
import RPi.GPIO as GPIO

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


pins = [2, 3, 4, 17, 27, 22, 10, 9]  # Add more pin numbers as needed

# Set up SQLAlchemy engine and session
sql = SQLClass(dotenv_values('.env')['MYSQL_ROOT_PASSWORD'])

# Function to get environment variables
def get_environ():
    env_variables = dotenv_values('.env')
    CRSF_KEY = env_variables['CRSF_KEY']
    return  CRSF_KEY

def GPIO_state(relay_id, state):
    # Assuming relay_id is numeric and directly corresponds to an index in pins
    pin_number = pins[int(relay_id) - 1]
    GPIO.setup(pin_number, GPIO.OUT)
    if state==True:
        GPIO.output(pin_number, GPIO.HIGH)
    elif state==False:
        GPIO.output(pin_number, GPIO.LOW)
    relay=sql.Relays.get(relay_id)
    relay._is_active=state
    sql.Relays.modify(relay)

def last_state_gpios():
    for each in sql.Relays.get_all():
        print("GPIO: ", each._id, " State: ", each._is_active)
        GPIO_state(each._id, each._is_active)
    


# Function to initialize Flask app
def init_flask(crsf_key):
    app = Flask(__name__, template_folder='/app/templates', static_folder='/app/static')
    app.config['SECRET_KEY'] = str(crsf_key)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_SQLALCHEMY'] = sql.Session
    return app

# Function to initialize SQLAlchemy
def init_sql(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = sql.uri
    app.config['SESSION_USE_SIGNER'] = True  # Enable session signing
    db.init_app(app)
    return app

# Function to initialize blueprints
def init_blueprints(app):
    from .pages import pages
    from .auth import auth
    app.register_blueprint(pages)
    app.register_blueprint(auth, url_prefix="/auth")
    return app

# Function to initialize login manager
def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.anonymous_user = CustomAnonymousUser
    login_manager.login_view = 'pages.home_page'
    login_manager.init_app(app)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_PROTECTION'] = 'strong'
    
    return app, login_manager

def create_admin_user_if_not_exists():
    user = sql.Users.get('admin@admin.admin')
    roles = sql.Roles.get_all()
    relays = sql.Relays.get_all()
    print("Roles: ",roles)
    if not relays:
        sql.Relays.new(1,'Relay1')
        sql.Relays.new(2,'Relay2')
        sql.Relays.new(3,'Relay3')
        sql.Relays.new(4,'Relay4')
        sql.Relays.new(5,'Relay5')
        sql.Relays.new(6,'Relay6')
        sql.Relays.new(7,'Relay7')
        sql.Relays.new(8,'Relay8')
    
    if not roles:
        sql.Roles.new(1,'admin')
        sql.Users.new(2,'user')
    
    if not user:
        # User doesn't exist, so create a new user
        new_user = sql.Users.new('admin@admin.admin','admin',1)
        return new_user
    else:
        # User already exists
        return user
    
# Function to create Flask app
def create_app():
    crsf_key = get_environ()  
    app = init_flask(crsf_key)  
    app, login_manager = init_login_manager(app)  
    app = init_sql(app) 
    app = init_blueprints(app) 
    app.app_context().push()  
    
    # Load user
    @login_manager.user_loader
    def user_loader(user_email):
        return sql.Users.get(user_email)

    # Handle unauthorized access
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return redirect(url_for('pages.home_page'))

    # Before the first request, create all tables
    @app.before_first_request
    def create_tables_sql():
        print("Creating tables...")
        db.create_all()
        create_admin_user_if_not_exists()
        last_state_gpios()
        
    @login_manager.needs_refresh_handler
    def refresh_login():
        if current_user.is_authenticated:
            print("Refreshing login...")
            print("Session token: ",current_user.session)

    # your code here

    return app
