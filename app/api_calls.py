import spotipy
from datetime import date
from spotipy.oauth2 import SpotifyClientCredentials
from flask import url_for

'''
	Do Spotify API batch requests
'''
class Spotify:

	def __init__(self):
		client_credentials_manager = SpotifyClientCredentials()
		self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


	def getArtist(self, id):
		#Each element is a dict of name, uri, img, date(optional)
		info = {'artist':{}, 'top_track':{}, 'newest_track':{}}

		artist = self.sp.artist(id)
		top_album = self.sp.artist_top_tracks(id, country='US')
		top_album = top_album['tracks'][0]
		newest_album = self.sp.artist_albums(id, limit=1)
		newest_album = newest_album['items'][0]

		info['artist']['name'] = Spotify.shortenName(artist['name'])
		info['artist']['uri'] = artist['uri']
		info['artist']['img'] = Spotify.getImg(artist['images'], 
			url_for('static', filename='icons/profile-icon.png'),
			index = 0)

		info['top_track']['name'] = Spotify.shortenName(top_album['name'])
		info['top_track']['uri'] = top_album['uri']
		info['top_track']['date'] = top_album['album']['release_date']
		info['top_track']['img'] = Spotify.getImg(
			top_album['album']['images'], 
			url_for('static', filename='icons/guitar-white.png'))

		info['newest_track']['name'] = Spotify.shortenName(
			newest_album['name'])
		info['newest_track']['date'] = newest_album['release_date']
		info['newest_track']['uri'] = newest_album['uri']
		info['newest_track']['img'] = Spotify.getImg(newest_album['images'], 
			url_for('static', filename='icons/guitar-white.png'))
		return info


	def spotifySearch(self, term):
		query = term.split(' ')
		searchResp = self.sp.search(q=query, type='artist', limit=8)
		searchResp = searchResp['artists']['items']

		artists = {}
		for i in searchResp:
			img = Spotify.getImg(i['images'], url_for('static', 
				filename='icons/guitar-white.png'))
			name = Spotify.shortenName(i['name'])
			artists[name] = [i['uri'], img]
		return artists


	@staticmethod
	def getImg(imgs, default, index=-2):
		img = default
		if len(imgs) >= 2:
			img = imgs[index]['url']
		elif len(imgs) >= 1:
			img = imgs[0]['url']
		return img


	@staticmethod
	def shortenName(name):
		for i in range(len(name)):
			if name[i] == '(':
				name = name[:i]
				break
		return name
