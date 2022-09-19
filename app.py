from flask import Flask, render_template, request,flash

# database
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# datetime
from datetime import datetime, timedelta

# forms, need to create forms and 
from flask_wtf import FlaskForm
from wtforms import  SubmitField,PasswordField,EmailField,PasswordField,BooleanField,ValidationError
from wtforms.validators import DataRequired,Email,EqualTo,Length

#import to password hashing
from werkzeug.security import generate_password_hash,check_password_hash


# initiating Flask, bootstrap, CRTF key
app = Flask(__name__)
app.config['SECRET_KEY'] = "t7w!z%C*F-JaNdRgUkXp2s5v8x/A?D(G+KbPeShVmYq3t6w9z$B&E)H@McQfTjWnZr4u7x!A%D*F-JaNdRgUkXp2s5v8y/B?E(H+KbPeShVmYq3t6w9z$C&F)J@NcQfT"
# sql lite
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:327baf2bcf1c1bc4ba3fbb5a9b95e69db7b1e61222e12c04bbd5e5a5d8a3676c@localhost/users'
db = SQLAlchemy(app)
migrate=Migrate(app,db)

#Model
class Users(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(100), nullable=False,unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash= db.Column(db.String(128),nullable=False)
    # create a string
    def __repr__(self):
            return '<Email %r>' % self.email
    @property
    def password(self):
        raise AttributeError('Password is not a readable option')
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def checkPass(self,password):
       return check_password_hash(self.password_hash,password)
   
# Creation or updating
class PasswordForm(FlaskForm):
        email=EmailField("Email",validators=[Email()])
        password_hash=PasswordField("Password",validators=[DataRequired(),EqualTo('passwordCheck',message='Passwords must match')])
        passwordCheck=PasswordField("Confirm Password",validators=[DataRequired()])
        submit = SubmitField('Submit')
        
# Create to check in
class LogIn(FlaskForm):
        email=EmailField("Email",validators=[Email()])
        password_hash=PasswordField("Password",validators=[DataRequired()])
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
    form = LogIn()
    LoginPass=None
    CheckUser=None
    #Validate form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # clear data from form
        form.email.data = ''
        form.password_hash.data=''
        CheckUser = Users.query.filter_by(email=email).first()
        if(CheckUser):
            LoginPass=check_password_hash(CheckUser.password_hash,password)
        return render_template('index.html', email=email,form=form, password=password,CheckUser=CheckUser,LoginPass=LoginPass)

    return render_template('index.html', email=email,form=form, password=password,CheckUser=CheckUser)


@app.route('/user/add', methods=['POST','GET'])
def signup():
    email = None
    password = None
    form = PasswordForm()
    our_users=Users.query.all()
    #Validate form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if(user is None):
            user = Users(email=form.email.data, password_hash= generate_password_hash(form.password_hash.data,"sha256"))
            db.session.add(user)
            db.session.commit()
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data=''
        our_users= Users.query.order_by(Users.date_added + timedelta(hours=2))
    return render_template('UserList.html', email=email, form=form, password=password, our_users=our_users)
 
@app.route('/user/update/<int:id>', methods=['POST','GET'])
def update(id):
    email = None
    password = None
    form = PasswordForm()
    name_update=Users.query.get_or_404(id)
    #Validate form
    if form.validate_on_submit():
        name_update.password_hash=generate_password_hash(form.password_hash.data,"sha256")
        db.session.commit()
        form.email.data = ''
        form.password_hash.data = ''
        flash("User modified successfully!")
    return render_template('UpdateUser.html', email=email, form=form, password=password,our_user=name_update)
 

@app.route('/user/delete/<int:id>', methods=['POST','GET'])
def delete(id):
    email = None
    password = None
    form = PasswordForm()
    name_update=Users.query.get_or_404(id)
    #Validate form
    try:			
        db.session.delete(name_update)
        db.session.commit()
        flash("User deleted successfully!")
        name_update.email = request.form['email']
        name_update.password = request.form['password']
        db.session.commit()
        form.email.data = ''
        form.password_hash.data=''
        password=name_update.password_hash
        our_users= Users.query.order_by(Users.date_added + timedelta(hours=2))
        return render_template('UserList.html', email=email, form=form, password=password, our_users=our_users)
    except:
        our_users= Users.query.order_by(Users.date_added + timedelta(hours=2))
        return render_template('UserList.html', email=email, form=form, password=password,our_users=our_users)
     
 
 

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

@app.route('/json', methods=['POST','GET'])
def json():
    json={"asd":"asd", "bb":"asd","sdasd":2}
    return json
    return render_template('user.html', email=email,form=form)




@app.errorhandler(404)
def error400(e):
    return render_template('error/404.html')  

@app.errorhandler(500)
def error500(e):
    return render_template('error/500.html')  

if __name__ == "__main__":
    app.run(debug=True)
