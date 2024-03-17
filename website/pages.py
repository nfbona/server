from flask import Blueprint,  render_template, request,redirect,url_for,session
from flask_login import login_required,current_user
from . import session_db
from .auth import get_events
from Modules.models import db,Users,Relay,Roles,Schedule
from Modules.forms import UserField
from datetime import datetime, timedelta


pages = Blueprint("pages", __name__,template_folder='/app/templates', static_folder='/app/static')


# Global variable
TIMETOWAIT=10


# the methods that the request can accept

@pages.route('/', methods=['GET','POST'])
def home_page():
    if current_user.is_authenticated:
        relays=session_db.query(Relay).order_by(Relay.id).all()
        return render_template('Switch.html',relays=relays)
    
    return redirect(url_for('auth.login'))

 
#Schedule all events
@pages.route('/schedule', methods=['GET'])
@login_required
def schedule():
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


#Schedule all events in json
@pages.route('/schedule/all_events', methods=['PULL'])
@login_required
def all_events():
    modified_list= get_events()
    return(modified_list)


#
@pages.route('/user', methods=['POST','GET'])
@login_required
def user():
    email = None
    form = UserField()
    #Validate form
    if form.validate_on_submit():
        email = form.email.data
        form.email.data = ''
    return render_template('userList.html', email=email,form=form)

# 
@pages.route('/json', methods=['POST'])
@login_required
def json():
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

@pages.route('/history', methods=['POST','GET'])
@login_required
def history():
    return render_template('History.html')

@pages.route('/configuration', methods=['POST','GET'])
@login_required
def configuration():
    return render_template('Configuration.html', userEmail=session['user'])


# database Creation 
@pages.route('/database', methods=['POST','GET'])
def database():

    print(db.get_tables_for_bind())

    relays=session_db.query(Relay).all()
    print(relays)
 
    roles=session_db.query(Roles).all()
     
    users=session_db.query(Users).all()
    return render_template('databse.html',our_roles=roles,our_relays=relays,our_users=users)
