# Import necessary modules
from flask import Flask, redirect, url_for,session
from dotenv import dotenv_values
from datetime import timedelta
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from flask_login import LoginManager, logout_user, current_user
from flask_session import Session
from Modules.models import db, Users
from sqlalchemy.orm import sessionmaker, scoped_session

# Set up SQLAlchemy engine and session
sql_uri = f"mysql+pymysql://{dotenv_values('.env')['DATABASE_USERNAME']}:{dotenv_values('.env')['DATABASE_PASSWORD']}@mysql/mysql"
engine = create_engine(sql_uri, poolclass=QueuePool)
Session = sessionmaker(bind=engine)
session_db = scoped_session(Session)

# Function to get environment variables
def get_environ():
    env_variables = dotenv_values('.env')
    SQL_URI, CRSF_KEY = f"mysql+pymysql://{env_variables['DATABASE_USERNAME']}:{env_variables['DATABASE_PASSWORD']}@mysql/mysql", env_variables['CRSF_KEY']
    return SQL_URI, CRSF_KEY

# Function to initialize Flask app
def init_flask(crsf_key):
    app = Flask(__name__, template_folder='/app/templates', static_folder='/app/static')
    app.config['SECRET_KEY'] = str(crsf_key)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_SQLALCHEMY'] = db
    return app

# Function to initialize SQLAlchemy
def init_sql(app, sql_uri):
    app.config['SQLALCHEMY_DATABASE_URI'] = str(sql_uri)
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
def init_login(app):
    login_manager = LoginManager()
    login_manager.login_view = 'pages.home_page'
    login_manager.init_app(app)
    return app, login_manager

# Function to create Flask app
def create_app():
    sql_uri, crsf_key = get_environ()  # Load environment variables
    app = init_flask(crsf_key)  # Initialize Flask app
    app, login_manager = init_login(app)  # Initialize login manager
    app = init_sql(app, sql_uri)  # Initialize SQLAlchemy
    app = init_blueprints(app)  # Initialize blueprints
    app.app_context().push()  # Push application context

    # Before each request, check if the user is authenticated and perform logout if necessary            
    @app.before_request
    def before_request():
        '''
        if current_user.is_authenticated:
            if 'value' in session:
                if session['value'] != current_user['email']:
                    logout_procedure()
        '''
    # Load user
    @login_manager.user_loader
    def load_user(user_email):
        return session_db.query(Users).get(user_email)

    # Handle unauthorized access
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        print("NOT unauthorized_handler")
        return redirect(url_for('pages.home_page'))

    # Before the first request, create all tables
    @app.before_first_request
    def create_tables():
        print("Creating tables...")
        db.create_all()

    # After each request, remove the session
    @app.teardown_appcontext
    def remove_session(*args, **kwargs):
        session_db.remove()

    return app



# Function to perform logout procedure
def logout_procedure():
    if session.get('user'):
        session.pop('user')
        logout_user()
        session.clear()
        print("USER POPED FROM SESSION")