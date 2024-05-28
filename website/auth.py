from flask import Blueprint,request, render_template, redirect, url_for, flash,make_response
# User Login
from . import sql
from Modules.forms import LogInForm,PasswordForm
from flask import Blueprint
from flask_login import current_user
from .function import is_current_user_or_admin,login_required_custom

auth = Blueprint("auth", __name__, template_folder='/app/templates', static_folder='/app/static')

@auth.route('/logout', methods=['POST', 'GET'])
def logout():
    response= make_response(redirect(url_for('auth.login')))
    if current_user.is_authenticated:
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
            else:
                flash('Invalid username or password')
                return redirect(url_for('auth.login'))
    form.clean() 
    return redirect(url_for('pages.home_page'))

@auth.route('/user/signup', methods=['POST','GET'])
def signup():
    form = PasswordForm()
    our_users=sql.Users.get_all()
    
    if request.method == 'POST':
        if form.validate_on_submit(): 
            # Admin role or same user
            if(form.validations()):
                sql.Users.new(form.email.data,form.password_hash.data)
            else:
                flash('User already registered.')
            return redirect(url_for('auth.signup'))

    form.clean() 
    return render_template('SignUp.html', form=form, our_users=our_users)
 
@auth.route('/user/update/<string:email>', methods=['GET'])
def update(email):
    if(is_current_user_or_admin(str(email))):
        form = PasswordForm()
        name_update= sql.Users.get(email)
        #Validate form
        return render_template('UpdateUser.html', form=form,our_user=name_update)
    flash("Not valid operation.")
    return redirect(url_for('auth.signup'))
    
@auth.route('/user/update/<string:email>', methods=['POST'])
def updatePOST(email):
    form = PasswordForm()
    if form.validate_on_submit():
        email=str(email)
        if(is_current_user_or_admin(str(email))):
            user=sql.Users.get(email)
            user.password_hash=form.password_hash.data
            sql.Users.modify(user)
            flash("Usuari modificat satisfactoriament.")
        
    form.clean()
    return redirect(url_for('update',email=email))

@auth.route('/user/delete/<string:email>', methods=['POST'])
@login_required_custom
def delete(email):
    if(is_current_user_or_admin(str(email))):
        user=sql.Users.get(email) 
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

