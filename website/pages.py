from flask import Blueprint,  render_template, request,jsonify
from flask_login import current_user
from . import sql
from .function import get_scheduled_events,create_event_schedule,update_event_schedule,delete_event_schedule
from Modules.forms import UserField
from .function import login_required_custom, login_required_admin,time_is_valid,conditions_to_update_or_create_event
from dateutil.parser import parse
from datetime import timedelta

pages = Blueprint("pages", __name__,template_folder='/app/templates', static_folder='/app/static')

# the methods that the request can accept
@pages.route('/', methods=['GET','POST'])
@login_required_custom
def home_page():
    relays=sql.Relays.get_all()
    return render_template('Switch.html',relays=relays)
 

@pages.route('/user', methods=['POST','GET'])
@login_required_custom
def user():
    email = None
    form = UserField()
    #Validate form
    if form.validate_on_submit():
        email = form.email.data
        form.email.data = ''
    return render_template('userList.html', email=email,form=form)

@pages.route('/json', methods=['POST'])
@login_required_custom
def json():
    rely=sql.Relays.get(request.json['id'])
    if rely and rely.is_wait_time_satisfied():
        rely.state = request.json['value']
        sql.Relays.modify(rely)
        sql.LogRelays.new(current_user.email,rely.id,rely.state)
        relays = {"Error":"0","relay":str(request.json['id'])}
    else:
        relays = {"Error":"1","relay":str(request.json['id'])}

    return relays

@pages.route('/history', methods=['POST','GET'])
@login_required_custom
def history():
    return render_template('History.html')

@pages.route('/configuration', methods=['POST','GET'])
@login_required_custom
def configuration():
    return render_template('Configuration.html', userEmail=current_user.email)

@pages.route('/database', methods=['POST','GET'])
@login_required_admin
def database():
    relays=sql.Relays.get_all()
    roles=sql.Roles.get_all()
    users=sql.Users.get_all()
    return render_template('databse.html',our_roles=roles,our_relays=relays,our_users=users)

@pages.route('/logs', methods=['POST','GET'])
@login_required_admin
def logs():
    userlogs=sql.LogUsers.get_all()
    relaylogs=sql.LogRelays.get_all()
    schedulelogs=sql.LogSchedules.get_all()
    signuprequestlogs=sql.LogSignUpRequest.get_all()
    return render_template('Logs.html',our_userlogs=userlogs,our_schedulelog=schedulelogs,our_relays=relaylogs,our_signuprequestlogs=signuprequestlogs)

@pages.route('/schedule', methods=['GET'])
@login_required_custom
def schedule():
    modified_list= get_scheduled_events()
    hours=sql.Schedules.get_time_user(current_user)
    userEventCount=len(sql.Schedules.get_future_user_schedules(current_user))
    
    return render_template('schedule.html',all_events=modified_list,current_user=current_user,hours=hours,userEventCount=userEventCount)

@pages.route('/create_event', methods=['POST'])
@login_required_custom
def create_event():
    new_event=False
    
    if conditions_to_update_or_create_event(request):
        new_event=create_event_schedule(request)
            
    return jsonify({"Created":new_event})

@pages.route('/update_event', methods=['POST'])
@login_required_custom
def update_event():
    modified_event=False
    
    if conditions_to_update_or_create_event(request):
        modified_event=update_event_schedule(request)
    
    return jsonify({"Updated":modified_event})

@pages.route('/delete_event', methods=['POST'])
@login_required_custom
def delete_event():
    delete_event=False
    
    if current_user.user_event_validation(request.json['title']) and time_is_valid(parse(request.json['start']),parse(request.json['end'])):
        delete_event=delete_event_schedule(request)
    
    return jsonify({"Deleted":delete_event})