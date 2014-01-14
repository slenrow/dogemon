class AlbumPhoto:
	def __init__(self, album_id, photo_id, caption, prev, next):
		self.prev = prev
		self.next = next
		self.caption = caption
		self.album_id = album_id
		self.id = photo_id

	@classmethod
	def get(cls, photo_id, db):
		rValue = None

		sequencenum = None
		caption = None
		title = None
		prev = None
		next = None

		cursor = db.cursor()

		cursor.execute("SELECT albumid, picid, caption, sequencenum FROM Contain WHERE picid=%s", (photo_id,))
		data = cursor.fetchone()
		if data:
			album_id = data[0]
			photo_id = data[1]
			caption = data[2]
			sequencenum = data[3]

			cursor2 = db.cursor()
			cursor2.execute("SELECT picid FROM Contain WHERE sequencenum < %s and albumid=%s ORDER BY sequencenum DESC LIMIT 0,1", (str(sequencenum), str(album_id)))
			data2 = cursor2.fetchone()
			if data2:
				prev = data2[0]

			cursor3 = db.cursor()
			cursor3.execute("SELECT picid FROM Contain WHERE sequencenum > %s and albumid=%s ORDER BY sequencenum ASC LIMIT 0,1", (str(sequencenum), str(album_id)))
			data3 = cursor3.fetchone()
			if data3:
				next = data3[0]
			rValue = cls(album_id, photo_id, caption, prev, next)
		return rValue

	@staticmethod
	def get_album_photo_ids(album, db):
		rValue = []

		cursor = db.cursor()
		cursor.execute("SELECT picid from Contain WHERE albumid=%s ORDER BY sequencenum ASC", (album.id,))

		while True:
			data = cursor.fetchone()
			if data:
				rValue.append(data[0])
			else:
				break

		return rValue

	@staticmethod
	def new(album, photo, caption, db):
		cursor = db.cursor()
		cursor.execute("INSERT INTO Contain (albumid, picid, caption) VALUES (%s, %s, %s)", (str(album.id), photo.id, caption))
		db.commit()
