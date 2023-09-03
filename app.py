from flask import Flask, render_template, request,flash,redirect,url_for,session,_app_ctx_stack

import os
from dotenv import load_dotenv
# datetime
from datetime import datetime, timedelta

# SQL alchemy
## Custom forms for login and password and more... 
from Modules.forms import PasswordForm,LogInForm,UserField
## Multithreat
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# User Login
from flask_login import LoginManager,login_user,login_required,logout_user


# DB
## Initiating models
from Modules.models import db,Users,Relay,Roles,Schedule,Sessions
from sqlalchemy.orm import sessionmaker



def create_app(db):
    # Load environment variables
    load_dotenv()
    sql_uri=os.environ.get('SQL_URI')
    crsf_key=os.environ.get('CRSF_KEY')
    
    
    engine = create_engine(sql_uri, poolclass=QueuePool)
    Session = sessionmaker(bind=engine)
    session_db=Session()
    
    print(sql_uri)
    # initiating Flask, bootstrap, CRTF key
    app = Flask(__name__)
    app.config['SECRET_KEY'] = str(crsf_key) 

    # Session
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_SQLALCHEMY'] = db
    app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'
    
    # mysql+pymysql://username:password@host/dbname
    app.config['SQLALCHEMY_DATABASE_URI'] = str(sql_uri)
    app.config['SESSION_USE_SIGNER'] = True  # Enable session signing
    # push configuration
    app.app_context().push()

    ## TEST CONNECTION TO SQL_Alchemy
    db.init_app(app)
    
    # SHA
    
    return app,session_db
 
def user_logged():
    if 'user' in session:
        user=session_db.query(Sessions).get(session['user'])
        if(user):
            print(user)
            return user 
        else:
            logout_user()
            session.pop('user',None)
            return None
    else :
        return None
 

def user_login_out_of_time():
    user=user_logged()
    print('user_login_out_of_time: ',user)
    if user and user.isExpired():
        print('User: ',user.isExpired())
        logout_user()
        session.pop('user',None)
        return True
    else:
        print('Not initiated')
        return False
        
        
# get all existing events
def get_events():
    
    modified_list=[]
    start_date = datetime.now() - timedelta(weeks=1)
    all_schedule=session_db.query(Schedule).filter(Schedule.end_time >=start_date).all()
        
    for event in all_schedule:
        if session['user']==event.email:
            User=session_db.query(Users).get(session['user'])
            modified_list.append({"title":event.email,"groupId":event.email,"start":event.start_time,"end":event.end_time,"editable":"true","color":User.color})
        else:
            try:
                user=session_db.query(Users).filter_by(email=event.email).first()
                modified_list.append({"title":event.email,"groupId":event.email,"start":event.start_time,"end":event.end_time,"editable":"false","color":user.color})
            except:
                session_db.delete(event)
    return modified_list   

# pw
app,session_db=create_app(db)

login_manager = LoginManager()
login_manager.login_view = 'login'

login_manager.init_app(app)



# Database
 
@login_manager.user_loader
def load_user(user_email):
    try:
        name_update = session_db.query(Sessions).get(user_email)
        
        if name_update and not(name_update.isExpired()):
            session['user'] = name_update.email
            return name_update
        else :
            return redirect(url_for('logout'))
    except:
        print(user_email)
        return redirect(url_for('logout'))

 
# Global variable
TIMETOWAIT=10


# the methods that the request can accept

@app.route('/', methods=['POST', 'GET'])
def login(): 
    
    # Check lifetime user

    form = LogInForm()
    if('user' not in session):
        
        return render_template('Login.html',form=form)
    
    return redirect(url_for('switch'))

    #Validate form


@app.route('/login', methods=['POST'])
def loginPOST(): 
   
    email = None
    password = None
    form = LogInForm()
    CheckUser=None
    
    if form.validate_on_submit():
        users = session_db.query(Users).filter_by(email=form.email.data).first()
        if users and users.checkPass(form.password_hash.data):

            login_user(users)
            session['user'] = users.email
            
            session_db.add(Sessions(users.email))
            session_db.commit()
            return redirect(url_for('switch'))

        else:
            flash('Invalid username or password')
    return redirect(url_for('switch'))


@app.route('/logout',methods=['POST','GET'])
@login_required
def logout():
    
    session_db.delete(session_db.query(Sessions).get(session['user']))
    session_db.commit()
    logout_user()
    session.pop('user',None)
    return redirect('/')

@app.route('/user/signup', methods=['POST','GET'])
def signup():
    if(user_login_out_of_time()):
        return redirect(url_for('login'))
    form = PasswordForm()
    our_users=session_db.query(Users).all()
    print(our_users)
    return render_template('SignUp.html', form=form, our_users=our_users)
 
@app.route('/user/signupPOST', methods=['POST'])
def signupPOST():
    form = PasswordForm()
    if form.validate_on_submit():
        
        user = session_db.query(Users).filter_by(email=form.email.data).first()
        print("users: ",user)
        if(user is None):
            user = Users(email=form.email.data, password_hash= form.password_hash.data)
            print("user inserted: ",user)   
            session_db.add(user)
            session_db.commit()
            flash('User afegit.')
        else:
            flash('User already registered.')
        user=None
        form.email.data = None
        form.password_hash.data=None

        our_users= session_db.query(Users).order_by(Users.date_added + timedelta(hours=2))
        print("user inserted: ",our_users)  
    return redirect(url_for('signup'))
 
 
@app.route('/user/update/<string:email>', methods=['GET'])
def update(email):
    if(user_login_out_of_time()):
        return redirect(url_for('login'))
    if('user' in session and (session['user'] == email or session_db.query(Users).get(session['user']).role_id ==1)):
        form = PasswordForm()
        name_update= session_db.query(Users).get(email).first()
        #Validate form
        return render_template('UpdateUser.html', form=form,our_user=name_update)
    flash("Not valid operation.")
    return redirect(url_for('signup'))
    
@app.route('/user/updatePOST/<string:email>', methods=['POST'])
def updatePOST(email):
    if(user_login_out_of_time()):
        return redirect(url_for('login'))
    email=str(email)
    if('user' in session and (session['user'] == email or session_db.query(Users).get(session['user']).role_id ==1)):
        form = PasswordForm()
        name_update= session_db.query(Users).filter_by(email=email).first()
        #Validate form
        if form.validate_on_submit():
            # if 
            
            name_update.set_password(form.password_hash.data)
            session_db.commit()
            form.email.data = ''
            form.password_hash.data = ''
            flash("Usuari modificat satisfactoriament.")
        
    return redirect(url_for('update',email=email))

@app.route('/user/delete/<string:email>', methods=['POST'])
@login_required
def delete(email):
    if(user_login_out_of_time()):
        return redirect(url_for('login'))
    email=str(email)
    if('user' in session and (session['user'] == email or session_db.query(Users).get(session['user']).role_id ==1)):
        name_update=session_db.query(Users).get_or_404(email)
        #Validate form
        flash('Usuari deletejat satisfactoriament.')
        try:			
            if('user' in session and session['user'] == name_update.email):
                print('SAME EMAIL AS USER')
                
                session_db.delete(name_update)
                session_db.commit()
                return redirect(url_for('logout'))
            else:
                print('OTHER EMAIL')
                
                session_db.delete(name_update)
                session_db.commit()
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
    if(user_login_out_of_time()):
        return redirect(url_for('login'))
    relays=session_db.query(Relay).order_by(Relay.id).all()
    return render_template('Switch.html',relays=relays)

#Switch
@app.route('/schedule', methods=['GET'])
@login_required
def schedule():
    if(user_login_out_of_time()):
        return redirect(url_for('login'))
    modified_list= get_events()
    events_from_user=session_db.query(Schedule).filter_by(user_email=session['user'])
    max_hours=3
    user=session_db.query(Users).get(session['user'])
    
    
    if user.role_id==2:
        for event in events_from_user:

            time=(event.end_time-event.start_time).total_seconds() / 3600

            max_hours=max_hours-time
    else:
        max_hours=999
    return render_template('schedule.html',all_events=modified_list,current_user=user,hours=max_hours)

@app.route('/schedule/all_events', methods=['PULL'])
@login_required
def all_events():
    if(user_login_out_of_time()):
        return redirect(url_for('login'))
    modified_list= get_events()
    print(modified_list)
    return(modified_list)


#userlist
@app.route('/user', methods=['POST','GET'])
@login_required
def user():
    if(user_login_out_of_time()):
        return redirect(url_for('login'))
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
    if(user_login_out_of_time()):
        return redirect(url_for('login'))
    if request.method == 'POST':  #this block is only entered when the form is submitted
        rely=session_db.query(Relay).filter_by(id=request.json['id']).first()
        print('IF: ',(datetime.now()-timedelta(seconds=TIMETOWAIT)) > rely.date_modified,', Delta time: ',rely.date_modified, ', Datetime to pass:',datetime.now()-timedelta(seconds=TIMETOWAIT))
        if (datetime.now()-timedelta(seconds=TIMETOWAIT)) > rely.date_modified:
            # changing the state of the relay
            
            rely.state=request.json['value']
            session_db.commit()
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
    if(user_login_out_of_time()):
        return redirect(url_for('login'))
    return render_template('History.html')

@app.route('/configuration', methods=['POST','GET'])
@login_required
def configuration():
    if(user_login_out_of_time()):
        return redirect(url_for('login'))

    return render_template('Configuration.html', userEmail=session['user'])

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

    relays=session_db.query(Relay).all()
    print(relays)
 
    roles=session_db.query(Roles).all()
     
    users=session_db.query(Users).all()
    return render_template('databse.html',our_roles=roles,our_relays=relays,our_users=users)


##---------------------------------------------------------------


if __name__=="__main__":
    db.create_all()
    
    

    
