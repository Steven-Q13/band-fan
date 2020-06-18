from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import main
from .. import db
from ..models import User


@main.route('/', methods=['GET'])
def index():
    return render_template('main/index.html')



@main.route('/profile', methods=['GET'])
@login_required
def profile():
	return render_template('a.html')

'''
	https://stackoverflow.com/questions/11078509/how-to-increase-the-clickable-area-of-a-a-tag-button
	https://css-tricks.com/books/fundamental-css-tactics/scale-typography-screen-size/
'''