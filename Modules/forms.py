# forms, need to create forms and 
from flask_wtf import FlaskForm
from wtforms import  SubmitField,PasswordField,EmailField,PasswordField
from wtforms.validators import DataRequired,Email,EqualTo
from .models import Users
from flask import flash
from website import sql

# Creation or updating
class PasswordForm(FlaskForm):
        email=EmailField("Email",validators=[Email()])
        password_hash=PasswordField("Password",validators=[DataRequired(),EqualTo('password_check',message='Passwords must match')])
        password_check=PasswordField("Confirm Password",validators=[DataRequired()])
        submit = SubmitField('Submit')
        
        def validate_email_unique(self):
                user = Users.query.filter_by(email=self.email.data).first()
                if user:
                        return False
                return True
                

        def validate_password_length(self):
                if len(self.password_hash.data) < 8:
                        flash('Password must be at least 8 characters long.')
                        return False
                return True

        def validate_passwords_equal(self):
                if self.password_hash.data != self.password_check.data:
                        flash('Passwords must match.')
                        return False
                return True
        
        def validations(self):
                if not(self.validate_email_unique()):
                        flash('Email already registered.')
                        return False
                if not(self.validate_password_length()):
                        flash('Password must be at least 8 characters long.')
                        return False
                if not(self.validate_passwords_equal()):
                        flash('Passwords must match.')
                        return False
                return True
                
        def create_user(self):
                user = Users(email=self.email.data, password_hash=self.password_hash.data)
                sql.add_object(user)
                return True
                
        def clean(self):
                self.email.data = None
                self.password_hash.data = None
                self.password_check.data = None
                return True
        
# Create to check in
class LogInForm(FlaskForm):
        email=EmailField("Email",validators=[Email()])
        password_hash=PasswordField("Password",validators=[DataRequired()])
        submit = SubmitField('Submit')

# Create form class TESTUING
class UserField(FlaskForm):
        email=EmailField("Email",validators=[Email()])
        submit = SubmitField('Submit')
