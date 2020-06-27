from . import db
import click
from flask.cli import with_appcontext


#Run with 'flask init-db'
#To remake db with new columns delet current
# db sqlite file and run
@click.command('init-db')
@with_appcontext
def init_db_command():
    db.create_all()
    click.echo('Initialized the database.')


def init_app(app):
    app.cli.add_command(init_db_command)