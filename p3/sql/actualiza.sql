-- ACTUALIZAMOS LOS VALORES DE LOS ID'S
SELECT setval('customers_customerid_seq', max(customerid)) FROM customers;
SELECT setval('orders_orderid_seq', max(orderid)) FROM orders;

﻿--BORRAR COLUMNAS QUE NO NECESITAMOS
ALTER TABLE customers DROP COLUMN address2;
ALTER TABLE customers DROP COLUMN zip;
ALTER TABLE customers DROP COLUMN state;
ALTER TABLE customers DROP COLUMN income;
ALTER TABLE customers DROP COLUMN region;
ALTER TABLE customers DROP COLUMN firstname;
ALTER TABLE customers DROP COLUMN lastname;
ALTER TABLE customers DROP COLUMN address1;
ALTER TABLE customers DROP COLUMN city;
ALTER TABLE customers DROP COLUMN country;
ALTER TABLE customers DROP COLUMN creditcardtype;
ALTER TABLE customers DROP COLUMN creditcardexpiration;
ALTER TABLE imdb_actormovies DROP COLUMN ascharacter;
ALTER TABLE imdb_actormovies DROP COLUMN isvoice;
ALTER TABLE imdb_actormovies DROP COLUMN isarchivefootage;
ALTER TABLE imdb_actormovies DROP COLUMN isuncredited;
ALTER TABLE imdb_actormovies DROP COLUMN creditsposition;
ALTER TABLE imdb_directormovies DROP COLUMN participation;
ALTER TABLE imdb_directormovies DROP COLUMN ascharacter;
ALTER TABLE imdb_movielanguages DROP COLUMN extrainformation;

--CREAMOS NUEVAS TABLAS
CREATE TABLE public.languages (
	languageid SERIAL PRIMARY KEY,
	language character varying(50) NOT NULL
);
CREATE TABLE public.genres (
	genreid SERIAL PRIMARY KEY,
	genre character varying(50) NOT NULL
);

CREATE TABLE public.countries (
	countryid SERIAL PRIMARY KEY,
	country character varying(50) NOT NULL
);


--INSERTAR EN LAS TABLAS CREADAS
INSERT INTO languages (language) SELECT DISTINCT language FROM imdb_movielanguages;
INSERT INTO genres (genre) SELECT DISTINCT genre FROM imdb_moviegenres;
INSERT INTO countries (country) SELECT DISTINCT country FROM imdb_moviecountries;


--METER LOS IDS EN LAS TABLAS ANTIGUAS
ALTER TABLE imdb_movielanguages ADD languageid integer NOT NULL DEFAULT 0;
ALTER TABLE imdb_moviegenres ADD genreid integer NOT NULL DEFAULT 0;
ALTER TABLE imdb_moviecountries ADD countryid integer NOT NULL DEFAULT 0;


UPDATE imdb_movielanguages
SET languageid = l.languageid
FROM languages AS l
WHERE l.language = imdb_movielanguages.language;


UPDATE imdb_moviecountries
SET countryid = c.countryid
FROM countries AS c
WHERE c.country = imdb_moviecountries.country;


UPDATE imdb_moviegenres
SET genreid = g.genreid
FROM genres AS g
WHERE g.genre = imdb_moviegenres.genre;


ALTER TABLE imdb_movielanguages DROP COLUMN language;
ALTER TABLE imdb_moviegenres DROP COLUMN genre;
ALTER TABLE imdb_moviecountries DROP COLUMN country;


--CAMBIAR LAS PRIMARY KEY
ALTER TABLE imdb_movielanguages ADD CONSTRAINT imdb_movielanguages_pk PRIMARY KEY (movieid, languageid);
ALTER TABLE imdb_moviecountries ADD CONSTRAINT imdb_moviecountries_pk PRIMARY KEY (movieid, countryid);
ALTER TABLE imdb_moviegenres ADD CONSTRAINT imdb_moviegenres_pk PRIMARY KEY (movieid, genreid);
