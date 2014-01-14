from uuid import uuid4

class User:
	def __init__(self, username, password, firstname, lastname, email):
		self.id = username
		self.password = password
		self.firstname = firstname
		self.lastname = lastname
		self.email = email

	@staticmethod
	def get_all(db):
		rValue = []
		cursor = db.cursor()

		cursor.execute("SELECT * FROM User ORDER BY username ASC")

		while True:
			data = cursor.fetchone()
			if data:
				rValue.append(data[0])
			else:
				break

		return rValue

	@classmethod
	def login(cls, username, password, db):
		rValue = None

		cursor = db.cursor()
		cursor.execute("SELECT username, password, firstname, lastname, email FROM User WHERE username = %s AND password = %s", (str(username), str(password)))

		data = cursor.fetchone()
		if data:
			rValue = cls(data[0], data[1], data[2], data[3], data[4])

		return rValue

	@classmethod
	def get(cls, username, db):
		rValue = None

		cursor = db.cursor()
		cursor.execute("SELECT username, password, firstname, lastname, email FROM User WHERE username = %s", (str(username),))

		data = cursor.fetchone()
		if data:
			rValue = cls(data[0], data[1], data[2], data[3], data[4])

		return rValue

	@staticmethod
	def new(username, password, firstname, lastname, email, db):
		rValue = None

		cursor = db.cursor()
		cursor.execute("INSERT INTO User (username, password, firstname, lastname, email) VALUES (%s, %s, %s, %s, %s)", (str(username), str(password), str(firstname), str(lastname), str(email)))
		db.commit()
		rValue = User.get(username, db)
		return rValue

	@staticmethod
	def update(username, password, firstname, lastname, email, db):
		cursor = db.cursor()
		cursor.execute("UPDATE User SET password=%s, firstname=%s, lastname=%s, email=%s WHERE username=%s", (str(password), str(firstname), str(lastname), str(email), str(username)))
		db.commit()

	def delete(self, db):
		cursor = db.cursor()
		cursor.execute("DELETE FROM User WHERE username=%s", (str(self.id),))
		db.commit()

	def reset_pw(self, db):
		self.password = "g21_" + str(uuid4().hex)[:7]
		cursor = db.cursor()
		cursor.execute("UPDATE User set password = %s WHERE username = %s", (self.password, self.id))
		db.commit()
