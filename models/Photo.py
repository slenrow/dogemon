from uuid import uuid4
import os

class Photo:
	def __init__(self, pic_id, filetype, date, url):
		self.id = pic_id
		self.filetype = filetype
		self.date = date
		self.url = url

	@classmethod
	def get(cls, pic_id, db):
		rValue = None
		
		cursor = db.cursor()
		
		cursor.execute("SELECT picid, format, date, url FROM Photo WHERE picid = %s ", (pic_id,))

		data = cursor.fetchone()
		if data:
			rValue = cls(data[0], data[1], data[2], data[3])

		return rValue

	@classmethod
	def get_list(cls, pic_ids, db):
		rValue = []

		for i in range(0, len(pic_ids)):
			photo = cls.get(pic_ids[i], db)
			if photo:
				rValue.append(photo)

		return rValue

	@staticmethod
	def new(file, base_dir, db):
		rValue = None

		filename = file.filename
		fn = str(filename).split('.')
		filetype = fn[len(fn) - 1][:3]
		pic_id = str(uuid4().hex)
		path = base_dir + '/' + pic_id + '.' + filetype

		cursor = db.cursor()
		cursor.execute("INSERT INTO Photo (picid, format, date, url) VALUES (%s, %s, NOW(), %s)", (pic_id, filetype, path))
		db.commit()

		rValue = Photo.get(pic_id, db)

		if rValue:
			file.save(path)

		return rValue

	def delete(self, db):
		cursor = db.cursor()
		cursor.execute("DELETE FROM Photo WHERE picid = %s", (self.id,))
		db.commit()

		os.remove(self.url)
		