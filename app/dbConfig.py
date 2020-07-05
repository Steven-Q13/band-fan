from . import db
import click
from flask.cli import with_appcontext
from .models import User, Band, Follow


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
	band = Band.query.all()
	users = User.query.all()
	follows = Follow.query.all()

	with open('./dbContents.txt', 'w') as f:
		f.write('Band:')
		for i in band:
			f.write('\tId: %s\t Name: %s' % (i.id, i.name))
		f.write('\n\n')
		f.write('User:')
		for j in users:
			f.write('\tId: %s\t Name: %s' % (j.id, j.email))
		f.write('\n\n')
		f.write('Follow:')
		for k in follows:
			f.write('\tFollower: %s\tBand: %s' % 
				(k.follower_id, k.band_following_id))
	click.echo('Wrote databases contents to "dbContents.txt".')


'''
	Fill out to update all the bands in db with new track/release info
'''
@click.command('update-db')
@with_appcontext
def update_db_command():
	click.echo('Did not update database contents')
	pass


def init_app(app):
	app.cli.add_command(init_db_command)
	app.cli.add_command(write_db_command)
	app.cli.add_command(update_db_command)