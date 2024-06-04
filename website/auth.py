from flask import Blueprint,request, render_template, redirect, url_for, flash,make_response
# User Login
from . import sql
from Modules.forms import LogInForm,PasswordForm,validator
from flask import Blueprint
from flask_login import current_user
from .function import login_required_custom,login_required_admin,login_required_admin_or_current_user
from html import escape

auth = Blueprint("auth", __name__, template_folder='/app/templates', static_folder='/app/static')

@auth.route('/logout', methods=['POST', 'GET'])
def logout():
    response= make_response(redirect(url_for('auth.login')))
    if current_user.is_authenticated:
        sql.LogUsers.new(current_user.email,'Logout')
        sql.Users.logout(current_user)
    return response

@auth.route('/login', methods=['GET','POST'])
def login():
    form = LogInForm()
    if request.method == 'GET':
        if not(current_user.is_authenticated):
            return render_template('Login.html', form=form)
        
    elif request.method == 'POST':
        if form.validate_on_submit():
            user = sql.Users.get(form.email.data)
            if user and user.checkPass(form.password_hash.data):
                sql.Users.login(user)
                sql.LogUsers.new(current_user.email,'Login')
            else:
                flash('Invalid username or password')
                return redirect(url_for('auth.login'))
    form.clean() 
    return redirect(url_for('pages.home_page'))

@auth.route('/user/signup', methods=['POST','GET'])
def signup():
    form = PasswordForm()
    our_SignUprequest=sql.SignUpRequest.get_all()
    
    if request.method == 'POST':
        if form.validate_on_submit(): 
            # Admin role or same user
            if(form.validations()):
                sql.SignUpRequest.new(form.email.data,form.password_hash.data)
                sql.LogSignUpRequest.new('',form.email.data,'Request')
                flash('Request done to admin.')
            else:
                flash('User already registered.')
            return redirect(url_for('auth.signup'))

    form.clean() 
    return render_template('SignUp.html', form=form, our_SignUprequest=our_SignUprequest)
 
@auth.route('/user/update/<string:email>', methods=['GET','POST'])
@login_required_admin_or_current_user
def update(email):
    form = PasswordForm()
    if request.method == 'GET':
        name_update= sql.Users.get(email)
        if name_update:
            our_userlogs=sql.LogUsers.get_all_user_logs(email)
            our_schedulelogs=sql.Schedules.get_future_user_schedules(email)
            our_relaylogs=sql.LogRelays.get_all_user_logs(email)
        
    if request.method == 'POST': 
        form.email.data=email   
        if form.validate_on_submit():
            user=sql.Users.get(email)
            user.password_hash=form.password_hash.data
            sql.Users.modify(user)
            sql.LogUsers.new(current_user.email,'Update password')
            flash("Usuari modificat satisfactoriament.")
            
        return redirect(url_for('auth.update',email=email))
    
    return render_template('Config.html', form=form,our_user=name_update,our_relaylogs=our_relaylogs,our_userlogs=our_userlogs,our_schedulelogs=our_schedulelogs)
    
@auth.route('/user/delete/<string:email>', methods=['POST'])
@login_required_admin
def delete(email):
    if(current_user.is_current_user_or_admin(email)):
        user=sql.Users.get(email) 
        sql.LogUsers.new(current_user.email,'Delete user')
        #Validate form
        flash('Usuari borrat satisfactoriament.')
        sql.Users.delete(user)
        try:			
            if(email==current_user.email):
                return redirect(url_for('auth.logout'))
            else:
                return redirect(url_for('auth.signup'))
        except:
            return redirect(url_for('auth.signup'))
    flash("Operació no valida.")

    return redirect(url_for('auth.signup'))


@auth.route('/user/signuprequest/accept/<string:email>', methods=['GET'])
@login_required_admin
def signuprequestaccept(email):
    if validator.is_email(email):
        user_SignUpRequest=sql.SignUpRequest.get(email)
        sql.Users.new(email,user_SignUpRequest.password)
        sql.LogSignUpRequest.new(current_user.email,email,'Accepted')
        sql.LogUsers.new(current_user.email,'Create user')
        sql.SignUpRequest.delete(user_SignUpRequest)
        flash('Accepted user: '+email)
    else:
        flash('Invalid email.')
        
    return redirect(url_for('auth.signup'))

@auth.route('/user/signuprequest/delete/<string:email>', methods=['GET'])
@login_required_admin
def signuprequestdeny(email):
    if validator.is_email(email):
        user_SignUpRequest=sql.SignUpRequest.get(email)
        sql.LogSignUpRequest.new(current_user.email,email,'Denied')
        sql.SignUpRequest.delete(user_SignUpRequest)
        flash('Denied user: '+email)
    else:
        flash('Invalid email.')
        
    return redirect(url_for('auth.signup'))

@auth.route('/deleteUsers', methods=['POST'])
@login_required_admin
def deleteUsers():
    userList=escape(request.json['emails'])
    response={"users_deleted":[], "users_not_existing":[]}
    for email in userList:
        if(validator.is_email(email)):
            user=sql.Users.get(email)
            if user:
                sql.LogUsers.new(current_user.email,'Deactivate user')
                sql.Schedules.delete_all_user_future_schedules(user)
                user.is_active=False
                sql.Users.modify(user)
                response.get('users_deleted').append(email)
            else:
                response.get('users_not_existing').append(email)
        else:
            response.get('users_not_existing').append(email)
    return response

@auth.route('/roleUser', methods=['POST'])
@login_required_admin
def roleUser():
    user=escape(request.json['email'])
    response={"is_active":""}
    if(validator.is_email(user)):
        user=sql.Users.get(user)
        if user:
            sql.Users.change_role(user,escape(request.json['role']))
            sql.LogUsers.new( user.email,current_user.email+' changing role to '+str(escape(request.json['role'])))
            response['is_active']="OK"
        else:
            response['is_active']="Error"
    else:
        response['is_active']="Error"
    return response