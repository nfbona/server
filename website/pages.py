from flask import Blueprint,  render_template, request,jsonify
from flask_login import current_user
from . import sql, GPIO_state
from .function import get_scheduled_events,create_event_schedule,update_event_schedule,delete_event_schedule
from Modules.forms import UserField
from .function import login_required_custom, login_required_admin,time_is_valid_end,conditions_to_update_or_create_event,is_user_valid
from dateutil.parser import parse
from html import escape


pages = Blueprint("pages", __name__,template_folder='/app/templates', static_folder='/app/static')

# the methods that the request can accept
@pages.route('/', methods=['GET','POST'])
@login_required_custom
def home_page():
    relays=sql.Relays.get_all()
    is_user=is_user_valid(current_user.email) or current_user.is_admin_role()
    return render_template('Switch.html',relays=relays,is_users=is_user)
 

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
    
    if current_user.is_admin_role() or is_user_valid(current_user.email):
        relay=escape(request.json['id'])
        relay = sql.Relays.get(relay)
        if relay and relay.is_wait_time_satisfied():
            if relay:
                relay.change_state()
                sql.LogRelays.new(current_user.email,str(escape(request.json['id'])),relay.is_active)
                sql.Relays.modify(relay)
                GPIO_state(int(relay._id),relay._is_active)

            relays = {"Error":"0","relay":str(escape(request.json['id']))}
        else:
            relays = {"Error":"1","relay":str(escape(request.json['id']))}
    else:
        relays = {"Error":"1","relay":str(escape(request.json['id']))}
    
    return relays

@pages.route('/history', methods=['POST','GET'])
@login_required_custom
def history():
    return render_template('History.html')

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
    userEventCount=len(sql.Schedules.get_future_user_schedules(current_user.email))
    
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
    
    if current_user.user_event_validation(escape(request.json['title'])) and time_is_valid_end(parse(escape(request.json['start'])),parse(escape(request.json['end']))):
        delete_event=delete_event_schedule(request)
    
    return jsonify({"Deleted":delete_event})

@pages.route('/rename_relay', methods=['POST'])
@login_required_admin
def rename_relay():
    response = {"Error":"1"}
    new_name = escape(request.json['name'])
    if (current_user.is_admin_role() and len(new_name) > 0):
        relay=escape(request.json['relay_id'])
        relay = sql.Relays.get(relay)
        if relay:
            relay.name = new_name
            sql.Relays.modify(relay)
            response = {"Error":"0"}
    
    return jsonify(response)