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
    app_name='MYAPPNAME'
    # Load environment variables
    load_dotenv()
    sql_uri=os.environ.get('SQL_URI')
    crtf_key=os.environ.get('CRTF_KEY')
    MIGRATION_DIR = os.path.join('Modules', 'migrations')

    print(sql_uri)
    # initiating Flask, bootstrap, CRTF key
    app = Flask(__name__)
    app.config['SECRET_KEY'] = str(crtf_key)


    # mysql+pymysql://username:password@host/dbname
    app.config['SQLALCHEMY_DATABASE_URI'] = str(sql_uri)
    # push configuration
    app.app_context().push()

    ## TEST CONNECTION TO SQL_Alchemy
    db.init_app(app)
    migrate = Migrate(app, db,directory=MIGRATION_DIR)
    return app
 
 
app=create_app(db)

# pw
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

 
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id)) 
 
# Global variable
TIMETOWAIT=10

# the methods that the request can accept

@app.route('/', methods=['POST', 'GET'])
def login(): 
    
    if(current_user.is_authenticated):
        return redirect(url_for('switch'))
    
    email = None
    password = None
    form = LogInForm()
    CheckUser=None
    
    #Validate form
    if form.validate_on_submit():
        users = Users.query.filter_by(email=form.email.data).first()
        if users:
            print("hash: " + form.password_hash.data)
            if users.checkPass(form.password_hash.data):
                session['user']=generate_password_hash(str(users.id))
                login_user(users)
                
                flash('Correct username and password')
                return redirect(url_for('switch'))
        # clear data from form
            else:
                flash('Invalid username or password')
        else:
            flash('Invalid username or password')
    return render_template('Login.html', email=email,form=form, password=password,CheckUser=CheckUser)

@app.route('/logout',methods=['POST','GET'])
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/user/signup', methods=['POST','GET'])
def signup():
    email = None
    password = None
    form = PasswordForm()
    our_users=Users.query.all()
    #Validate form
    if form.validate_on_submit():
        print("Email: ",form.email.data)
        print("Password: ",form.password_hash.data)
        user = Users.query.filter_by(email=form.email.data).first()
        print("users: ",user)
        if(user is None):
            user = Users(email=form.email.data, password_hash= generate_password_hash(form.password_hash.data,"sha256"))
            print("user inserted: ",user)   
            db.session.add(user)
            db.session.commit()
        email = form.email.data
        print("user inserted: ",email)   
        password = form.password_hash.data
        print("user inserted: ",password)   
        form.email.data = ''
        form.password_hash.data=''
        our_users= Users.query.order_by(Users.date_added + timedelta(hours=2))
        print("user inserted: ",our_users)   
    return render_template('SignUp.html', email=email, form=form, password=password, our_users=our_users)
 
@app.route('/user/update/<int:id>', methods=['POST','GET'])
def update(id):
    if(current_user.id == id or current_user.roles_id ==1):
        email = None
        password = None
        form = PasswordForm()
        name_update=Users.query.get_or_404(id)
        #Validate form
        if form.validate_on_submit():
            name_update.password_hash=generate_password_hash(form.password_hash.data,"sha256")
            db.session.commit()
            form.email.data = ''
            form.password_hash.data = ''
            flash("User modified successfully!")
        return render_template('UpdateUser.html', email=email, form=form, password=password,our_user=name_update)
    flash("Not valid :S")
    return redirect(url_for('signup'))
    
@app.route('/user/delete/<int:id>', methods=['POST','GET'])
@login_required
def delete(id):
    email = None
    password = None
    form = PasswordForm()
    name_update=Users.query.get_or_404(id)
    #Validate form
    try:			
        db.session.delete(name_update)
        db.session.commit()
        flash("User deleted successfully!")
        name_update.email = request.form['email']
        name_update.password = request.form['password']
        db.session.commit()
        form.email.data = ''
        form.password_hash.data=''
        password=name_update.password_hash
        our_users= Users.query.order_by(Users.date_added + timedelta(hours=2))
        return render_template('UserList.html', email=email, form=form, password=password, our_users=our_users)
    except:
        our_users= Users.query.order_by(Users.date_added + timedelta(hours=2))
        return render_template('UserList.html', email=email, form=form, password=password,our_users=our_users)
     
#Switch
@app.route('/switch', methods=['POST','GET'])
@login_required
def switch():
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
  return render_template('History.html')

@app.route('/configuration', methods=['POST','GET'])
@login_required
def configuration():
  return render_template('Configuration.html')

@app.errorhandler(404)
def error400(e):
    return render_template('error/404.html')  

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('error/404.html')

@app.errorhandler(500)
def error500(e):
    return render_template('error/500.html')  

# database Creation 
@app.route('/database', methods=['POST','GET'])
def database():

    print(db.get_tables_for_bind())

    relays=Relay.query.all()
    print(relays)
    try:
        if(len(relays)==0):
            print("No relays")
            db.session.add(Relay(id=1,name="relay1"))
            db.session.add(Relay(id=2,name="relay2"))
            db.session.add(Relay(id=3,name="relay3"))
            db.session.add(Relay(id=4,name="relay4"))
            db.session.add(Relay(id=5,name="relay5"))
            db.session.add(Relay(id=6,name="relay6"))
            db.session.add(Relay(id=7,name="relay7"))
            db.session.add(Relay(id=8,name="relay8"))
            db.session.add(Relay(id=9,name="relay9"))
            db.session.add(Relay(id=10,name="relay10"))
            db.session.add(Relay(id=11,name="relay11"))
            db.session.add(Relay(id=12,name="relay12"))
            db.session.commit()
        
        roles=Roles.query.all()
        print(roles)
        if(len(roles)==0):
            db.session.add(Roles(id=1,name='Admin'))
            db.session.add(Roles(id=2,name='User'))
            db.session.commit()
    except:    
        db.create_all()
    users=Users.query.all()
    return render_template('databse.html',our_roles=roles,our_relays=relays,our_users=users)


##---------------------------------------------------------------


if __name__=="__main__":
    db.create_all()
    
    

    
