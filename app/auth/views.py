from flask import render_template, redirect, request, url_for, flash, session 
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, \
    PasswordResetForm, ChangeEmailForm
from datetime import date


# Might need more
@auth.before_app_request
def before_request():
    pass


'''
    Fix generating errors messages when form input fails validators
'''
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            session['last_login'] = current_user.last_login
            current_user.last_login = date.today()
            db.session.commit()
            next = request.args.get('next')
            if next is not None and next.startswith('/'):
                return redirect(next)
            return redirect(url_for('main.index'))
        flash('Invalid Email or Password')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are now logged out')
    return redirect(url_for('auth.login'))


'''
    Fix generating errors messages when form input fails validators
'''
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account registered')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/change-password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password(form.new_password.data)
            db.session.commit()
            flash('Password Succesfully Updated')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid Password')
    return render_template('auth/change-password')


@auth.route('/change-email', methods=['GET', 'POST'])
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            current_user.email = form.new_email.data
            db.session.commit()
            flash('Email Succesfully Updated')
            return redirect(url_for('main.inedx'))
        else:
            flash('Invalid Email Update')
    return render_template('auth/change-email.html')


@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    pass


@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    passwordForm = ChangePasswordForm()
    if passwordForm.validate_on_submit():
        if current_user.verify_password(passwordForm.old_password.data):
            current_user.password(passwordForm.new_password.data)
            db.session.commit()
            flash('Password Succesfully Updated')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid Password')


    emailForm = ChangeEmailForm()
    if emailForm.validate_on_submit():
        if current_user.verify_password(emailForm.password.data):
            current_user.email = emailForm.new_email.data
            db.session.commit()
            flash('Email Succesfully Updated')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid Email')

    return render_template('auth/profile.html', 
        emailForm=emailForm, passwordForm=passwordForm)

