from flask import Blueprint,  render_template, request,redirect,url_for,jsonify
from flask_login import current_user
from . import sql
from .function import get_scheduled_events
from Modules.forms import UserField
from .function import login_required_custom, login_required_admin
from dateutil.parser import parse
from datetime import timedelta

pages = Blueprint("pages", __name__,template_folder='/app/templates', static_folder='/app/static')

# the methods that the request can accept
@pages.route('/', methods=['GET','POST'])
@login_required_custom
def home_page():
    relays=sql.Relays.get_all()
    return render_template('Switch.html',relays=relays)
 
@pages.route('/schedule', methods=['GET'])
@login_required_custom
def schedule():
    modified_list= get_scheduled_events()
    events_from_user=sql.Schedules.get_user_schedules(current_user)
    
    if events_from_user is None:
        events_from_user=[]
    
    if current_user.is_user_role():
        max_hours=29
        for event in events_from_user:
            time=(event.end_time-event.start_time).total_seconds() / 60
            max_hours=max_hours-time
            
    elif current_user.is_admin_role():
        max_hours=999
        
    return render_template('schedule.html',all_events=modified_list,current_user=current_user,hours=max_hours)

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
    if request.method == 'POST':  #this block is only entered when the form is submitted
        rely=sql.Relays.get(request.json['id'])
        if rely and rely.is_wait_time_satisfied():
            rely.state = request.json['value']
            sql.Relays.modify(rely)
            sql.LogRelays.new(current_user.email,rely.id,rely.state)
            relays = {"Error":"0","relay":str(request.json['id'])}
        else:
            relays = {"Error":"1","relay":str(request.json['id'])}
    if request.method == 'GET':
        relays=sql.Relays.get_all()

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


@pages.route('/create_event', methods=['POST'])
@login_required_custom
def create_event():
    new_event=False
    
    if not(request.json['title'].is_token_expired()) and request.json['title'].is_current_user_or_admin():
        if(sql.Users.get(request.json['title'])):
            new_event=True
            sql.Schedules.new(request.json['title'], parse(request.json['start']) + timedelta(hours=2),parse(request.json['end']) + timedelta(hours=2),request.json['groupId'])
            sql.LogSchedules.new(current_user.email,request.json['groupId'], 'Create schdule', parse(request.json['start']) + timedelta(hours=2),parse(request.json['end']) + timedelta(hours=2))
    return jsonify({"Created":new_event})

@pages.route('/update_event', methods=['POST'])
@login_required_custom
def update_event():
    modified_event=False
    
    if not(request.json['title'].is_token_expired()) and request.json['title'].is_current_user_or_admin():
        if(sql.Users.get(request.json['title'])):
            schedule = sql.Schedules.get(request.json['groupId'])
            schedule.start_time = parse(request.json['start'])
            schedule.end_time = parse(request.json['end'])
            modified_event = sql.Schedules.modify(schedule)
            sql.LogSchedules.new(current_user.email,schedule.groupId,'Update event',schedule.start_time,schedule.end_time)
    return jsonify({"Updated":modified_event})