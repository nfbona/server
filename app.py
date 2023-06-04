from flask import Flask, render_template, request,flash,redirect,url_for,session

# database
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# datetime
from datetime import datetime, timedelta

# Custom forms for login and password and more... 
from forms import PasswordForm,LogInForm,UserField

#import to password hashing
from werkzeug.security import generate_password_hash,check_password_hash

# User Login
from flask_login import UserMixin,LoginManager,login_user,login_required,logout_user,current_user

# Forms
from forms import PasswordForm,LogInForm,UserField


# initiating Flask, bootstrap, CRTF key
app = Flask(__name__)
app.config['SECRET_KEY'] = "t7w!z%C*F-JaNdRgUkXp2s5v8x/A?D(G+KbPeShVmYq3t6w9z$B&E)H@McQfTjWnZr4u7x!A%D*F-JaNdRgUkXp2s5v8y/B?E(H+KbPeShVmYq3t6w9z$C&F)J@NcQfT"
# sql lite
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:327baf2bcf1c1bc4ba3fbb5a9b95e69db7b1e61222e12c04bbd5e5a5d8a3676c@localhost/users'
db = SQLAlchemy(app)
migrate=Migrate(app,db)
 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
 
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id)) 
 

TIMETOWAIT=10


#Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(100), nullable=False,unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash= db.Column(db.String(128),nullable=False)
    # One user can have many roles, referencing an inexisting column in ROles that will be created automatically.
    # key_roles=db.relationship('Roles',backref='user',lazy='dynamic')
    
    # One to one relationship must have a role
    roles_id = db.Column(db.Integer, db.ForeignKey('roles.id'),nullable=False,default=2)
    
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

class Roles(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True,unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False,unique=True)

class Relay(db.Model, UserMixin):
    _id= db.Column(db.Integer,primary_key=True,nullable=False,unique=True)
    _state= db.Column(db.Boolean,nullable=False)
    _DateTime= db.Column(db.DateTime,nullable=False)
    
    @property
    def Relay(self):
        raise AttributeError('Error')
    
    @Relay.setter
    def state(self,state):
        self._state=state
        self._DateTime=datetime.now()

# the methods that the request can accept

@app.route('/', methods=['POST', 'GET'])
def login(): 
    email = None
    password = None
    form = LogInForm()
    CheckUser=None
    
    #Validate form
    if form.validate_on_submit():
        users = Users.query.filter_by(email=form.email.data).first()
        if users:
            print("hash: " + form.password_hash.data)
            if users.checkPass(form.password_hash.data):
                session['user']=generate_password_hash(str(users.id))
                login_user(users)
                flash('Correct username and password')
                return redirect(url_for('switch'))
        # clear data from form
            else:
                flash('Invalid username or password')
        else:
            flash('Invalid username or password')
    return render_template('index.html', email=email,form=form, password=password,CheckUser=CheckUser)

@app.route('/logout',methods=['POST','GET'])
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/user/signup', methods=['POST','GET'])
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
    return render_template('SignUp.html', email=email, form=form, password=password, our_users=our_users)
 
@app.route('/user/update/<int:id>', methods=['POST','GET'])
def update(id):
    print("USERID: ",current_user.id,", Role_ID: ",current_user.roles_id)
    if(current_user.id == id or current_user.roles_id ==1):
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
    flash("Not valid :S")
    return redirect(url_for('signup'))
    
    
    
@app.route('/user/delete/<int:id>', methods=['POST','GET'])
@login_required
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
@app.route('/switch', methods=['POST','GET'])
@login_required
def switch():
    return render_template('Switch.html')
    try:
        db.session.pop('user',None)
        del db.session['username']
    except:
        print("Error")
    return render_template('logout.html')

# database
@app.route('/database', methods=['POST','GET'])
def database():

    if request.method=='POST':
        db.drop_all()
        db.create_all()
    relays=Relay.query.all()
    print(relays)
    if(len(relays)==0):
        print("No relays")
        db.session.add(Relay(_id=1,_state=False,_DateTime=datetime.now()))
        db.session.add(Relay(_id=2,_state=False,_DateTime=datetime.now()))
        db.session.add(Relay(_id=3,_state=False,_DateTime=datetime.now()))
        db.session.add(Relay(_id=4,_state=False,_DateTime=datetime.now()))
        db.session.add(Relay(_id=5,_state=False,_DateTime=datetime.now()))
        db.session.add(Relay(_id=6,_state=False,_DateTime=datetime.now()))
        db.session.add(Relay(_id=7,_state=False,_DateTime=datetime.now()))
        db.session.add(Relay(_id=8,_state=False,_DateTime=datetime.now()))
        db.session.add(Relay(_id=9,_state=False,_DateTime=datetime.now()))
        db.session.add(Relay(_id=10,_state=False,_DateTime=datetime.now()))
        db.session.add(Relay(_id=11,_state=False,_DateTime=datetime.now()))
        db.session.add(Relay(_id=12,_state=False,_DateTime=datetime.now()))
        db.session.commit()
    
    roles=Roles.query.all()
    print(roles)
    if(len(roles)==0):
        db.session.add(Roles(id=1,name='Admin'))
        db.session.add(Roles(id=2,name='User'))
        db.session.commit()
    
    
    users=Users.query.order_by(Users.date_added + timedelta(hours=2))
    return render_template('databse.html',our_roles=roles,our_relays=relays,our_users=users)

#TESTING
@app.route('/user', methods=['POST','GET'])
@login_required
def user():
    email = None
    form = UserField()
    #Validate form
    if form.validate_on_submit():
        email = form.email.data
        form.email.data = ''
    return render_template('userList.html', email=email,form=form)

@app.route('/json', methods=['POST','GET'])
@login_required
def json():
    if request.method == 'POST':  #this block is only entered when the form is submitted
        rely=Relay.query.filter_by(_id=request.json['id']).first()
        print('IF: ',(datetime.now()-timedelta(seconds=TIMETOWAIT)) > rely._DateTime,', Delta time: ',rely._DateTime, ', Datetime to pass:',datetime.now()-timedelta(seconds=TIMETOWAIT))
        if (datetime.now()-timedelta(seconds=TIMETOWAIT)) > rely._DateTime:
            # changing the state of the relay
            """
            print(rely.state)
            """
            rely.state=request.json['value']
            db.session.commit()
        else:
            return {"Error":"1","relay":str(request.json['id'])}

        return {"Error":"0","relay":str(request.json['id'])}
    if request.method == 'GET':
        relays=Relay.copy()
        for relay in relays:
            time= str(int(TIMETOWAIT-datetime.now()-relay['_DateTime'].total_seconds()))
        return relays

    return Relay
 
 
 
 # NEW TEMPLATES TO BE MADE

# ------------------  NEW TEMPLATES TO BE MADE ------------------ #

@app.route('/history', methods=['POST','GET'])
@login_required
def history():
  return render_template('History.html')


@app.route('/configuration', methods=['POST','GET'])
@login_required
def configuration():
  return render_template('Configuration.html')

@app.errorhandler(404)
def error400(e):
    return render_template('error/404.html')  

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('error/404.html')

@app.errorhandler(500)
def error500(e):
    return render_template('error/500.html')  

def init():
    
    db.session.add(Roles(role="Admin"))


if __name__ == "__main__":
    app.run(debug=True)
    
