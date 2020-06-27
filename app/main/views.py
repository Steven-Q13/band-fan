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


@main.route('/myBands', methods=['GET'])
@login_required
def myBands():
	return render_template('a.html')


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
	return render_template('main/band.html', info=artistInfo)


@main.route('/addBand/<bandID>', methods=['GET'])
@login_required
def addBand(bandID):
	artistInfo = artistDict(bandID)

	followCheck = None
	if 'dbID' in artistInfo:
		dbID = artistInfo['dbID']
		followsCheck = Follow.query.filter_by(follower_id=current_user.id,
			band_following_id=dbID).first()
	else:
		dbID = makeBandCol(artistInfo)

	if followsCheck:
		flash('You are already following %s' % artistInfo['artist']['name'])
		return redirect( url_for('main.addBand', 
			bandID=artistInfo['artist']['uri']))

	follows = Follow(follower_id=current_user.id, 
		band_following_id=dbID)
	db.session.add(follows)
	db.session.commit()
	return redirect(url_for('main/myBands'))


#Temp button in navbar for testing, delete on production
@main.route('/testDB', methods=['GET'])
def testDB():
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
	return redirect( url_for('main.index') )


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

