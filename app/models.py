import hashlib
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app, request, url_for
from . import db, login_manager

#Can add any necessary methods to flask-login's default anonymous user
class AnonymousUser(AnonymousUserMixin):
	is_logged_in = False
login_manager.anonymous_user = AnonymousUser


class Follow(db.Model):
	__tablename__ = 'follows'
	follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
							primary_key=True)
	band_following_id = db.Column(db.Integer, db.ForeignKey('bands.id'),
								  primary_key=True)
	last_checkin = db.Column(db.DateTime, default=datetime.utcnow)

	def ping(self):
		self.last_checkin = datetime.utcnow()


class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(64), unique=True, index=True)
	username = db.Column(db.String(48), unique=True)
	password_hash = db.Column(db.String(100))
	signup_date = db.Column(db.DateTime(), default=datetime.utcnow)
	last_login = db.Column(db.DateTime(), default=datetime.utcnow)
	following = db.relationship('Follow', 
								foreign_keys=[Follow.follower_id],
								backref=db.backref('following', lazy='joined'),
								lazy='dynamic',
								cascade='all, delete-orphan')

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	#Need to change to use emails tokens when email auth is used
	@staticmethod
	def reset_password(users_email, old_password, new_password):
		user = User.query.filter_by(emaail=users_email).first()
		if user is not None and user.verify_password(old_password):
			user.password(new_password)
			return True
		return False

	def ping(self):
		self.lastseen = datetime.utcnow()

	def follow(self, band):
		if not self.is_following(band):
			f = Follow(follower=self, band_following=band)
			db.session.add(f)

	def unfollow(self, band):
		f = self.followed.filter_by(band_following_id=band.id).first()
		if f:
			db.session.delete(f)

	def is_following(self, band):
		if band.id is not None:
			return False
		return self.following.filter_by(
			band_following_id=band.id).first() is not None

	is_logged_in = True


class Band(db.Model):
	__tablename__ = 'bands'
	id = db.Column(db.Integer, primary_key=True, index=True)
	name = db.Column(db.String(64), unique=True, index=True)
	followers = db.relationship('Follow',
								foreign_keys=[Follow.band_following_id],
								backref=db.backref('band_following', 
												   lazy='joined'),
								lazy='dynamic',
								cascade='all, delete-orphan')
	lastest_release = db.Column(db.DateTime())
	last_update = db.Column(db.DateTime(), default=datetime.utcnow)

	def ping(self):
		self.last_update = db.datetime.utcnow

	def users_to_notify(self):
		all_users = self.following.all()
		users = []
		comp_time = self.lastest_release
		for u in all_users:
			if u.last_checkin<comp_time:
				users.append(u)
			else:
				u.ping()
		return users


@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))