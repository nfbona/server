from flask import Flask, render_template, request,flash,redirect,url_for,session

import os
from dotenv import load_dotenv
# datetime
from datetime import datetime, timedelta

# Custom forms for login and password and more... 
from Modules.forms import PasswordForm,LogInForm,UserField
from werkzeug.security import generate_password_hash

# User Login
from flask_login import LoginManager,login_user,login_required,logout_user,current_user

# ----------REQUEST COOKIE -----------
"""
Response.set_cookie('key','value')

request.cookies.get('key')

"""

# DB
## Initiating models
from Modules.models import db,Users,Relay,Roles
## Create the tables in the sql 
from flask_migrate import Migrate


def create_app(db):
    # Load environment variables
    load_dotenv()
    sql_uri=os.environ.get('SQL_URI')
    crsf_key=os.environ.get('CRSF_KEY')
    MIGRATION_DIR = os.path.join('Modules', 'migrations')

    print(sql_uri)
    # initiating Flask, bootstrap, CRTF key
    app = Flask(__name__)
    app.config['SECRET_KEY'] = str(crsf_key)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)  

    # mysql+pymysql://username:password@host/dbname
    app.config['SQLALCHEMY_DATABASE_URI'] = str(sql_uri)
    # push configuration
    app.app_context().push()

    ## TEST CONNECTION TO SQL_Alchemy
    db.init_app(app)
    migrate = Migrate(app, db,directory=MIGRATION_DIR)
    return app
 
def user_login_out_of_time():
    if current_user.is_authenticated:
        if current_user.old_session():
            return redirect(url_for('logout'))
        else:
            print('Not that old user')
    else:
        print('Not initiated')
        

app=create_app(db)
# pw
login_manager = LoginManager()
login_manager.login_view = 'login'

login_manager.init_app(app)

 
@login_manager.user_loader
def load_user(user_email):
    return Users.query.get(user_email)
 
# Global variable
TIMETOWAIT=10


# the methods that the request can accept

@app.route('/', methods=['POST', 'GET'])
def login(): 
    
    # Check lifetime user
    user_login_out_of_time()
    
    email = None
    password = None
    form = LogInForm()
    CheckUser=None
    if(current_user.is_authenticated):
        return redirect(url_for('switch'))

    #Validate form
    return render_template('Login.html',form=form)


@app.route('/login', methods=['POST'])
def loginPOST(): 
    user_login_out_of_time()
    
    email = None
    password = None
    form = LogInForm()
    CheckUser=None
    
    if form.validate_on_submit():
        users = Users.query.filter_by(email=form.email.data).first()
        if users:
            print("hash: " + form.password_hash.data)
            print("user password: " + users.password_hash)
            print("password correct?: " + str(users.checkPass(form.password_hash.data)))
            if users.checkPass(form.password_hash.data):
                login_user(users)
                
                flash('Correct username and password')
                return redirect(url_for('switch'))
        # clear data from form
            else:
                flash('Invalid username or password')
        else:
            flash('Invalid username or password')
    return redirect(url_for('switch'))


@app.route('/logout',methods=['POST','GET'])
@login_required
def logout():
    user_login_out_of_time()
    logout_user()
    return redirect('/')

@app.route('/user/signup', methods=['POST','GET'])
def signup():
    user_login_out_of_time()
    form = PasswordForm()
    our_users=Users.query.all()  
 
    return render_template('SignUp.html', form=form, our_users=our_users)
 
@app.route('/user/signupPOST', methods=['POST'])
def signupPOST():
    form = PasswordForm()
    print("NOT VALUDATED FORM, ", form.validate_on_submit(),"NOT VALUDATED FORM, ", form.validate_on_submit(),', Errors: ',form.errors)
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        print("users: ",user)
        if(user is None):
            user = Users(email=form.email.data, password_hash= form.password_hash.data)
            print("user inserted: ",user)   
            db.session.add(user)
            db.session.commit()
        else:
            flash('User already registered.')
        user=None
        form.email.data = None
        form.password_hash.data=None

        our_users= Users.query.order_by(Users.date_added + timedelta(hours=2))
        print("user inserted: ",our_users)  
    return redirect(url_for('signup'))
 
 
@app.route('/user/update/<string:email>', methods=['POST','GET'])
def update(email):
    user_login_out_of_time()
    if(current_user.email == email or current_user.role_id ==1):
        form = PasswordForm()
        name_update= Users.query.filter_by(email=email).first()
        #Validate form
        if form.validate_on_submit():
            # if 
            name_update.set_password(form.password_hash.data)
            db.session.commit()
            form.email.data = ''
            form.password_hash.data = ''
            flash("User updated successfully.")
        return render_template('UpdateUser.html', form=form,our_user=name_update)
    flash("Not valid operation.")
    return redirect(url_for('signup'))
    
@app.route('/user/delete/<string:email>', methods=['POST','GET'])
@login_required
def delete(email):
    user_login_out_of_time()
    if(current_user.email == email or current_user.role_id ==1):
        form = PasswordForm()
        name_update=Users.query.get_or_404(email)
        #Validate form
        try:			

            flash("User deleted successfully.")
            name_update.email = request.form['email']
            name_update.password = request.form['password']
            form.email.data = ''
            form.password_hash.data=''
            flash("User deleted successfully: ",current_user.email,", form: ",request.form['email'])
            if(current_user.email == request.form['email']):
                logout_user()
                db.session.delete(name_update)
                db.session.commit()
                return redirect(url_for('login'))
            else:
                db.session.delete(name_update)
                db.session.commit()
        except:
            return redirect(url_for('signup'))
    flash("Not valid operation.")
    return redirect(url_for('signup'))
#Switch
@app.route('/switch', methods=['POST','GET'])
@login_required
def switch():
    user_login_out_of_time()
    return render_template('Switch.html')


# ---------------------------------TETS_---------------
@app.route('/a1', methods=['POST','GET'])
def a1():
    users=session.query(Users).all()
    session.close()
    return json(users)

#userlist
@app.route('/user', methods=['POST','GET'])
@login_required
def user():
    user_login_out_of_time()
    email = None
    form = UserField()
    #Validate form
    if form.validate_on_submit():
        email = form.email.data
        form.email.data = ''
    return render_template('userList.html', email=email,form=form)

@app.route('/json', methods=['POST','GET'])
@login_required
def json():
    user_login_out_of_time()
    if request.method == 'POST':  #this block is only entered when the form is submitted
        rely=Relay.query.filter_by(_id=request.json['id']).first()
        print('IF: ',(datetime.now()-timedelta(seconds=TIMETOWAIT)) > rely._DateTime,', Delta time: ',rely._DateTime, ', Datetime to pass:',datetime.now()-timedelta(seconds=TIMETOWAIT))
        if (datetime.now()-timedelta(seconds=TIMETOWAIT)) > rely._DateTime:
            # changing the state of the relay
            """
            print(rely.state)
            """
            
            rely.state=request.json['value']
            db.session.commit()
        else:
            return {"Error":"1","relay":str(request.json['id'])}

        return {"Error":"0","relay":str(request.json['id'])}
    if request.method == 'GET':
        relays=Relay.copy()
        for relay in relays:
            time= str(int(TIMETOWAIT-datetime.now()-relay['_DateTime'].total_seconds()))
        return relays

    return Relay

# ------------------  NEW TEMPLATES TO BE MADE ------------------ #

@app.route('/history', methods=['POST','GET'])
@login_required
def history():
    user_login_out_of_time()
    return render_template('History.html')

@app.route('/configuration', methods=['POST','GET'])
@login_required
def configuration():
    user_login_out_of_time()
    current_user.email
    return render_template('Configuration.html', userEmail=current_user.email)

@app.errorhandler(404)
def error400(e):
    return render_template('error/404.html')  

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login'))

@app.errorhandler(500)
def error500(e):
    return render_template('error/500.html')  

# database Creation 
@app.route('/database', methods=['POST','GET'])
def database():

    print(db.get_tables_for_bind())

    relays=Relay.query.all()
    print(relays)
 
    roles=Roles.query.all()
     
    users=Users.query.all()
    return render_template('databse.html',our_roles=roles,our_relays=relays,our_users=users)


##---------------------------------------------------------------


if __name__=="__main__":
    db.create_all()
    
    

    
