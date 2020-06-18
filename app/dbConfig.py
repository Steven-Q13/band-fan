from . import db
import click
from flask.cli import with_appcontext


@click.command('init-db')
@with_appcontext
def init_db_command():
    db.create_all()
    click.echo('Initialized the database.')


def init_app(app):
    app.cli.add_command(init_db_command)