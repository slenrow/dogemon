import MySQLdb as sql
from functools import wraps
from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
from flask import session
from flask import app
from flask import g

from models.Photo import Photo
from models.Album import Album
from models.User import User
from models.AlbumPhoto import AlbumPhoto
from models.AlbumAccess import AlbumAccess

from time import time
from email.utils import parseaddr
import re

from flask_mail import Mail
from flask_mail import Message


'''
CONF = {
	'host': 'localhost',
	'user': 'group21',
	'pass': 'ducksauce',
	'data': 'group21',
	'uploads': '/Users/kompreni/dogemon/static/pictures/',
	'root': ''
}

def tablize_photos(photos):
	rValue = []

	for i in range(0, len(photos)):
		if i % 4 == 0:
			rValue.append([])
		rValue[len(rValue) - 1].append(photos[i])
	return rValue

def get_whistle():
	return sql.connect(CONF['host'], CONF['user'], CONF['pass'], CONF['data'])

def login_required(f):
	@wraps(f)
	def decorated_login(*args, **kwargs):
		if not g.user['active']:	
			if g.user['logged_in']:
				return redirect(url_for('login', redirect_url=request.url, logged_in=1))
			else:
				return redirect(url_for('login', redirect_url=request.url, logged_in=0))
		return f(*args, **kwargs)
	return decorated_login

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = CONF['uploads']
app.secret_key = '\xe6\xb0\xd4l\xe7(\xb7\xa0\x90\xb4\x14\xf3 \xc6\x8b\x14P\xd3%\xd9c\x1a4\xe1'
app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = '485group21@gmail.com',
	MAIL_PASSWORD = 'ducksauce',
	HOST = '0.0.0.0'
)

mail = Mail(app)

def kill_session():
	if 'username' in session:
		session.pop('username')

	if 'lastactivity' in session:
		session.pop('lastactivity')

def start_session(username):
	session['lastactivity'] = int(time())
	session['username'] = username
	g.user = {
		'logged_in': True,
		'active': True
	}

def check_user(f):
	@wraps(f)
	def decorated_user(*args, **kwargs):
		if 'username' in session and 'lastactivity' in session:
			last_time = session['lastactivity']
			current_time = int(time())

			time_diff = current_time - last_time 
			max_time = 300 #seconsds / 5 minutes

			if time_diff > max_time:
				g.user = {
					'logged_in': True,
					'active': False
				}
				session.pop('username', None)
				session.pop('lastactivity', None)
			else:
				session['lastactivity'] = current_time
				g.user = {
					'logged_in': True,
					'active': True
				}
		else:
			g.user = {
				'logged_in': False,
				'active': False
			}
		return f(*args, **kwargs)

	return decorated_user

@app.route(CONF['root']+'/')
@check_user
def homepage():
	db = get_whistle()

	usernames = User.get_all(db)
	
	current_user = None
	user = None

	if g.user['active']:
		current_user = session['username']
		user = User.get(current_user, db)

	user_albums = []
	usernames = User.get_all(db)

	for username in usernames:
		user_albums.append((username,[]))
		albums = Album.get_albums_by_user(username, db)
		for album in albums:
			if album.access == 'private' and user:
				album_access = AlbumAccess.get(user, album, db)
				if album_access:
					user_albums[len(user_albums) - 1][1].append(album)
			elif album.access == 'public':
				user_albums[len(user_albums) - 1][1].append(album)

	header = render_template('header.html', current_user=current_user, message=None, docroot=CONF['root'])
	return render_template('index.html', user_albums_list=user_albums, header=header, docroot=CONF['root'])

@app.route(CONF['root']+'/album')
@check_user
def browse_album():

	album_id = request.args.get('id')
	db = get_whistle()
	album = Album.get(album_id, db)

	user = None
	current_user = None
	if g.user['active']:
		user = User.get(session['username'], db)
		current_user = user.id

	if album:
		if album.access == 'private':
			if user:
				album_access = AlbumAccess.get(user, album, db)
				if album.username != user.id and not album_access:
					return "Access denied"
			else:
				return redirect(url_for('login', redirect_url=request.url))

		photo_ids = AlbumPhoto.get_album_photo_ids(album, db)
		photos = Photo.get_list(photo_ids, db)
		header = render_template('header.html', current_user=current_user, message=None, docroot=CONF['root'])
		return render_template('viewAlbum.html', album=album, photos=photos, header=header, docroot=CONF['root'])

	else:
		return "Album not found"

@app.route(CONF['root']+'/album/edit', methods=['GET', 'POST'])
@check_user
@login_required
def edit_album():

	db = get_whistle()
	
	user = User.get(session['username'], db)
	
	album_id = request.args.get('id')
	if not album_id:
		return "Album ID not given"

	album = Album.get(album_id, db)
	if not album:
		return "Album not found"

	message = None

	if not album:
		message = "Album not found"

	elif album and album.username != user.id:
		message = "Not authorized to edit album"

	elif request.method == 'POST':
		operation = request.form['op']

		if operation == "add":

			file = request.files['photo']
			if file:

				caption = request.form['caption']

				photo = Photo.new(file, CONF['uploads'], db)
				AlbumPhoto.new(album, photo, caption, db)
				album.update(db)
				message = "Photo successfully added"

			else:
				message = "Unable to process photo"

		elif operation == "delete":
			photo_id = request.form['picid']
			photo = Photo.get(photo_id, db)
			if photo:
				photo.delete(db)
				album.update(db)
				message = "Photo successfully deleted"
			else:
				message = "Unable to delete photo"

		elif operation == "grant":
			friend = request.form['username']
			friend = User.get(friend, db)

			if album and friend:
				album_access = AlbumAccess.get(friend, album, db)
				if album_access:
					message = "User already has album privileges"
				else:
					AlbumAccess.new(album, friend, db)
					album.update(db)
					message = "Successfully shared with user"
			else:
				message = "Unable to share with user"

		elif operation == "revoke":
			friend = request.form['username']
			friend = User.get(friend, db)

			if album and album.access == "private":
				album_access = AlbumAccess.get(friend, album, db)
				if album_access:
					album_access.revoke(db)
					album.update(db)
					message = "Permission successfully revoked"
				else:
					message = "Unable to revoke permission"

			else:
				message = "Nothing changed"

		elif operation == "adjust":
			access = request.form['access']
			if album.access != access:
				album.update(db)
				message = "Privacy successfully changed"
				if access == 'public':
					album_access_list = AlbumAccess.get_list_by_album(album, db)
					for aa in album_access_list:
						aa.revoke(db)
					album.set_access('public', db)
				elif access == 'private':
					AlbumAccess.new(album, user, db)
					album.set_access('private', db)
			else:
				return "Nothing changed"

		else:
			message = "Operation not recognized"

	photo_ids = AlbumPhoto.get_album_photo_ids(album, db)
	photos = Photo.get_list(photo_ids, db)
	aal = []
	album_access_list = AlbumAccess.get_list_by_album(album, db)
	for album_access in album_access_list:
		if user.id != album_access.username:
			aal.append(album_access)

	header = render_template('header.html', current_user=user.id, message=message, docroot=CONF['root'])
	return render_template('editAlbum.html', header=header, album=album, photos=photos, album_access_list=aal, docroot=CONF['root'])

@app.route(CONF['root']+'/albums')
@check_user
def browse_albums():
	username = request.args.get('username')
	db = get_whistle()
	owner = User.get(username, db)
	current_user = None

	if owner:
		album_list = Album.get_albums_by_user(owner.id, db)
		if g.user['active']:
			user = User.get(session['username'], db)
			current_user = user.id
			if user.id == owner.id:
				albums = album_list
			else:
				albums = []
				for album in album_list:
					if album.access == 'public':
						albums.append(album)
					else:
						album_access = AlbumAccess.get(user, album, db)
						if album_access:
							albums.append(album)
		else:
			albums = []
			for album in album_list:
				if album.access == 'public':
					albums.append(album)

		header = render_template('header.html', current_user=current_user, message=None, docroot=CONF['root'])
		return render_template('viewAlbumList.html', username=username, albums=albums, header=header, docroot=CONF['root'])
	else:
		return "User not found"

@app.route(CONF['root']+'/albums/edit', methods=['GET', 'POST'])
@check_user
@login_required
def edit_albums():
	
	db = get_whistle()
	
	user = User.get(session['username'], db)

	message = None

	if request.method == 'POST':
		operation = request.form['op']

		if operation == 'add':
			title = request.form['title']
			access = request.form['access']
			Album.new(user.id, title, access, db)
			message = "Album successfully created"

		elif operation == 'delete':
			album_id = request.form['albumid']
			album = Album.get(album_id, db)

			if album and album.username == user.id:
				photo_ids = AlbumPhoto.get_album_photo_ids(album, db)		
				photos = Photo.get_list(photo_ids, db)
		
				for i in range(0, len(photos)):
					photos[i].delete(db)
	
				album.delete(db)
				message = "Album successfully deleted"
			else:
				return "You can only delete your own albums, silly juice"
		else:
			return "404"

	albums = Album.get_albums_by_user(user.id, db)
	header = render_template('header.html', current_user=user.id, message=message, docroot=CONF['root'])
	return render_template('editAlbumList.html', username=user.id, albums=albums, header=header, docroot=CONF['root'])

@app.route(CONF['root']+'/pic')
@check_user
def view_photo():
	pic_id = request.args.get('id')
	db = get_whistle()

	current_user = None

	if g.user['active']:
		user = User.get(session['username'], db)
		current_user = user.id

	album_photo = AlbumPhoto.get(pic_id, db)

	if album_photo:
		album = Album.get(album_photo.album_id, db)
		if album.access == "private":
			if not g.user['active']:
				return redirect(url_for('login', redirect_url=request.url))

			album_access = AlbumAccess.get(user, album, db)
			if not album_access:
				return "Access denied"

		photo = Photo.get(pic_id, db)
		header = render_template('header.html', current_user=current_user, message=None, docroot=CONF['root'])
		return render_template('viewPic.html', ap=album_photo, album=album, photo=photo, header=header, docroot=CONF['root'])

	else:
		return "No Photo"

@app.route(CONF['root']+'/user', methods=['GET','POST'])
@check_user
def add_user():
	if g.user['active']:
		return redirect(url_for('edit_user'))

	first_name = ""
	last_name = ""
	username = ""
	email = "" 

	message = ""

	if request.method == 'POST':
		db = get_whistle()

		username = str(request.form['username'])
		password = str(request.form['password'])
		password_repeat = str(request.form['password_repeat'])
		first_name = str(request.form['first_name'])
		last_name = str(request.form['last_name'])
		email = str(request.form['email'])
	
		password_regex = re.compile(r"^.*(?=.{5,15})(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9_]*$")
		username_regex = re.compile(r"^[A-Za-z0-9_]{3,20}$")

		if User.get(username, db):
			message = "Username already taken"
		elif password != password_repeat:
			message = "Passwords do not match"
		elif parseaddr(email)[1] == "":
			message = "Invalid email"
		elif not username_regex.match(username):
			message = "Invalid username"
		elif not password_regex.match(password):
			message = "Invalid password"
		else:
			user = User.new(username, password, first_name, last_name, email, db)
			start_session(user.id)
			try:
				msg = Message("Group 21's Photo Gallery - Registration Confirmation", sender=("Group 21", "485group21@gmail.com"), recipients=[email])
				msg.body = render_template('userRegistration.html', username=username, password=password)
				mail.send(msg)
			except:
				pass

			return redirect(url_for('homepage'))

	header = render_template('header.html', current_user=None, message=message, docroot=CONF['root'])
	return render_template('editUserList.html', username=username, first_name=first_name, last_name=last_name, email=email, header=header, docroot=CONF['root'])

@app.route(CONF['root']+'/user/edit', methods=['GET', 'POST'])
@check_user
@login_required
def edit_user():
	db = get_whistle()

	user = User.get(session['username'], db)

	first_name = user.firstname
	last_name = user.lastname
	username = user.id
	email = user.email

	message = None

	if request.method == 'POST':

		first_name = request.form['first_name']
		last_name = request.form['last_name']
		username = user.id
		email = request.form['email']

		old_password = request.form['old_password']
		new_password = request.form['new_password']
		new_password_repeat = request.form['new_password_repeat']

		if user.password != old_password:
			message = "Invalid Password!"

		if new_password != new_password_repeat:
			message = "New password does not match!"	

		else:
			if new_password == "":
				new_password = old_password
			db = get_whistle()
			User.update(username, new_password, first_name, last_name, email, db)
			message = "Profile successfully updated"

	header = render_template('header.html', current_user=user.id, message=message, docroot=CONF['root'])
	return render_template('editUser.html', first_name=first_name, last_name=last_name, username=username, email=email, header=header, docroot=CONF['root'])

@app.route(CONF['root']+'/user/forgot', methods=['GET', 'POST'])
@check_user
def reset_user_pw():
	message = None

	if g.user['active']:
		return redirect(url_for('homepage'))

	elif request.method == 'POST':
		db = get_whistle()
		username = request.form['username']
		user = User.get(username, db)
		if user:
			user.reset_pw(db)
			message = "An email has been sent containing instructions on how to access you account"
			try:
				msg = Message("Group 21's Photo Gallery - Forgotten Password", sender=("Group 21", "485group21@gmail.com"), recipients=[user.email])
				msg.body = render_template('userRegistration.html', username=user.id, password=user.password)
				mail.send(msg)
			except:
				pass
		else:
			message = "User not found"

	header = render_template('header.html', current_user=None, message=message, docroot=CONF['root'])
	return render_template('forgotUser.html', header=header, docroot=CONF['root'])

@app.route(CONF['root']+'/user/delete', methods=['POST'])
@check_user
@login_required
def delete_user():
	db = get_whistle()
	user = User.get(session['username'], db)

	albums = Album.get_albums_by_user(user.id, db)
	for album in albums:
		photo_ids = AlbumPhoto.get_album_photo_ids(album, db)
		photos = Photo.get_list(photo_ids, db)
		
		for i in range(0, len(photos)):
			photos[i].delete(db)

	user.delete(db)
	kill_session()
	return redirect(url_for('homepage'))

@app.route(CONF['root']+'/login',  methods=['GET', 'POST'])
@check_user
def login(redirect_url=None):
	if g.user['active'] and g.user['logged_in']:
		return redirect(url_for('homepage'))

	elif request.method == 'POST':

		username = request.form['username']
		password = request.form['password']
		redirect_url = request.form['redirect_url']
	
		db = get_whistle()
		user = User.login(username, password, db)

		if user:
			start_session(user.id)
			return redirect(redirect_url)
		else:
			header = render_template('header.html', current_user=None, message=None, docroot=CONF['root'])
			return render_template('login.html', error="Invalid username or password", redirect_url=redirect_url, header=header, docroot=CONF['root'])

	else:
		
		logged_in = request.args.get('logged_in')
		redirect_url = request.args.get('redirect_url')
		header = render_template('header.html', current_user=None, message=None, docroot=CONF['root'])
		if redirect_url:
			return render_template('login.html', error=None, redirect_url=redirect_url, logged_in=logged_in, header=header, docroot=CONF['root'])
		else:
			return render_template('login.html', error=None, redirect_url=url_for('homepage'), logged_in=logged_in, header=header, docroot=CONF['root'])

@app.route(CONF['root']+'/logout')
@check_user
def logout():
	kill_session()
	return redirect(url_for('homepage'))
'''
######################################################################################

app = Flask(__name__)
app.config.update(
	DEBUG=True
)

#	Returns the BTC balance of the current user
def get_balance():
	return "-"

#	Sends payment from address
#	Address must be associated with account
@app.route('/send')
def send():
	return "send"
#	Generates an address
#	Shows receive history
#	Associates address with account
@app.route('/receive')
def receive():
	return "rec"

@app.route('/transactions')
def transactions():
	return "txn"

@app.route('/')
def home():
	return "YOURE ON THE HOMEPAGE. KINNARD IS A FUCKER"

if __name__ == '__main__':
	app.run(host='127.0.0.1')