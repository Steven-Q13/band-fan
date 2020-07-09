from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from . import main
from .. import db
from ..models import User, Band, Follow
from .forms import SearchForm
from ..api_calls import Spotify
from datetime import date
import pickle


@main.route('/', methods=['GET'])
def index():
    return render_template('main/index.html')


@main.route('/info', methods=['GET'])
def info():
	return render_template('main/info.html')


@main.route('/search', methods=['GET', 'POST'])
def search():
	form = SearchForm()
	if form.validate_on_submit():
		artists = Spotify().spotifySearch(form.search.data)
		if not artists:
			flash('No results for "%s".  Try a different search term.' % 
				form.search.data)
		session['results'] = artists 
		return redirect(url_for('.search'))
	results = session.pop('results', None)
	return render_template('main/search.html', form=form, results=results)


@main.route('/band/<bandID>', methods=['GET', 'POST'])
def band(bandID):
	artistInfo = artistDict(bandID)

	follows_band = False
	if 'dbID' in artistInfo:
		dbID = artistInfo['dbID']
		if current_user.is_logged_in and Follow.query.filter_by(follower_id=current_user.id,
			band_following_id=dbID).first():
			follows_band = True
		
		'''
		follows_check = Follow.query.filter_by(follower_id=current_user.id,
			band_following_id=dbID).first()
		if follows_check:
		'''

	return render_template('main/band.html', info=artistInfo, 
		follows_band=follows_band)


@main.route('/addBand/<bandID>', methods=['GET'])
@login_required
def addBand(bandID):
	artistInfo = artistDict(bandID)
	if 'dbID' in artistInfo:
		dbID = artistInfo['dbID'] 
	else:
		band = Band(uri=artistInfo['artist']['uri'])
		band.updateBand(artistInfo)
		db.session.add(band)
		db.session.commit()
		db.session.refresh(band)
		dbID = band.id
	current_user.follow(dbID)
	db.session.commit()
	flash('You are now following %s' % artistInfo['artist']['name'])
	return redirect(url_for('main.following'))


@main.route('/removeBand/<bandID>', methods=['GET'])
@login_required
def removeBand(bandID):
	artistInfo = artistDict(bandID)
	if 'dbID' in artistInfo:
		dbID = artistInfo['dbID']
		current_user.unfollow(dbID)
		db.session.commit()
	flash('You are no longer following %s' % artistInfo['artist']['name'])
	return redirect(url_for('main.following'))


@main.route('/following', methods=['GET'])
@login_required
def following(): 
	page = request.args.get('page', 1, type=int)
	pagination = db.session.query(Band).filter(User.id == current_user.id).order_by(Band.newest_date.desc()).paginate(page, per_page=8)
	bands = []
	for i in pagination.items:
		bands.append(i.bandDict())

	return render_template('main/following.html', bands=bands, 
		pagination=pagination)


@main.route('/updates', methods=['GET'])
@login_required
def updates():
	last_login = date.fromisoformat(session['last_login']) if 'last_login' in session else date.today()
	page = request.args.get('page', 1, type=int)
	pagination = db.session.query(Band).filter(User.id == current_user.id, Band.newest_date >= last_login).order_by(Band.newest_date.desc()).paginate(page, per_page=8)
	new_releases = []
	for i in pagination.items:
		new_releases.append(i.bandDict())

	return render_template('main/updates.html', bands=new_releases, 
		pagination=pagination)


def artistDict(id):
	artist = Band.query.filter_by(uri=id).first()
	if artist:
		return artist.bandDict()
	return Spotify().getArtist(id)


'''
	Delete
'''
@main.route('/dateChangeUser', methods=['GET'])
@login_required
def dateChangeUser():
	current_user.last_login = date.fromisoformat('2016-06-27')
	db.session.commit()
	return redirect(url_for('main.index'))

'''
	Delete
'''
@main.route('/changeBandURI', methods=['GET'])
def changeBandURI():
	band = db.session.query(Band).first()
	band.newest_uri = 12345
	db.session.commit()
	return redirect(url_for('main.index'))


'''
	Delete
'''
@main.route('/changeUserURI', methods=['GET'])
@login_required
def changeUserURI():
	current_user.latest_song_uri = 1234
	db.session.commit()
	return redirect(url_for('main.index'))
