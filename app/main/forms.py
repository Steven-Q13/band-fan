from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
	search = StringField('Band name...', validators=[DataRequired()])
	submit = SubmitField('Search')
