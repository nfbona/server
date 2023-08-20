
# forms, need to create forms and 
from flask_wtf import FlaskForm
from wtforms import  SubmitField,PasswordField,EmailField,PasswordField,BooleanField,ValidationError,StringField
from wtforms.validators import DataRequired,Email,EqualTo,Length


# Creation or updating
class PasswordForm(FlaskForm):
        email=EmailField("Email",validators=[Email()])
        password_hash=PasswordField("Password",validators=[DataRequired(),EqualTo('passwordCheck',message='Passwords must match')])
        password_check=PasswordField("Confirm Password",validators=[DataRequired()])
        submit = SubmitField('Submit')
        
# Create to check in
class LogInForm(FlaskForm):
        email=EmailField("Email",validators=[Email()])
        password_hash=PasswordField("Password",validators=[DataRequired()])
        submit = SubmitField('Submit')

# Create form class TESTUING
class UserField(FlaskForm):
        email=EmailField("Email",validators=[Email()])
        submit = SubmitField('Submit')
