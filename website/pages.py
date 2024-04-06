from flask import Blueprint,  render_template, request,redirect,url_for
from flask_login import current_user,login_required
from . import sql
from .auth import get_events
from Modules.forms import UserField
from .function import login_required_custom


pages = Blueprint("pages", __name__,template_folder='/app/templates', static_folder='/app/static')


# the methods that the request can accept
@pages.route('/', methods=['GET','POST'])
@login_required_custom
def home_page():
    relays=sql.Relays.get_all()
    return render_template('Switch.html',relays=relays)


#Schedule all events
@pages.route('/schedule', methods=['GET'])
@login_required
@login_required_custom
def schedule():
    modified_list= get_events()
    events_from_user=sql.Users.get_schedules(current_user)
    if current_user.is_user_role():
        for event in events_from_user:
            time=(event.end_time-event.start_time).total_seconds() / 3600
            max_hours=max_hours-time
            
    elif user.is_admin_role():
        max_hours=999
        
    return render_template('schedule.html',all_events=modified_list,current_user=current_user.email,hours=max_hours)


#Schedule all events in json
@pages.route('/schedule/all_events', methods=['PULL'])
@login_required_custom
def all_events():
    modified_list= get_events()
    return(modified_list)

#Schedule all events in json
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

# 
@pages.route('/json', methods=['POST'])
@login_required_custom
def json():
    if request.method == 'POST':  #this block is only entered when the form is submitted
        rely=sql.Relays.get(request.json['id'])
        if rely.is_wait_time_satisfied():
            # changing the state of the relay
            rely.state = request.json['value']
            sql.Relays.modify(rely)
            
        else:
            return {"Error":"1","relay":str(request.json['id'])}

        return {"Error":"0","relay":str(request.json['id'])}
    if request.method == 'GET':
        relays=sql.Relays.get_all()
        return relays

    return relays

# ------------------  NEW TEMPLATES TO BE MADE ------------------ #

@pages.route('/history', methods=['POST','GET'])
@login_required_custom
def history():
    return render_template('History.html')

@pages.route('/configuration', methods=['POST','GET'])
@login_required_custom
def configuration():
    return render_template('Configuration.html', userEmail=current_user.email)


# database Creation 
@pages.route('/database', methods=['POST','GET'])
def database():
    relays=sql.Relays.get_all()
    roles=sql.Roles.get_all()
    users=sql.Users.get_all()
    return render_template('databse.html',our_roles=roles,our_relays=relays,our_users=users)
