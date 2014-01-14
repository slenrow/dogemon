class Album:
	def __init__(self, album_id, username, title, created, updated, access):
		self.id = album_id
		self.username = username
		self.title = title
		self.created = created
		self.updated = updated
		self.access = access

	@classmethod
	def get(cls, album_id, db):
		rValue = None

		cursor = db.cursor()
		cursor.execute("SELECT albumid, username, title, created, lastupdated, access FROM Album WHERE albumid=%s", (str(album_id),))

		data = cursor.fetchone()
		if data:
			rValue = cls(data[0], data[1], data[2], data[3], data[4], data[5])

		return rValue

	@staticmethod
	def new(username, title, access, db):
		rValue = None

		cursor = db.cursor()
		cursor.execute("INSERT INTO Album (username, title, created, lastupdated, access) VALUES (%s, %s, NOW(), NOW(), %s)", (username, str(title), access))
		db.commit()

		return rValue

	@classmethod
	def get_albums_by_user(cls, username, db):
		rValue = []
		cursor = db.cursor()
		cursor.execute("SELECT albumid, username, title, created, lastupdated, access FROM Album WHERE username=%s", (str(username),))
		
		while True:
			data = cursor.fetchone()
			if data:
				rValue.append(cls(data[0], data[1], data[2], data[3], data[4], data[5]))
			else:
				break

		return rValue

	@classmethod
	def get_homepage(cls, user, db):
		rValue = []

		cursor = db.cursor()

		if user:
			cursor.execute("SELECT Album.albumid, Album.username, Album.title, Album.created, Album.lastupdated, Album.access FROM Album, AlbumAccess WHERE (Album.albumid = AlbumAccess.albumid AND AlbumAccess.username = %s) OR (Album.access=%s) ORDER BY Album.username ASC", (str(user.id),'public'))
		else:
			cursor.execute("SELECT albumid, username, title, created, lastupdated, access FROM Album WHERE (access=%s) ORDER BY username ASC", ('public',))

		last_user = ""

		while True:
			data = cursor.fetchone()

			if data and data[1] != last_user:
				rValue.append(data[1],[])
				rValue[len(rValue) - 1][1].append(cls(data[0], data[1], data[2], data[3], data[4], data[5]))
				last_user = data[1]
			elif data:
				rValue[len(rValue) - 1][1].append(cls(data[0], data[1], data[2], data[3], data[4], data[5]))
			else:
				break
		return rValue

	def update(self, db):
		cursor = db.cursor()
		cursor.execute("UPDATE Album SET lastupdated = NOW() WHERE albumid=%s", (str(self.id),))
		db.commit()

	def delete(self, db):
		cursor = db.cursor()
		cursor.execute("DELETE FROM Album WHERE albumid=%s", (str(self.id),))
		db.commit()

	def set_access(self, access_type, db):
		self.access = access_type

		cursor = db.cursor()
		cursor.execute("UPDATE Album SET access = %s WHERE albumid = %s", (self.access, str(self.id)))

		db.commit()
