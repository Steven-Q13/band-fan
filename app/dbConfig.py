from . import db
import click
from datetime import date
from .api_calls import Spotify, Mail
from flask.cli import with_appcontext
from .models import User, Band, Follow
from flask import url_for, current_app
import pickle
from threading import Thread


#Run with 'flask init-db'
#To remake db with new columns delete current
# db sqlite file and run
@click.command('init-db')
@with_appcontext
def init_db_command():
    db.create_all()
    click.echo('Initialized the database.')


@click.command('write-db')
@with_appcontext
def write_db_command():
	band = db.session.query(Band).all()
	users = db.session.query(User).all()
	follows = db.session.query(Follow).all()

	with open('./dbContents.txt', 'w') as f:
		f.write('Band:')
		for i in band:
			dateStr = i.newest_date.isoformat()
			f.write('\tId: %s\t Name: %s\tNewest Track: %s' % (i.id, i.name, dateStr))
		f.write('\n\n')
		f.write('User:')
		for j in users:
			dateStr = j.last_login.isoformat()
			f.write('\tId: %s\t Name: %s\t Last Login: %s' % (j.id, j.email, dateStr))
		f.write('\n\n')
		f.write('Follow:')
		for k in follows:
			f.write('\tFollower: %s\tBand: %s' % 
				(k.follower_id, k.band_following_id))
	click.echo('Wrote databases contents to "dbContents.txt".')


'''
	Untested
	First Go to Endpoint main.getURL
'''
@click.command('update-db')
@with_appcontext
def update_db_command():
	sp = Spotify()
	#Spotify takes a max of 50 artists API Batch Requests
	PER_PAGE = 49
	users_to_notify = set()
	page = 1
	pagination = db.session.query(Band).paginate(page, per_page=PER_PAGE)
	check_releases(sp, pagination.items, users_to_notify)
	while pagination.has_next:
		page += 1
		pagination = db.session.query(Band).paginate(page, per_page=PER_PAGE)
		check_releases(sp, pagination.items, users_to_notify)
	with open('./urls.txt', 'rb') as f:
		urls = pickle.load(f)
	mail = Mail(current_app.config['SECRET_KEY'], 
				current_app.config['SERVER_EMAIL'], 
				urls['unsubscribe'], 
				urls['updates'], 
				urls['info'])
	threads = []
	for i in users_to_notify:
		t = Thread(target=email_user, args=(i, mail))
		threads.append(t)
		t.start()
	for j in threads:
		j.join()
	mail.quit()
	db.session.commit()
	click.echo('Updated Database and sent emails to all users with new releases.')


def check_releases(spotify, bands, users_to_notify):
	for i in bands:
		updatedBand = spotify.getArtist(i.uri)
		click.echo(str(updatedBand['newest_track']['uri']))
		if updatedBand['newest_track']['uri'] != i.newest_uri:
			users_following=db.session.query(User).filter(Band.id==i.id).all()
			click.echo(str(users_following))
			for j in users_following:
				notify = j.ping(i.newest_date, i.newest_uri)
				if notify:
					users_to_notify.add(j)
		i.updateBand(updatedBand)


def email_user(user, mail):
	user.last_login = date.today()
	mail.sendUpdateEmail(user.email)



'''
	When in final deployment enter urls
'''
@click.command('make-urls')
def make_urls():
	'''
	urls = {'unsubscribe':url_for('auth.unsubscribe'),
			'info':url_for('main.info'),
			'updates':url_for('main.updates'),
			'guitar':url_for('static', filename='icons/guitar-white.png'),
			'anonymous':url_for('static', filename='icons/profile-icon.png')}
	'''
	urls = {}
	with open('./urls.txt', 'wb') as f:
		pickle.dump(urls, f)
	click.echo('Made pcikled dictionary of URLs at "urls.txt"')


def init_app(app):
	app.cli.add_command(init_db_command)
	app.cli.add_command(write_db_command)
	app.cli.add_command(update_db_command)
	app.cli.add_command(make_urls)


