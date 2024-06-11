from flask_login import current_user
from flask import redirect, url_for
from functools import wraps
from .__init__ import sql
from dateutil.parser import parse
from datetime import datetime,timedelta
from Modules.forms import validator
from html import escape

# Decorator to check if user is logged in
def login_required_custom(f):
    @wraps(f)
    def login_required(*args, **kwargs):
        if current_user.is_token_expired():
            return redirect(url_for('auth.logout'))
        return (f(*args, **kwargs))
    return login_required

def login_required_admin(f):
    @wraps(f)
    def login_required(*args, **kwargs):
        if not(current_user.is_authenticated_and_admin()):
            return redirect(url_for('pages.home_page'))
        return (f(*args, **kwargs))
    return login_required

def login_required_admin_or_current_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = kwargs.get('email')
        if not(validator.is_email(user)) or not(current_user.is_authenticated and (current_user.is_admin_role() or current_user.email == user)):
            return redirect(url_for('pages.home_page'))
        return f(*args, **kwargs)
    return decorated_function

def create_disabled_event(event):
    return {"title":event.user_email,"groupId":event.id,"start":event.start_time,"end":event.end_time,"editable":"false","color":sql.Users.get(event.user_email).color}
    
def create_enabled_event(event):
    return {"title":event.user_email,"groupId":event.id,"start":event.start_time,"end":event.end_time,"editable":"true","color":sql.Users.get(event.user_email).color}
    
# Function to return all scheduled events
def get_scheduled_events():
    event_list=[]
    all_schedule=sql.Schedules.get_all()
    event_list= list(map(create_enabled_event,all_schedule))   
    
    if(current_user.is_user_role()):
        all_schedule_minus_user_future=sql.Schedules.get_all_schedules_minus_user_future(current_user)
        user_schedule=sql.Schedules.get_future_user_schedules(current_user.email) 
        event_list= list(map(create_enabled_event,user_schedule))
        event_list= event_list + list(map(create_disabled_event,all_schedule_minus_user_future))
    else:
        future_schedules=sql.Schedules.get_future_schedules()
        past_schedules=sql.Schedules.get_past_schedules() 
        event_list= list(map(create_enabled_event,future_schedules))
        event_list= event_list + list(map(create_disabled_event,past_schedules))
    
    return event_list   

def user_exists(email):
    return sql.Users.get(email)

def is_user_valid(email):
    response=False
    is_in_current_schedule=sql.Schedules.get_future_user_schedules(email)

    if(len(is_in_current_schedule)>0 and is_in_current_schedule[0].start_time.astimezone()<=(datetime.now() + timedelta(hours=2)).astimezone()):
        response=True      
    return response

def time_is_valid(start_time, end_time):   
    now = (datetime.now() + timedelta(hours=2)).astimezone() # now is an aware datetime
    start_time = start_time.astimezone()
    end_time = end_time.astimezone()
    return start_time < end_time and start_time > now


def time_is_valid_end(start_time, end_time):   
    now = (datetime.now() + timedelta(hours=2)).astimezone() # now is an aware datetime
    start_time = start_time.astimezone()
    end_time = end_time.astimezone()
    return start_time < end_time and end_time > now

def time_is_not_overlap(start_time,end_time,schedule_id):
    schedules=sql.Schedules.get_overlap(start_time,end_time)
    return len(schedules)== 0 or (len(schedules)==1 and schedule_id == schedules[0].id)

def time_in_minutes(start_time,end_time):
    print('start_time: ',start_time,'; end_time: ',end_time,'= ',(end_time-start_time).total_seconds()/3600)
    return (end_time-start_time).total_seconds()/60

def conditions_to_update_or_create_event(request):
    user=sql.Users.get(escape(request.json['title']))       
    return user and current_user.user_event_validation(user.email) and  time_is_valid(parse(escape(request.json['start'])),parse(escape(request.json['end'])))and time_is_not_overlap(parse(escape(request.json['start'])),parse(escape(request.json['end'])),escape(request.json['groupId'])) and time_in_minutes(parse(escape(request.json['start'])),parse(escape(request.json['end'])))<= sql.Schedules.get_time_user(user)

def create_event_schedule(request):
    new_event=True
    sql.Schedules.new(escape(request.json['title']), parse(escape(request.json['start'])) ,parse(escape(request.json['end'])) ,escape(request.json['groupId']))
    sql.LogSchedules.new(current_user.email,escape(request.json['groupId']), 'Create event', parse(escape(request.json['start'])) ,parse(escape(request.json['end'])) )
    return new_event

def update_event_schedule(request):
    schedule = sql.Schedules.get(escape(request.json['groupId']))
    schedule.start_time = parse(escape(request.json['start']))
    schedule.end_time = parse(escape(request.json['end']))
    sql.LogSchedules.new(current_user.email,escape(request.json['groupId']),'Update event',parse(escape(request.json['start'])) ,parse(escape(request.json['end'])) )
    modified_event = sql.Schedules.modify(schedule)
    return modified_event

def delete_event_schedule(request):
    delete_event=True
    schedule = sql.Schedules.get(escape(request.json['groupId']))
    sql.LogSchedules.new(current_user.email,escape(request.json['groupId']),'Delete event',parse(escape(request.json['start'])) ,parse(escape(request.json['end'])))
    sql.Schedules.delete(schedule)
    return delete_event

"""    elif(current_user.is_admin_role()):
        all_schedule=sql.Schedules.get_all()
        event_list= list(map(create_enabled_event,all_schedule)) """      
        


