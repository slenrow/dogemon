INSERT INTO User (username, password, firstname, lastname, email) VALUES 
 ('sportslover', 'paulpass93', 'Paul', 'Walker', 'sportslover@hotmail.com'), 
 ('traveler', 'rebeccapass15', 'Rebecca', 'Travolta', 'rebt@explorer.org'), 
 ('spacejunkie', 'bob1pass', 'Bob', 'Spacey', 'bspace@spacejunkies.net');

INSERT INTO Album (username, title, created, lastupdated, access) VALUES 
 ('sportslover', 'I love sports', NOW(), NOW(), 'public'), 
 ('sportslover', 'I love football', NOW(), NOW(), 'public'), 
 ('traveler', 'Around The World', NOW(), NOW(), 'public'), 
 ('spacejunkie', 'Cool Space Shots', NOW(), NOW(), 'private');

 INSERT INTO AlbumAccess (albumid, username) VALUES ('4', 'spacejunkie');
 INSERT INTO AlbumAccess (albumid, username) VALUES ('4', 'traveler');
