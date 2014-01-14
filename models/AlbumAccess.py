class AlbumAccess:
	def __init__(self, album_id, username):
		self.album_id = album_id
		self.username = username

	@staticmethod
	def new(album, user, db):
		cursor = db.cursor()
		cursor.execute("INSERT INTO AlbumAccess (albumid, username) VALUES (%s, %s)", (str(album.id), str(user.id)))
		db.commit()

	def revoke(self, db):
		cursor = db.cursor()
		cursor.execute("DELETE FROM AlbumAccess WHERE albumid = %s AND username = %s", (str(self.album_id), self.username))
		db.commit()

	@classmethod
	def get(cls, user, album, db):
		rValue = None

		cursor = db.cursor()

		cursor.execute("SELECT albumid, username FROM AlbumAccess WHERE albumid = %s AND username = %s", (str(album.id), str(user.id)))

		data = cursor.fetchone()
		if data:
			rValue = cls(data[0], data[1])

		return rValue

	@classmethod
	def get_list_by_album(cls, album, db):
		rValue = []

		cursor = db.cursor()

		cursor.execute("SELECT albumid, username FROM AlbumAccess WHERE albumid = %s", (str(album.id), ))

		while True:
			data = cursor.fetchone()
			if data:
				rValue.append(cls(data[0], data[1]))
			else:
				break

		return rValue

	@classmethod
	def get_list_by_user(cls, user, db):
		rValue = []

		cursor = db.cursor

		cursor.execute("SELECT albumid, username FROM AlbumAccess WHERE username = %s", (str(user.id), ))

		while True:
			data = cursor.fetchone()
			if data:
				rValue.append(cls(data[0], data[1]))
			else:
				break

		return rValue
		
