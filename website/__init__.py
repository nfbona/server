# Import necessary modules
from flask import Flask, redirect, url_for
from dotenv import dotenv_values
from datetime import timedelta

from flask_login import LoginManager, current_user
from Modules.models import db, SQLClass

# Set up SQLAlchemy engine and session
sql = SQLClass(dotenv_values('.env')['MYSQL_ROOT_PASSWORD'])

# Function to get environment variables
def get_environ():
    env_variables = dotenv_values('.env')
    CRSF_KEY = env_variables['CRSF_KEY']
    return  CRSF_KEY

# Function to initialize Flask app
def init_flask(crsf_key):
    app = Flask(__name__, template_folder='/app/templates', static_folder='/app/static')
    app.config['SECRET_KEY'] = str(crsf_key)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_SQLALCHEMY'] = db
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
    login_manager.login_view = 'pages.home_page'
    login_manager.init_app(app)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_PROTECTION'] = 'strong'
    
    return app, login_manager

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
        sql.Relays.init()
        
    @login_manager.needs_refresh_handler
    def refresh_login():
        if current_user.is_authenticated:
            print("Refreshing login...")
            print("Session token: ",current_user.session)

    # your code here

    return app
