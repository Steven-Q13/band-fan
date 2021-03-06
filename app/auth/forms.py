from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class RegistrationForm(FlaskForm):
	email = StringField('Email', 
						validators=[DataRequired(), Length(1,64), Email()])
	password = PasswordField('Password', validators=[
		DataRequired(), EqualTo('password2', 'Passwords must match.'),
		Regexp('^[A-Za-z0-9]*$', 0,'No special characters'), Length(4,18)])
	password2 = PasswordField('Confirm Password', validators=[DataRequired()])
	question1 = StringField('Securtiy Question 1', 
		validators=[DataRequired(),Length(1,(256))])
	question2 = StringField('Securtiy Question 2', 
		validators=[DataRequired(),Length(1,(256))])
	answer1 = StringField('Securtiy Answer 1', 
		validators=[DataRequired(),Length(1,(64))])
	answer2 = StringField('Securtiy Answer 2', 
		validators=[DataRequired(),Length(1,(64))])
	subscribe = BooleanField('Subscribe to Band-Fan Emails')
	submit = SubmitField('REGISTER')

	#Custom validator auto run on email field
	def validate_email(self, field):
		if User.query.filter_by(email=field.data.lower()).first():
			raise ValidationError('Email already registered.')

	#Custom validator auto run on username field
	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('Username already taken.')


class LoginForm(FlaskForm):
	email = StringField('Email', 
						validators=[DataRequired(), Length(1,64), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Keep Me Logged In')
	submit = SubmitField('LOGIN')


class ChangePasswordForm(FlaskForm):
	old_password = PasswordField('Old Password', validators=[DataRequired()])
	new_password = PasswordField('New Password', validators=[
		DataRequired(), EqualTo('new_password2', 'Passwords must match.'),
		Regexp('^[A-Za-z][A-Za-z0-9]*$', 0,'No special characters')])
	new_password2 = PasswordField('Confirm new Password', 
								  validators=[DataRequired()])
	submit = SubmitField('Update Password')


class ChangeEmailForm(FlaskForm):
	new_email = StringField('New Email', 
						validators=[DataRequired(), Length(1,64), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Update Email')


class PasswordResetForm(FlaskForm):
	new_password = PasswordField('Password', validators=[
		DataRequired(), EqualTo('new_password2', 'Passwords must match.'),
		Regexp('^[A-Za-z0-9]*$', 0,'No special characters'), Length(4,18)])
	new_password2 = PasswordField('Confirm Password', validators=[DataRequired()])
	answer1 = StringField('Securtiy Answer 1', 
		validators=[DataRequired(),Length(1,(64))])
	answer2 = StringField('Securtiy Answer 2', 
		validators=[DataRequired(),Length(1,(64))])
	submit = SubmitField('RESET')


class PasswordResetFormEmail(FlaskForm):
	email = StringField('Email', 
						validators=[DataRequired(), Length(1,64), Email()])
	submit = SubmitField('SUBMIT')