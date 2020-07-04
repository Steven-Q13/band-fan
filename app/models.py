import hashlib
from datetime import date
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

	def ping(self):
		self.last_checkin = datetime.utcnow()


class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(64), unique=True, index=True)
	username = db.Column(db.String(48), unique=True)
	password_hash = db.Column(db.String(100))

	last_login = db.Column(db.Date(), default=date.today)
	following = db.relationship('Follow', 
		foreign_keys=[Follow.follower_id], 
		backref=db.backref('following', lazy='joined'),
		lazy='dynamic', cascade='all, delete-orphan')

	subscribed = db.Column(db.Boolean(), default=True)
	question1 = db.Column(db.String(256))
	question2 = db.Column(db.String(256))
	answer1 = db.Column(db.String(96))
	answer2 = db.Column(db.String(96))

	latest_song_uri = db.Column(db.String(64))

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)


	@staticmethod
	def reset_password(users_email, old_password, new_password, answer1, answer2):
		user = User.query.filter_by(emaail=users_email).first()
		if user is not None and user.verify_password(old_password) and user.answer1==answer1.lower() and user.answer2==answer2.lower():
			user.password(new_password)
			return True
		return False

	def follow(self, bandID):
		if not self.is_following(bandID):
			row = Follow(follower_id=self.id, band_following_id=bandID)
			db.session.add(row)

	def unfollow(self, bandID):
		row = self.following.filter_by(band_following_id=bandID).first()
		if row:
			db.session.delete(row)

	def is_following(self, bandID):
		return self.following.filter_by(
			band_following_id=bandID).first() is not None

	#Ping should email user if they are subscribed that a band has an update
	def ping(self, new_song_id):
		pass

	is_logged_in = True


class Band(db.Model):
	__tablename__ = 'bands'
	id = db.Column(db.Integer, primary_key=True, index=True)
	name = db.Column(db.String(64))
	img = db.Column(db.String(128))
	uri = db.Column(db.String(64), unique=True, index=True)

	top_name = db.Column(db.String(64))
	top_img = db.Column(db.String(128))
	top_uri = db.Column(db.String(64))
	top_date = db.Column(db.Date())

	newest_name = db.Column(db.String(64))
	newest_img = db.Column(db.String(128))
	newest_uri = db.Column(db.String(64))
	newest_date = db.Column(db.Date())

	followers = db.relationship('Follow',
								foreign_keys=[Follow.band_following_id],
								backref=db.backref('band_following', 
												   lazy='joined'),
								lazy='dynamic',
								cascade='all, delete-orphan')
	#last_update = db.Column(db.Date(), default=date.today)


	def users_to_notify(self):
		all_users = self.following.all()
		users = []
		comp_time = self.newest_date
		for u in all_users:
			if u.last_checkin<comp_time:
				users.append(u)
			else:
				u.ping(self.newest_uri)
		return users

	def colDict(self):
		info = {'artist':{}, 'top_track':{}, 
			'newest_track':{}, 'dbID':self.id}
		info['artist']['name'] = self.name
		info['artist']['uri'] = self.uri
		info['artist']['img'] = self.img

		info['top_track']['name'] = self.top_name
		info['top_track']['uri'] = self.top_uri
		info['top_track']['date'] = self.top_date.isoformat()
		info['top_track']['img'] = self.top_img

		info['newest_track']['name'] = self.newest_name
		info['newest_track']['date'] = self.newest_date.isoformat()
		info['newest_track']['uri'] = self.newest_uri
		info['newest_track']['img'] = self.newest_img

		return info


@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))