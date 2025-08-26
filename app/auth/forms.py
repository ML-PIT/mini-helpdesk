from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Optional
from app.models.user import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], 
                       render_kw={'placeholder': 'Enter your email address'})
    password = PasswordField('Password', validators=[DataRequired()],
                           render_kw={'placeholder': 'Enter your password'})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)],
                          render_kw={'placeholder': 'Choose a username'})
    email = StringField('Email', validators=[DataRequired(), Email()],
                       render_kw={'placeholder': 'Enter your email address'})
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)],
                            render_kw={'placeholder': 'Your first name'})
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)],
                           render_kw={'placeholder': 'Your last name'})
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ], render_kw={'placeholder': 'Create a strong password'})
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ], render_kw={'placeholder': 'Repeat your password'})
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already registered. Please use a different email address.')

class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)],
                       render_kw={'placeholder': '+49 123 456789'})
    department = StringField('Department', validators=[Optional(), Length(max=100)],
                           render_kw={'placeholder': 'IT, Marketing, Sales, etc.'})
    location = StringField('Location', validators=[Optional(), Length(max=100)],
                         render_kw={'placeholder': 'City, Country'})
    submit = SubmitField('Update Profile')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()],
                                   render_kw={'placeholder': 'Enter your current password'})
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ], render_kw={'placeholder': 'Enter your new password'})
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ], render_kw={'placeholder': 'Confirm your new password'})
    submit = SubmitField('Change Password')

class RequestPasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()],
                       render_kw={'placeholder': 'Enter your registered email address'})
    submit = SubmitField('Request Password Reset')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No account found with that email address.')
        if user.microsoft_id:
            raise ValidationError('Password reset is not available for Microsoft accounts.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ], render_kw={'placeholder': 'Enter your new password'})
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ], render_kw={'placeholder': 'Repeat your new password'})
    submit = SubmitField('Reset Password')