import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'rand key'
	SSL_REDIRECT = False
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQL_ALCHEMY_RECORD_QUERIES = True
	SSL_REDIRECT = False
	SLOW_DB_QUERY_TIME = 0.1
	SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
	SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
	POSTS_PER_PAGE = 8
	SERVER_EMAIL = 'bandfan.notifications@gmail.com'

	@staticmethod
	def init_app(app):
		pass


class DevConfig(Config):
	DEBUG = True


class TestingConfig(Config):
	TESTING = True


class HerokuConfig(Config):
	SSL_REDIRECT = True if os.environ.get('DYNO') else False
	SQL_ALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')

	#Used to setup logging
	@classmethod
	def init_app(cls,app):
		pass


class ProductionConfig(Config):

	#Used to setup logging
	@classmethod
	def init_app(cls,app):
		pass


config = {
    'development':DevConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'heroku':HerokuConfig,

    'default':DevConfig
}
