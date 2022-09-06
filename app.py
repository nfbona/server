from asyncore import write
from wsgiref.validate import validator
from flask import Flask, render_template, url_for, request, redirect

# database
from flask_sqlalchemy import SQLAlchemy

# datetime
from datetime import datetime, timedelta

# forms, need to create forms and 
from flask_wtf import FlaskForm
from wtforms import  SubmitField,PasswordField,EmailField
from wtforms.validators import DataRequired,Email

# initiating Flask, bootstrap, CRTF key
app = Flask(__name__)
app.config['SECRET_KEY'] = "t7w!z%C*F-JaNdRgUkXp2s5v8x/A?D(G+KbPeShVmYq3t6w9z$B&E)H@McQfTjWnZr4u7x!A%D*F-JaNdRgUkXp2s5v8y/B?E(H+KbPeShVmYq3t6w9z$C&F)J@NcQfT"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

#Model
class Users(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(100), nullable=False,unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # create a string
    def __repr__(self):
            return '<Email %r>' % self.email

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String())

# Create form class
class PasswordForm(FlaskForm):
        email=EmailField("Email",validators=[Email()])
        password=PasswordField("Password",validators=[DataRequired()])
        submit = SubmitField('Submit')

# Create form class TESTUING
class UserField(FlaskForm):
        email=EmailField("Email",validators=[Email()])
        submit = SubmitField('Submit')



# the methods that the request can accept

@app.route('/', methods=['POST', 'GET'])
def index():
    email = None
    password = None
    form = PasswordForm()
    #Validate form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        form.email.data = ''
        form.password.data=''
    return render_template('index.html', email=email,form=form, password=password)

@app.route('/user/add', methods=['POST','GET'])
def signup():
    email = None
    password = None
    form = PasswordForm()
    #Validate form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        print(user is None)
        if(user is None):
            user = Users(email=form.email.data)
            db.session.add(user)
            db.session.commit()
        email = form.email.data
        password = form.password.data
        form.email.data = ''
        form.password.data=''
        our_users= Users.query.order_by(Users.date_added + timedelta(hours=2))
    return render_template('UserList.html', email=email, form=form, password=password, our_users=our_users)
 

#TESTING
@app.route('/user', methods=['POST','GET'])
def user():
    email = None
    form = UserField()
    #Validate form
    if form.validate_on_submit():
        email = form.email.data
        form.email.data = ''
    return render_template('user.html', email=email,form=form)

@app.errorhandler(404)
def error400(e):
    return render_template('error/404.html')  

@app.errorhandler(500)
def error500(e):
    return render_template('error/500.html')  

if __name__ == "__main__":
    app.run(debug=True)
