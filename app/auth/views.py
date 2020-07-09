from flask import current_app, render_template, redirect, request, url_for, flash, session 
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, \
    PasswordResetForm, ChangeEmailForm, PasswordResetFormEmail
from datetime import date
from ..api_calls import Mail


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
            session['last_login'] = str(current_user.last_login)
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
                    password=form.password.data,
                    question1=form.question1.data,
                    question2=form.question2.data,
                    answer1=form.answer1.data.lower(),
                    answer2=form.answer2.data.lower(),
                    subscribed=form.subscribe.data)
        db.session.add(user)
        db.session.commit()
        mail = Mail(current_app.config['SECRET_KEY'], 
                current_app.config['SERVER_EMAIL'], 
                url_for('auth.unsubscribe'), 
                url_for('main.updates'), 
                url_for('main.info'))
        mail.sendWelcomeEmail(user.email)
        mail.quit()
        flash('Account registered')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
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
            mail = Mail(current_app.config['SECRET_KEY'], 
                        current_app.config['SERVER_EMAIL'], 
                        url_for('auth.unsubscribe'), 
                        url_for('main.updates'), 
                        url_for('main.info'))
            mail.sendWelcomeEmail(current_user.email)
            mail.quit()
            return redirect(url_for('main.index'))
        else:
            flash('Invalid Email')
    return render_template('auth/settings.html', 
                            subscribed=current_user.subscribed,
                            emailForm=emailForm, 
                            passwordForm=passwordForm)


@auth.route('/reset/email', methods=['GET', 'POST'])
def reset_email_form():
    form = PasswordResetFormEmail()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email=form.email.data.lower()).first()
        if user:
            return redirect(url_for('auth.reset_password_form', userID=user.id))
        else:
            flash("User doesn't exist")
    return render_template('auth/reset_email.html', form=form)


@auth.route('/reset/password/<userID>', methods=['GET', 'POST'])
def reset_password_form(userID):
    form = PasswordResetForm()
    user = db.session.query(User).filter_by(id=userID).first()
    if form.validate_on_submit():
        if user.answer1==form.answer1.data.lower() and user.answer2==form.answer2.data.lower():
            user.password = form.new_password.data
            db.session.commit()
            flash('Password Succesfully Reset')
            return redirect(url_for('auth.login'))
    else:
        flash('A1 %s \t A2 %s' % (user.answer1, user.answer2))

    return render_template('auth/reset_password.html', form=form,
        question1=user.question1, question2=user.question2)


@auth.route('/unsubscribe', methods=['GET'])
@login_required
def unsubscribe():
    current_user.subscribed = False
    db.session.commit()
    flash('You have been unsubscribed from all Band-Fan emails.')
    return redirect(url_for('main.index'))


@auth.route('/subscribe', methods=['GET'])
@login_required
def subscribe():
    current_user.subscribed = True
    db.session.commit()
    mail = Mail(current_app.config['SECRET_KEY'], 
                current_app.config['SERVER_EMAIL'], 
                url_for('auth.unsubscribe'), 
                url_for('main.updates'), 
                url_for('main.info'))
    mail.sendWelcomeEmail(current_user.email)
    mail.quit()
    flash('You have subscribed to Band-Fan emails.')
    return redirect(url_for('main.index'))






