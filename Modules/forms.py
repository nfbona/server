# forms, need to create forms and 
from flask_wtf import FlaskForm
from wtforms import  SubmitField,PasswordField,EmailField,PasswordField
from wtforms.validators import DataRequired,Email,EqualTo
from flask import flash
from website import sql
import re

# Creation or updating

class FormBase(FlaskForm):
        __abstract__ = True
        
        def clean(self):
                for attr in self:
                        attr.data = None
                return True

class PasswordForm(FormBase):
        email=EmailField("Email",validators=[Email()])
        password_hash=PasswordField("Password",validators=[DataRequired(),EqualTo('password_check',message='Passwords must match')])
        password_check=PasswordField("Confirm Password",validators=[DataRequired()])
        submit = SubmitField('Submit')
        
        def validate_email_unique(self):
                user = sql.Users.get(self.email.data)
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

        
# Create to check in
class LogInForm(FormBase):
        email=EmailField("Email",validators=[Email()])
        password_hash=PasswordField("Password",validators=[DataRequired()])
        submit = SubmitField('Submit')

# Create form class TESTUING
class UserField(FormBase):
        email=EmailField("Email",validators=[Email()])
        submit = SubmitField('Submit')

class validator():
        def is_email(email):
                email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                if not re.match(email_regex, email):
                        return False
                return True