# pip install flask-wtf
from flask_wtf import FlaskForm # For inheritance
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
# NOTE: validator Email should be installed by {pip install email_validator}

from flaskblog.model import User
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed


class RegistrationForm(FlaskForm):
    username = StringField('Username', # field label
                           validators = [DataRequired(), Length(min = 2, max = 20)]
                           )
    
    email = StringField('Email',
                        validators = [DataRequired(), Email()]
                        )
    
    password = PasswordField('Password',
                             validators = [DataRequired()]
                             )
    
    confirm_password = PasswordField('Confirm Password',
                                     validators = [DataRequired(), EqualTo('password')]
                                     )
    
    submit = SubmitField('Sign up')

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):

    email = StringField('Email',
                        validators = [DataRequired(), Email()]
                        )
    
    password = PasswordField('Password',
                             validators = [DataRequired()]
                             )
    
    remember = BooleanField('Remember me')

    submit = SubmitField('Log in')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', # field label
                           validators = [DataRequired(), Length(min = 2, max = 20)]
                           )
    
    email = StringField('Email',
                        validators = [DataRequired(), Email()]
                        )
    picture = FileField('Update Profile Picture', validators = [FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class PostForm(FlaskForm):
    title = StringField('Title', validators = [DataRequired()])
    # from wtforms import TextAreaField
    content = TextAreaField('Content', validators = [DataRequired()])
    submit = SubmitField('Post')