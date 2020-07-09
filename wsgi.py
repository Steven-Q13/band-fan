import app as a
#Start with gunicorn --bind 0.0.0.0:5000 wsgi:app
app = a.create_app()
