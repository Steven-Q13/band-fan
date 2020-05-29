import os
import sys
import click

from config import config
from app import create_app, db
from app.models import User

app = create_app(config=os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
	return dict(db=db, User=User, app=app)

@app.cli.command()
def make_db():
	with app.app_context():
		db.create_all()
