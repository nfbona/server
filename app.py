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


import random
# ----------REQUEST COOKIE -----------
"""
Response.set_cookie('key','value')

request.cookies.get('key')

"""

# DB
## Initiating models
from Modules.models import db,Users,Relay,Roles,Schedule
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
    
    # Session
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_USE_SIGNER'] = True
    
    # mysql+pymysql://username:password@host/dbname
    app.config['SQLALCHEMY_DATABASE_URI'] = str(sql_uri)
    # push configuration
    app.app_context().push()

    ## TEST CONNECTION TO SQL_Alchemy
    db.init_app(app)
    migrate = Migrate(app, db,directory=MIGRATION_DIR)
    return app
 
def user_login_out_of_time(current_user):
    if current_user.is_authenticated:
        if current_user.old_session():
            print('User: ',current_user.old_session(),', TimeNOw-LastLogin: ',datetime.now() - current_user.last_login , ', Timedelta24h: ', timedelta(hours=24))
            return True
        else:
            print('correct user')
            return False
    else:
        print('Not initiated')
        return False
        
        
# get all existing events
def get_events(current_user):
    modified_list=[]
    start_date = datetime.now() - timedelta(weeks=1)
    all_schedule=Schedule.query.filter(Schedule.end_time >=start_date).all()
        
    for event in all_schedule:
        if current_user.email==event.email:
            modified_list.append({"title":event.email,"groupId":event.email,"start":event.start_time,"end":event.end_time,"editable":"true","color":current_user.color})
        else:
            try:
                user=Users.query.filter_by(email=event.email).first()
                modified_list.append({"title":event.email,"groupId":event.email,"start":event.start_time,"end":event.end_time,"editable":"false","color":user.color})
            except:
                db.session.delete(event)
    return modified_list   

# pw
app=create_app(db)

login_manager = LoginManager()
login_manager.login_view = 'login'

login_manager.init_app(app)

 
@login_manager.user_loader
def load_user(user_email):
    try:
        name_update=Users.query.get(user_email)
        current_user=session['user']
        return name_update
    except:
        print(user_email)
        redirect(url_for('logout'))

 
# Global variable
TIMETOWAIT=10


# the methods that the request can accept

@app.route('/', methods=['POST', 'GET'])
def login(): 
    
    # Check lifetime user

    form = LogInForm()
    if(current_user.is_authenticated):
        
        return redirect(url_for('switch'))

    #Validate form
    return render_template('Login.html',form=form)


@app.route('/login', methods=['POST'])
def loginPOST(): 
   
    email = None
    password = None
    form = LogInForm()
    CheckUser=None
    
    if form.validate_on_submit():
        users = Users.query.filter_by(email=form.email.data).first()
        if users:
            if users.checkPass(form.password_hash.data):
                login_user(users)
                session['user']=form.email.data
                current_user.update_last_login()
                db.session.commit()
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
    logout_user()
    session.pop('user',None)
    current_user=None
    return redirect('/')

@app.route('/user/signup', methods=['POST','GET'])
def signup():
    if(user_login_out_of_time(current_user)):
        return redirect(url_for('logout'))
    form = PasswordForm()
    our_users=Users.query.all()
 
    return render_template('SignUp.html', form=form, our_users=our_users)
 
@app.route('/user/signupPOST', methods=['POST'])
def signupPOST():
    form = PasswordForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        print("users: ",user)
        if(user is None):
            user = Users(email=form.email.data, password_hash= form.password_hash.data)
            print("user inserted: ",user)   
            db.session.add(user)
            db.session.commit()
            flash('User')
        else:
            flash('User already registered.')
        user=None
        form.email.data = None
        form.password_hash.data=None

        our_users= Users.query.order_by(Users.date_added + timedelta(hours=2))
        print("user inserted: ",our_users)  
    return redirect(url_for('signup'))
 
 
@app.route('/user/update/<string:email>', methods=['GET'])
def update(email):
    if(user_login_out_of_time(current_user)):
        return redirect(url_for('logout'))
    if(current_user.email == email or current_user.role_id ==1):
        form = PasswordForm()
        name_update= Users.query.filter_by(email=email).first()
        #Validate form
        return render_template('UpdateUser.html', form=form,our_user=name_update)
    flash("Not valid operation.")
    return redirect(url_for('signup'))
    
@app.route('/user/updatePOST/<string:email>', methods=['POST'])
def updatePOST(email):
    if(user_login_out_of_time(current_user)):
        return redirect(url_for('logout'))
    email=str(email)
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
            flash("Usuari modificat satisfactoriament.")
        
    return redirect(url_for('update',email=email))

@app.route('/user/delete/<string:email>', methods=['POST'])
@login_required
def delete(email):
    if(user_login_out_of_time(current_user)):
        return redirect(url_for('logout'))
    email=str(email)
    if(current_user.email == email or current_user.role_id ==1):
        name_update=Users.query.get_or_404(email)
        #Validate form
        flash('Usuari deletejat satisfactoriament.')
        try:			
            if(current_user.email == name_update.email):
                print('SAME EMAIL AS USER')
                db.session.delete(name_update)
                db.session.commit()
                return redirect(url_for('logout'))
            else:
                print('OTHER EMAIL')
                db.session.delete(name_update)
                db.session.commit()
                return redirect(url_for('signup'))
        except:
            print('EXCEPT')
            return redirect(url_for('signup'))
    flash("Operació no valida.")
    return redirect(url_for('signup'))
#Switch
@app.route('/switch', methods=['GET'])
@login_required
def switch():
    if(user_login_out_of_time(current_user)):
        return redirect(url_for('logout'))
    relays=Relay.query.order_by(Relay.id).all()
    return render_template('Switch.html',relays=relays)

#Switch
@app.route('/schedule', methods=['GET'])
@login_required
def schedule():
    if(user_login_out_of_time(current_user)):
        return redirect(url_for('logout'))
    modified_list= get_events(current_user)
    events_from_user=Schedule.query.filter_by(user_email=current_user.email)
    max_hours=3
    
    if current_user.role_id==2:
        for event in events_from_user:

            time=(event.end_time-event.start_time).total_seconds() / 3600

            max_hours=max_hours-time
    else:
        max_hours=999
    return render_template('schedule.html',all_events=modified_list,current_user=current_user,hours=max_hours)

@app.route('/schedule/all_events', methods=['PULL'])
@login_required
def all_events():
    if(user_login_out_of_time(current_user)):
        return redirect(url_for('logout'))
    modified_list= get_events()
    print(modified_list)
    return(modified_list)


#userlist
@app.route('/user', methods=['POST','GET'])
@login_required
def user():
    if(user_login_out_of_time(current_user)):
        return redirect(url_for('logout'))
    email = None
    form = UserField()
    #Validate form
    if form.validate_on_submit():
        email = form.email.data
        form.email.data = ''
    return render_template('userList.html', email=email,form=form)

@app.route('/json', methods=['POST'])
@login_required
def json():
    if(user_login_out_of_time(current_user)):
        return redirect(url_for('logout'))
    if request.method == 'POST':  #this block is only entered when the form is submitted
        rely=Relay.query.filter_by(id=request.json['id']).first()
        print('IF: ',(datetime.now()-timedelta(seconds=TIMETOWAIT)) > rely.date_modified,', Delta time: ',rely.date_modified, ', Datetime to pass:',datetime.now()-timedelta(seconds=TIMETOWAIT))
        if (datetime.now()-timedelta(seconds=TIMETOWAIT)) > rely.date_modified:
            # changing the state of the relay
            
            rely.state=request.json['value']
            db.session.commit()
        else:
            return {"Error":"1","relay":str(request.json['id'])}

        return {"Error":"0","relay":str(request.json['id'])}
    if request.method == 'GET':
        relays=Relay.copy()
        for relay in relays:
            time= str(int(TIMETOWAIT-datetime.now()-relay['date_modified'].total_seconds()))
        return relays

    return Relay

# ------------------  NEW TEMPLATES TO BE MADE ------------------ #

@app.route('/history', methods=['POST','GET'])
@login_required
def history():
    if(user_login_out_of_time(current_user)):
        return redirect(url_for('logout'))
    return render_template('History.html')

@app.route('/configuration', methods=['POST','GET'])
@login_required
def configuration():
    if(user_login_out_of_time(current_user)):
        return redirect(url_for('logout'))
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
    
    

    
