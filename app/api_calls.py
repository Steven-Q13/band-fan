import spotipy
from datetime import date
from spotipy.oauth2 import SpotifyClientCredentials
from flask import url_for

import email.message
import smtplib
import re
import pickle


class Spotify:
	def __init__(self):
		client_credentials_manager = SpotifyClientCredentials()
		self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
 

	def getArtist(self, id, default_img=None):
		with open('./urls.txt', 'rb') as f:
			urls = pickle.load(f)
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
			urls['anonymous'], index = 0)

		info['top_track']['name'] = Spotify.shortenName(top_album['name'])
		info['top_track']['uri'] = top_album['uri']
		info['top_track']['date'] = top_album['album']['release_date']
		info['top_track']['img'] = Spotify.getImg(
			top_album['album']['images'], urls['guitar'])

		info['newest_track']['name'] = Spotify.shortenName(
			newest_album['name'])
		info['newest_track']['date'] = newest_album['release_date']
		info['newest_track']['uri'] = newest_album['uri']
		info['newest_track']['img'] = Spotify.getImg(newest_album['images'], 
			urls['guitar'])
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


class Mail:
	def __init__(self, password, fromEmail, unsubscribe, updates, info):
		self.unsubscribe = unsubscribe
		self.updates = updates
		self.info = info

		self.server = smtplib.SMTP('smtp.gmail.com: 587')
		self.server.starttls()
		self.msg = email.message.Message()
		self.msg['From'] = fromEmail
		self.server.login(self.msg['From'], password)


	def sendUpdateEmail(self, address):
		self.msg['To'] = address
		self.msg['Subject'] = 'Band-Fan Update'

		with open('./app/static/email/update.html','r') as f:
			html_content = f.read()
		match = re.findall('{{ .*? }}', html_content)
		for i in match:
			#html_content.replace(i, url_for(i[3:-3]))
			if i[3:-3] == 'unsubscribe':
				html_content = html_content.replace(i, self.unsubscribe)
			elif i[3:-3] == 'updates':
				html_content = html_content.replace(i, self.updates)
			else:
				html_content = html_content.replace(i, self.info)

		self.msg.add_header('Content-Type', 'text/html')
		self.msg.set_payload(html_content)
		self.server.sendmail(self.msg['From'], self.msg['To'],self.msg.as_string())


	def sendWelcomeEmail(self, address):
		self.msg['To'] = address
		self.msg['Subject'] = 'Welcome to Band-Fan!'

		with open('./app/static/email/hello.html', 'r') as f:
			html_content = f.read()
		match = re.findall('{{ .*? }}', html_content)
		for i in match:
			#html_content.replace(i, url_for(i[3:-3]))
			if i[3:-3] == 'unsubscribe':
				html_content = html_content.replace(i, self.unsubscribe)
			elif i[3:-3] == 'updates':
				html_content = html_content.replace(i, self.updates)
			else:
				html_content = html_content.replace(i, self.info)
		with open('hello.html', 'w') as f:
			f.write(str(match))
			f.write(html_content)
		self.msg.add_header('Content-Type', 'text/html')
		self.msg.set_payload(html_content)
		self.server.sendmail(self.msg['From'], self.msg['To'],self.msg.as_string())


	def quit(self):
		self.server.quit()
