from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from . import main
from .. import db
from ..models import User, Band, Follow
from .forms import SearchForm
from ..api_calls import Spotify
from datetime import date


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
		follows_check = Follow.query.filter_by(follower_id=current_user.id,
			band_following_id=dbID).first()
		if follows_check:
			follows_band = True

	return render_template('main/band.html', info=artistInfo, 
		follows_band=follows_band)


@main.route('/addBand/<bandID>', methods=['GET'])
@login_required
def addBand(bandID):
	artistInfo = artistDict(bandID)
	dbID = artistInfo['dbID'] if 'dbID' in artistInfo else makeBandCol(artistInfo)
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
		bands.append(i.colDict())

	return render_template('main/following.html', bands=bands, 
		pagination=pagination)


'''
	Untested
'''
@main.route('/updates', methods=['GET'])
@login_required
def updates():
	last_login = date.fromisoformat(session['last_login']) if 'last_login' in session else date.today()
	page = request.args.get('page', 1, type=int)
	pagination = db.session.query(Band).filter(User.id == current_user.id, Band.newest_date >= last_login).order_by(Band.newest_date.desc()).paginate(page, per_page=8)
	new_releases = []
	for i in pagination.items:
		new_releases.append(i.colDict())

	return render_template('main/updates.html', bands=new_releases, 
		pagination=pagination)

	'''
	following_links = current_user.following.all()
	page = request.args.get('page', 1, type=int)
	pagination = current_user.following.paginate(page, per_page=8, error_out=False)
	following_links = pagination.items
	new_releases = []
	last_login = date.fromisoformat(session['last_login']) if 'last_login' in session else date.today()
	l = current_user.last_login

	for i in following_links:
		band = Band.query.filter_by(id=i.band_following_id).first()

		if band.newest_date >= last_login:
			new_releases.append(band.colDict())

	new_releases.sort(key=lambda new_releases: new_releases['newest_track']['date'])
	new_releases.reverse()
	return render_template('main/updates.html', bands=new_releases, 
		pagination=pagination)
	'''


def artistDict(id):
	artistCol = Band.query.filter_by(uri=id).first()
	if artistCol:
		return artistCol.colDict()
	return Spotify().getArtist(id)


def makeBandCol(bandDict):
	top_date = date.fromisoformat(bandDict['top_track']['date'])
	newest_date = date.fromisoformat(bandDict['newest_track']['date'])

	band = Band(name=bandDict['artist']['name'], 
				img=bandDict['artist']['img'], 
				uri=bandDict['artist']['uri'], 
				top_name=bandDict['top_track']['name'],
				top_img=bandDict['top_track']['img'],
				top_uri=bandDict['top_track']['uri'],
				top_date=top_date,
				newest_name=bandDict['newest_track']['name'],
				newest_img=bandDict['newest_track']['img'],
				newest_uri=bandDict['newest_track']['uri'],
				newest_date=newest_date)
	db.session.add(band)
	db.session.commit()
	return band.id

