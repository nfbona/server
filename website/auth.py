from flask import Blueprint,request,session, render_template, redirect, url_for, flash
# User Login
from . import session_db,logout_procedure
from Modules.models import Users,Schedule
from Modules.forms import LogInForm,PasswordForm
from flask import Blueprint
from flask_login import login_user, login_required,current_user
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

auth = Blueprint("auth", __name__, template_folder='/app/templates', static_folder='/app/static')

@auth.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_procedure()
    return redirect(url_for('pages.home_page'))

@auth.route('/login', methods=['GET','POST'])
def login():
    form = LogInForm()
    if request.method == 'GET':
        if not(session.get('user')):
            return render_template('Login.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user = session_db.query(Users).filter_by(email=form.email.data).first()
            if user and user.checkPass(form.password_hash.data):
                login_user(user)
                session['user'] = user.email
            else:
                flash('Invalid username or password')
                return redirect(url_for('auth.login'))
    return redirect(url_for('pages.home_page'))

@auth.route('/user/signup', methods=['POST','GET'])
def signup():
    form = PasswordForm()
    if request.method == 'GET':
        our_users=session_db.query(Users).all()
        print(our_users)
        return render_template('SignUp.html', form=form, our_users=our_users)
    elif request.method == 'POST':
        if form.validate_on_submit(): 
            # Admin role or same user
            user = session_db.query(Users).filter_by(email=form.email.data).first()
            if(user is None):
                user = Users(email=form.email.data, password_hash= form.password_hash.data)   
                session_db.add(user)
                session_db.commit()
            else:
                flash('User already registered.')
            user=None
            form.email.data = None
            form.password_hash.data=None
            our_users= session_db.query(Users).order_by(Users.date_added + timedelta(hours=2)) 
    return redirect(url_for('auth.signup'))
 
@auth.route('/user/update/<string:email>', methods=['GET'])
def update(email):
    if('user' in session and (session['user'] == email or session_db.query(Users).filter_by(email=email).first().role_id ==1)):
        form = PasswordForm()
        name_update= session_db.query(Users).filter_by(email=email).first()
        #Validate form
        return render_template('UpdateUser.html', form=form,our_user=name_update)
    flash("Not valid operation.")
    return redirect(url_for('auth.signup'))
    
@auth.route('/user/update/<string:email>', methods=['POST'])
def updatePOST(email):
    email=str(email)
    if('user' in session and (session['user'] == email or session_db.query(Users).filter_by(email=email).first().role_id ==1)):
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

@auth.route('/user/delete/<string:email>', methods=['POST'])
@login_required
def delete(email):
    email=str(email)
    if('user' in session and (session['user'] == email or session_db.query(Users).get(session['user']).role_id ==1)):
        user=session_db.query(Users).filter_by(email=email).first()
        #Validate form
        flash('Usuari deletejat satisfactoriament.')
        try:			
            if('user' in session and session['user'] == user.email):
                print('SAME EMAIL AS USER')
                
                session_db.delete(user)
                session_db.commit()
                return redirect(url_for('auth.logout'))
            else:
                print('OTHER EMAIL')
                
                session_db.delete(user)
                session_db.commit()
                return redirect(url_for('auth.signup'))
        except:
            print('EXCEPT')
            return redirect(url_for('auth.signup'))
    flash("Operació no valida.")
    return redirect(url_for('auth.signup'))


@auth.errorhandler(404)
def error400(e):
    return render_template('error/404.html')  



@auth.errorhandler(500)
def error500(e):
    return render_template('error/500.html')  



#--------FUNCTIONS--------
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


def generate_unique_id(user):
    data = f"{user.email}-{datetime.utcnow()}"
    return generate_password_hash(data)