from config import config
from flask import flask
from flask_moment import Moment
from flask_login import LoginManager
from flask_boostrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
moment = Moment()
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config='default'):
	#init app
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	#init flask extensions
	db.init_app(app)
	moment.init_app(app)
	bootstrap.init_app(app)
	login_manager.init_app(app)

	#Import/implement flask_sslify to handle ssl redirect
	if app.config['SSL_REDIRECT']:
		pass


	#Attach blueprints
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint, url_prefix='/main')

	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprinth, url_prefix='/auth')

	return app