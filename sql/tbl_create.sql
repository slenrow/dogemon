CREATE TABLE User (
 username VARCHAR(20),
 password VARCHAR(20),
 firstname VARCHAR(20),
 lastname VARCHAR(20),
 email VARCHAR(40),
 PRIMARY KEY (username));

CREATE TABLE Photo (
 picid VARCHAR(40),
 format CHAR(3),
 date DATETIME,
 url VARCHAR(255),
 PRIMARY KEY (picid),
 UNIQUE KEY (url)
);

CREATE TABLE Album (
 albumid INTEGER AUTO_INCREMENT,
 username VARCHAR(20),
 title VARCHAR(50),
 created DATETIME,
 lastupdated DATETIME,
 access ENUM('public', 'private'),
 PRIMARY KEY (albumid),
 FOREIGN KEY (username) REFERENCES User(username) ON DELETE CASCADE
);

CREATE TABLE Contain (
 albumid INTEGER,
 picid VARCHAR(40),
 caption VARCHAR(255),
 sequencenum INTEGER AUTO_INCREMENT,
 PRIMARY KEY (picid),
 UNIQUE KEY (sequencenum),
 FOREIGN KEY (albumid) REFERENCES Album(albumid) ON DELETE CASCADE,
 FOREIGN KEY (picid) REFERENCES Photo(picid) ON DELETE CASCADE
);

CREATE TABLE AlbumAccess (
 albumid INTEGER,
 username VARCHAR(20),
 PRIMARY KEY (albumid, username),
 FOREIGN KEY (albumid) REFERENCES Album(albumid) ON DELETE CASCADE,
 FOREIGN KEY (username) REFERENCES User(username) ON DELETE CASCADE
);