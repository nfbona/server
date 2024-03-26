from flask import Blueprint,request,session, render_template, redirect, url_for, flash
# User Login
from . import sql
from Modules.forms import LogInForm,PasswordForm
from flask import Blueprint
from flask_login import login_required
from datetime import datetime, timedelta

auth = Blueprint("auth", __name__, template_folder='/app/templates', static_folder='/app/static')

@auth.route('/logout', methods=['POST', 'GET'])
def logout():
    user=session.get('user')
    user.logout()
    return redirect(url_for('pages.home_page'))

@auth.route('/login', methods=['GET','POST'])
def login():
    form = LogInForm()
    if request.method == 'GET':
        if not(session.get('user')):
            return render_template('Login.html', form=form)
        
    elif request.method == 'POST':
        if form.validate_on_submit():
            user = sql.get_user(form.email.data)
            if user and user.checkPass(form.password_hash.data):
                user.login()
            else:
                flash('Invalid username or password')
                return redirect(url_for('auth.login'))
            
    return redirect(url_for('pages.home_page'))

@auth.route('/user/signup', methods=['POST','GET'])
def signup():
    form = PasswordForm()
    if request.method == 'GET':
        our_users=sql.get_users()
        return render_template('SignUp.html', form=form, our_users=our_users)
    elif request.method == 'POST':
        if form.validate_on_submit(): 
            # Admin role or same user
            if(form.validations()):
                form.create_user()
            else:
                flash('User already registered.')
            form.clean()
            
            our_users= sql.get_users()
    return redirect(url_for('auth.signup'))
 
@auth.route('/user/update/<string:email>', methods=['GET'])
def update(email):
    user=sql.get_user(str(email))
    if(email.is_same_user(session.get('user')) or user.is_admin_role()):
        form = PasswordForm()
        name_update= sql.get_user(email)
        #Validate form
        return render_template('UpdateUser.html', form=form,our_user=name_update)
    flash("Not valid operation.")
    return redirect(url_for('auth.signup'))
    
@auth.route('/user/update/<string:email>', methods=['POST'])
def updatePOST(email):
    if form.validate_on_submit():
        email=str(email)
        user=sql.get_user(email)
        if(email.is_same_user(session.get('user')) or user.is_admin_role()):
            form = PasswordForm()
            #Validate form
        # if 
            user.set_password(form.password_hash.data)
            sql.modify_object(user)
            form.clean()
            flash("Usuari modificat satisfactoriament.")
        
    return redirect(url_for('update',email=email))

@auth.route('/user/delete/<string:email>', methods=['POST'])
@login_required
def delete(email):
    
    user=sql.get_user(email) 
    if(email.is_same_user(session.get('user')) == email or user.is_admin_role()):
        #Validate form
        flash('Usuari borrat satisfactoriament.')
        sql.delete_object(user)
        try:			
            if(email.is_same_user(session.get('user'))):
                return redirect(url_for('auth.logout'))
            else:
                sql.delete_object(user)
                return redirect(url_for('auth.signup'))
        except:
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
    all_schedule=sql.get_schedule()
    user=sql.get_user(session['user'])
        
    for event in all_schedule:
        if session['user']==event.email:
            modified_list.append({"title":event.email,"groupId":event.email,"start":event.start_time,"end":event.end_time,"editable":"true","color":user.color})
        else:
            try:
                modified_list.append({"title":event.email,"groupId":event.email,"start":event.start_time,"end":event.end_time,"editable":"false","color":user.color})
            except:
                sql.delete_object(event)
    return modified_list   


