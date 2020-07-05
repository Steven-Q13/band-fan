import click
from flask import Flask
from config import config
from flask_moment import Moment
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

db = SQLAlchemy()
moment = Moment()
migrate = Migrate()
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name='default'):
	#init app
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	#init flask extensions
	db.init_app(app)
	moment.init_app(app)
	migrate.init_app(app, db)
	bootstrap.init_app(app)
	login_manager.init_app(app)

	#Import/implement flask_sslify to handle ssl redirect
	if app.config['SSL_REDIRECT']:
		pass

	#Attach blueprints
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint, url_prefix='/main')

	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint, url_prefix='/auth')

	from . import dbConfig
	dbConfig.init_app(app)

	return app