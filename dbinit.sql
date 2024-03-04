DROP TABLE IF EXISTS ytTracks;
DROP TABLE IF EXISTS ytPlaylists;
DROP TABLE IF EXISTS spTracks;
DROP TABLE IF EXISTS spPlaylists;

CREATE TABLE ytPlaylists(
	id INT AUTO_INCREMENT PRIMARY KEY,
	playlist_id VARCHAR(80) UNIQUE,
	title VARCHAR(80) NOT NULL,
	tracks_count INT,
	`description` VARCHAR(100),
	artwork VARCHAR(300)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE ytTracks(
	id INT AUTO_INCREMENT PRIMARY KEY,
	title VARCHAR(100) NOT NULL,
	duration INT,
	artists VARCHAR(150) NOT NULL,
	album VARCHAR(100),
	playlist_id VARCHAR(80) NOT NULL,
	artwork VARCHAR(300),
	CONSTRAINT track_to_playlist FOREIGN KEY (playlist_id) REFERENCES ytPlaylists(playlist_id) 
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE spPlaylists(
	id INT AUTO_INCREMENT PRIMARY KEY,
	playlist_id VARCHAR(80) UNIQUE,
	title VARCHAR(80) NOT NULL,
	tracks_count INT,
	`description` VARCHAR(100),
	artwork VARCHAR(300)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE spTracks(
	id INT AUTO_INCREMENT PRIMARY KEY,
	title VARCHAR(100) NOT NULL,
	duration INT,
	artists VARCHAR(150) NOT NULL,
	album VARCHAR(100),
	playlist_id VARCHAR(80) NOT NULL,
	artwork VARCHAR(300),
	CONSTRAINT sp_track_to_playlist FOREIGN KEY (playlist_id) REFERENCES spPlaylists(playlist_id) 
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;