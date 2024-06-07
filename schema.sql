DROP TABLE IF EXISTS film;
DROP TABLE IF EXISTS actor;
DROP TABLE IF EXISTS film_actor;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS film_category;
DROP TABLE IF EXISTS user;
CREATE TABLE film (
    film_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    release_year INTEGER,
    length INTEGER
);

CREATE TABLE actor (
    actor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(45) NOT NULL,
    last_name VARCHAR(45) NOT NULL
);

CREATE TABLE film_actor (
    film_actor INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id INTEGER,
    film_id INTEGER,
    FOREIGN KEY (actor_id) REFERENCES actor(actor_id),
    FOREIGN KEY (film_id) REFERENCES film(film_id)
);

CREATE TABLE user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(45) NOT NULL,
    password VARCHAR(45) NOT NULL,
    role VARCHAR(45) NOT NULL default 'user'
);