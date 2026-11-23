-- ============================================================================
--  THEDATABASE.sql — полный дамп базы данных lab_db
--  СУБД: PostgreSQL, схема: lab_schema
--  Создан: 11.11.2026
--
--  Состав: 6 таблиц (developer, game, genre, game_genre, review, log_game),
--          4 представления, 14 функций PL/pgSQL, данные всех таблиц,
--          последовательности, индексы и ограничения целостности.
-- ============================================================================
--
--  ВОССТАНОВЛЕНИЕ В pgAdmin 4:
--    1. Подключитесь к серверу PostgreSQL (обычно пользователь postgres).
--    2. Правой кнопкой по "Databases" -> Create -> Database...
--       В поле Database введите: lab_db
--       (можно создать базу с другим именем, но тогда имя lab_db нужно
--        будет изменить в строке подключения приложений из лаб. 4-5).
--    3. Выберите созданную базу lab_db и откройте Query Tool.
--    4. Нажмите "Open File" (иконка папки) и выберите THEDATABASE.sql.
--    5. Нажмите Execute (F5) и дождитесь сообщения об успешном выполнении.
--
--  ВОССТАНОВЛЕНИЕ ЧЕРЕЗ psql (командная строка):
--    createdb -U postgres -h localhost -p 5432 lab_db
--    psql -U postgres -h localhost -p 5432 -d lab_db -f THEDATABASE.sql
--
--  ВАЖНО:
--    * Данные вставлены командами INSERT, поэтому скрипт можно выполнять
--      не только в psql, но и в pgAdmin Query Tool.
--    * В конце скрипта создаётся роль приложения lab_test (пароль lab_test)
--      и ей выдаются права на схему lab_schema. Это нужно для приложений
--      из лабораторных работ 4 и 5. Блок создания роли выполняется только
--      при наличии прав суперпользователя. Если прав недостаточно,
--      создайте роль и выдайте права вручную:
--        CREATE ROLE lab_test LOGIN PASSWORD 'lab_test';
--        GRANT USAGE ON SCHEMA lab_schema TO lab_test;
--        GRANT SELECT, INSERT, UPDATE, DELETE
--            ON ALL TABLES IN SCHEMA lab_schema TO lab_test;
--        GRANT USAGE, SELECT
--            ON ALL SEQUENCES IN SCHEMA lab_schema TO lab_test;
--        GRANT EXECUTE
--            ON ALL FUNCTIONS IN SCHEMA lab_schema TO lab_test;
-- ============================================================================

--
-- PostgreSQL database dump
--


-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
-- SET transaction_timeout = 0;  -- параметр доступен только в PostgreSQL 17+
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: lab_schema; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA lab_schema;


--
-- Name: t_game; Type: TYPE; Schema: lab_schema; Owner: -
--

CREATE TYPE lab_schema.t_game AS (
	id bigint,
	title character varying(150),
	price numeric(10,2)
);


--
-- Name: delete_game(bigint); Type: FUNCTION; Schema: lab_schema; Owner: -
--

CREATE FUNCTION lab_schema.delete_game(_id bigint) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM lab_schema.log_game WHERE game_id = _id;
    DELETE FROM lab_schema.game WHERE id = _id;
EXCEPTION
    WHEN foreign_key_violation THEN
        RAISE EXCEPTION 'Невозможно удалить игру, так как на неё есть ссылки из других таблиц.';
END;
$$;


--
-- Name: delete_review(bigint); Type: FUNCTION; Schema: lab_schema; Owner: -
--

CREATE FUNCTION lab_schema.delete_review(_id bigint) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM lab_schema.review WHERE id = _id;
EXCEPTION
    WHEN foreign_key_violation THEN
        RAISE EXCEPTION 'Невозможно удалить запись, так как на неё существуют внешние ссылки.';
END;
$$;


--
-- Name: filter_games_array(lab_schema.t_game[], numeric); Type: FUNCTION; Schema: lab_schema; Owner: -
--

CREATE FUNCTION lab_schema.filter_games_array(_arr lab_schema.t_game[], _min_price numeric) RETURNS lab_schema.t_game[]
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN ARRAY(
        SELECT (id, title, price)::lab_schema.t_game
        FROM unnest(_arr)
        WHERE price >= _min_price
    );
END;
$$;


SET default_table_access_method = heap;

--
-- Name: game; Type: TABLE; Schema: lab_schema; Owner: -
--

CREATE TABLE lab_schema.game (
    id bigint NOT NULL,
    title character varying(150) NOT NULL,
    developer_id bigint NOT NULL,
    release_year integer,
    price numeric(10,2),
    is_released boolean DEFAULT false NOT NULL,
    CONSTRAINT game_price_check CHECK ((price >= (0)::numeric)),
    CONSTRAINT game_release_year_check CHECK (((release_year >= 1970) AND (release_year <= 2030)))
);


--
-- Name: filter_games_by_price(numeric); Type: FUNCTION; Schema: lab_schema; Owner: -
--

CREATE FUNCTION lab_schema.filter_games_by_price(_min_price numeric) RETURNS SETOF lab_schema.game
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM lab_schema.game
    WHERE price >= _min_price;
END;
$$;


--
-- Name: filter_games_by_title(character varying); Type: FUNCTION; Schema: lab_schema; Owner: -
--

CREATE FUNCTION lab_schema.filter_games_by_title(_title_pattern character varying) RETURNS TABLE(id bigint, title character varying, developer_name character varying, release_year integer, price numeric, is_released boolean)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT g.id, g.title, d.name, g.release_year, g.price, g.is_released
    FROM lab_schema.game g
    JOIN lab_schema.developer d ON g.developer_id = d.id
    WHERE UPPER(g.title) LIKE UPPER(_title_pattern)
    ORDER BY g.id;
END;
$$;


--
-- Name: filter_reviews_by_reviewer(character varying); Type: FUNCTION; Schema: lab_schema; Owner: -
--

CREATE FUNCTION lab_schema.filter_reviews_by_reviewer(_pattern character varying) RETURNS TABLE(id bigint, game_id bigint, game_title character varying, reviewer_name character varying, score integer, review_date date)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT r.id, r.game_id, g.title, r.reviewer_name, r.score, r.review_date
    FROM lab_schema.review r
    JOIN lab_schema.game g ON r.game_id = g.id
    WHERE UPPER(r.reviewer_name) LIKE UPPER(_pattern)
    ORDER BY r.id;
END;
$$;


--
-- Name: get_all_developers(); Type: FUNCTION; Schema: lab_schema; Owner: -
--

CREATE FUNCTION lab_schema.get_all_developers() RETURNS TABLE(id bigint, name character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT d.id, d.name
    FROM lab_schema.developer d
    ORDER BY d.name;
END;
$$;


--
-- Name: get_all_games_list(); Type: FUNCTION; Schema: lab_schema; Owner: -
--

CREATE FUNCTION lab_schema.get_all_games_list() RETURNS TABLE(id bigint, title character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT g.id, g.title
    FROM lab_schema.game g
    ORDER BY g.title;
END;
$$;


--
-- Name: get_games_with_developers(); Type: FUNCTION; Schema: lab_schema; Owner: -
--

CREATE FUNCTION lab_schema.get_games_with_developers() RETURNS TABLE(id bigint, title character varying, developer_name character varying, release_year integer, price numeric, is_released boolean)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT g.id, g.title, d.name, g.release_year, g.price, g.is_released
    FROM lab_schema.game g
    JOIN lab_schema.developer d ON g.developer_id = d.id
    ORDER BY g.id;
END;
$$;


--
-- Name: get_reviews_with_games(); Type: FUNCTION; Schema: lab_schema; Owner: -
--

CREATE FUNCTION lab_schema.get_reviews_with_games() RETURNS TABLE(id bigint, game_id bigint, game_title character varying, reviewer_name character varying, score integer, review_date date)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT r.id, r.game_id, g.title, r.reviewer_name, r.score, r.review_date
    FROM lab_schema.review r
    JOIN lab_schema.game g ON r.game_id = g.id
    ORDER BY r.id;
END;
$$;


--
-- Name: get_value_by_id(character varying, character varying, bigint); Type: FUNCTION; Schema: lab_schema; Owner: -
--

CREATE FUNCTION lab_schema.get_value_by_id(_table_name character varying, _column_name character varying, _id bigint) RETURNS text
    LANGUAGE plpgsql
    AS $_$
DECLARE
    result TEXT;
BEGIN
    EXECUTE 'SELECT ' || _column_name || ' FROM lab_schema.' || _table_name || ' WHERE id = $1'
    USING _id
    INTO result;
    RETURN result;
END;
$_$;


--
-- Name: log_game_price_trigger(); Type: FUNCTION; Schema: lab_schema; Owner: -
--

CREATE FUNCTION lab_schema.log_game_price_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    old_val NUMERIC(10, 2);
BEGIN
    IF (TG_OP = 'UPDATE') THEN
        old_val := OLD.price;
    ELSIF (TG_OP = 'INSERT') THEN
        old_val := NULL;
    END IF;
    
    INSERT INTO lab_schema.log_game (game_id, old_price, new_price)
    VALUES (NEW.id, old_val, NEW.price);
    
    RETURN NEW;
END;
$$;


--
-- Name: save_game(bigint, character varying, bigint, integer, numeric, boolean); Type: FUNCTION; Schema: lab_schema; Owner: -
--

CREATE FUNCTION lab_schema.save_game(_id bigint, _title character varying, _developer_id bigint, _release_year integer, _price numeric, _is_released boolean) RETURNS bigint
    LANGUAGE plpgsql
    AS $$
DECLARE
    used_id BIGINT;
BEGIN
    -- Проверка на наличие уже имеющихся данных (без учета регистра)
    IF EXISTS (
        SELECT 1 FROM lab_schema.game
        WHERE UPPER(TRIM(title)) = UPPER(TRIM(_title))
          AND (_id IS NULL OR id <> _id)
    ) THEN
        RAISE EXCEPTION 'Игра с названием "%" уже существует в базе данных!', _title;
    END IF;

    IF _id IS NULL THEN
        INSERT INTO lab_schema.game (title, developer_id, release_year, price, is_released)
        VALUES (TRIM(_title), _developer_id, _release_year, _price, _is_released)
        RETURNING id INTO used_id;
    ELSE
        UPDATE lab_schema.game
        SET title = TRIM(_title),
            developer_id = _developer_id,
            release_year = _release_year,
            price = _price,
            is_released = _is_released
        WHERE id = _id;
        used_id := _id;
    END IF;

    RETURN used_id;
END;
$$;


--
-- Name: save_review(bigint, bigint, character varying, integer, date); Type: FUNCTION; Schema: lab_schema; Owner: -
--

CREATE FUNCTION lab_schema.save_review(_id bigint, _game_id bigint, _reviewer_name character varying, _score integer, _review_date date) RETURNS bigint
    LANGUAGE plpgsql
    AS $$
DECLARE
    used_id BIGINT;
BEGIN
    -- Проверка на наличие уже имеющихся данных (отзыв того же автора на ту же игру)
    IF EXISTS (
        SELECT 1 FROM lab_schema.review
        WHERE game_id = _game_id
          AND UPPER(TRIM(reviewer_name)) = UPPER(TRIM(_reviewer_name))
          AND (_id IS NULL OR id <> _id)
    ) THEN
        RAISE EXCEPTION 'Отзыв от пользователя "%" на данную игру уже существует!', _reviewer_name;
    END IF;

    IF _id IS NULL THEN
        INSERT INTO lab_schema.review (game_id, reviewer_name, score, review_date)
        VALUES (_game_id, TRIM(_reviewer_name), _score, _review_date)
        RETURNING id INTO used_id;
    ELSE
        UPDATE lab_schema.review
        SET game_id = _game_id,
            reviewer_name = TRIM(_reviewer_name),
            score = _score,
            review_date = _review_date
        WHERE id = _id;
        used_id := _id;
    END IF;

    RETURN used_id;
END;
$$;


--
-- Name: developer; Type: TABLE; Schema: lab_schema; Owner: -
--

CREATE TABLE lab_schema.developer (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    country character varying(50),
    is_active boolean DEFAULT true NOT NULL
);


--
-- Name: developer_id_seq; Type: SEQUENCE; Schema: lab_schema; Owner: -
--

CREATE SEQUENCE lab_schema.developer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: developer_id_seq; Type: SEQUENCE OWNED BY; Schema: lab_schema; Owner: -
--

ALTER SEQUENCE lab_schema.developer_id_seq OWNED BY lab_schema.developer.id;


--
-- Name: review; Type: TABLE; Schema: lab_schema; Owner: -
--

CREATE TABLE lab_schema.review (
    id bigint NOT NULL,
    game_id bigint NOT NULL,
    reviewer_name character varying(100) NOT NULL,
    score integer NOT NULL,
    review_date date DEFAULT CURRENT_DATE NOT NULL,
    CONSTRAINT review_score_check CHECK (((score >= 1) AND (score <= 10)))
);


--
-- Name: game_avg_rating_v; Type: VIEW; Schema: lab_schema; Owner: -
--

CREATE VIEW lab_schema.game_avg_rating_v AS
 SELECT g.title AS game_title,
    count(r.id) AS review_count,
    round(avg(r.score), 2) AS avg_score
   FROM (lab_schema.game g
     LEFT JOIN lab_schema.review r ON ((g.id = r.game_id)))
  GROUP BY g.id, g.title;


--
-- Name: game_genre; Type: TABLE; Schema: lab_schema; Owner: -
--

CREATE TABLE lab_schema.game_genre (
    id bigint NOT NULL,
    game_id bigint NOT NULL,
    genre_id bigint NOT NULL
);


--
-- Name: game_genre_id_seq; Type: SEQUENCE; Schema: lab_schema; Owner: -
--

CREATE SEQUENCE lab_schema.game_genre_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: game_genre_id_seq; Type: SEQUENCE OWNED BY; Schema: lab_schema; Owner: -
--

ALTER SEQUENCE lab_schema.game_genre_id_seq OWNED BY lab_schema.game_genre.id;


--
-- Name: genre; Type: TABLE; Schema: lab_schema; Owner: -
--

CREATE TABLE lab_schema.genre (
    id bigint NOT NULL,
    name character varying(50) NOT NULL
);


--
-- Name: game_genres_v; Type: VIEW; Schema: lab_schema; Owner: -
--

CREATE VIEW lab_schema.game_genres_v AS
 SELECT g.title AS game_title,
    gen.name AS genre_name
   FROM ((lab_schema.game g
     JOIN lab_schema.game_genre gg ON ((g.id = gg.game_id)))
     JOIN lab_schema.genre gen ON ((gg.genre_id = gen.id)));


--
-- Name: game_id_seq; Type: SEQUENCE; Schema: lab_schema; Owner: -
--

CREATE SEQUENCE lab_schema.game_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: game_id_seq; Type: SEQUENCE OWNED BY; Schema: lab_schema; Owner: -
--

ALTER SEQUENCE lab_schema.game_id_seq OWNED BY lab_schema.game.id;


--
-- Name: game_info_v; Type: VIEW; Schema: lab_schema; Owner: -
--

CREATE VIEW lab_schema.game_info_v AS
 SELECT g.id,
    g.title AS game_title,
    d.name AS developer_name,
    d.country AS developer_country,
    g.release_year,
    g.price,
    g.is_released
   FROM (lab_schema.game g
     JOIN lab_schema.developer d ON ((g.developer_id = d.id)));


--
-- Name: game_reviews_v; Type: VIEW; Schema: lab_schema; Owner: -
--

CREATE VIEW lab_schema.game_reviews_v AS
 SELECT g.title AS game_title,
    d.name AS developer_name,
    r.reviewer_name,
    r.score,
    r.review_date
   FROM ((lab_schema.review r
     JOIN lab_schema.game g ON ((r.game_id = g.id)))
     JOIN lab_schema.developer d ON ((g.developer_id = d.id)));


--
-- Name: genre_id_seq; Type: SEQUENCE; Schema: lab_schema; Owner: -
--

CREATE SEQUENCE lab_schema.genre_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: genre_id_seq; Type: SEQUENCE OWNED BY; Schema: lab_schema; Owner: -
--

ALTER SEQUENCE lab_schema.genre_id_seq OWNED BY lab_schema.genre.id;


--
-- Name: log_game; Type: TABLE; Schema: lab_schema; Owner: -
--

CREATE TABLE lab_schema.log_game (
    id bigint NOT NULL,
    game_id bigint,
    change_datetime timestamp without time zone DEFAULT now(),
    old_price numeric(10,2) DEFAULT NULL::numeric,
    new_price numeric(10,2) DEFAULT NULL::numeric
);


--
-- Name: log_game_id_seq; Type: SEQUENCE; Schema: lab_schema; Owner: -
--

CREATE SEQUENCE lab_schema.log_game_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: log_game_id_seq; Type: SEQUENCE OWNED BY; Schema: lab_schema; Owner: -
--

ALTER SEQUENCE lab_schema.log_game_id_seq OWNED BY lab_schema.log_game.id;


--
-- Name: review_id_seq; Type: SEQUENCE; Schema: lab_schema; Owner: -
--

CREATE SEQUENCE lab_schema.review_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: review_id_seq; Type: SEQUENCE OWNED BY; Schema: lab_schema; Owner: -
--

ALTER SEQUENCE lab_schema.review_id_seq OWNED BY lab_schema.review.id;


--
-- Name: developer id; Type: DEFAULT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.developer ALTER COLUMN id SET DEFAULT nextval('lab_schema.developer_id_seq'::regclass);


--
-- Name: game id; Type: DEFAULT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.game ALTER COLUMN id SET DEFAULT nextval('lab_schema.game_id_seq'::regclass);


--
-- Name: game_genre id; Type: DEFAULT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.game_genre ALTER COLUMN id SET DEFAULT nextval('lab_schema.game_genre_id_seq'::regclass);


--
-- Name: genre id; Type: DEFAULT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.genre ALTER COLUMN id SET DEFAULT nextval('lab_schema.genre_id_seq'::regclass);


--
-- Name: log_game id; Type: DEFAULT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.log_game ALTER COLUMN id SET DEFAULT nextval('lab_schema.log_game_id_seq'::regclass);


--
-- Name: review id; Type: DEFAULT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.review ALTER COLUMN id SET DEFAULT nextval('lab_schema.review_id_seq'::regclass);


--
-- Data for Name: developer; Type: TABLE DATA; Schema: lab_schema; Owner: -
--

INSERT INTO lab_schema.developer VALUES (1, 'Valve Corporation', 'USA', true);
INSERT INTO lab_schema.developer VALUES (2, 'Mojang Studios', 'Sweden', true);
INSERT INTO lab_schema.developer VALUES (4, 'Hopoo Games', 'USA', true);
INSERT INTO lab_schema.developer VALUES (5, 'Arc System Works', 'Japan', true);
INSERT INTO lab_schema.developer VALUES (3, 'Team Cherry', 'Canada', true);


--
-- Data for Name: game; Type: TABLE DATA; Schema: lab_schema; Owner: -
--

INSERT INTO lab_schema.game VALUES (4, 'Risk of Rain 2', 4, 2020, 27.49, true);
INSERT INTO lab_schema.game VALUES (5, 'Guilty Gear Strive', 5, 2021, 65.99, true);
INSERT INTO lab_schema.game VALUES (3, 'Hollow Knight', 3, 2017, 21.99, true);
INSERT INTO lab_schema.game VALUES (2, 'Minecraft', 2, 2011, 11.37, true);
INSERT INTO lab_schema.game VALUES (21, 'Elden Ring', 1, 2022, 59.99, true);
INSERT INTO lab_schema.game VALUES (1, 'Dota 2', 1, 2013, 0.00, true);


--
-- Data for Name: game_genre; Type: TABLE DATA; Schema: lab_schema; Owner: -
--

INSERT INTO lab_schema.game_genre VALUES (1, 1, 1);
INSERT INTO lab_schema.game_genre VALUES (3, 2, 3);
INSERT INTO lab_schema.game_genre VALUES (4, 2, 4);
INSERT INTO lab_schema.game_genre VALUES (5, 3, 5);
INSERT INTO lab_schema.game_genre VALUES (6, 3, 6);
INSERT INTO lab_schema.game_genre VALUES (7, 3, 7);
INSERT INTO lab_schema.game_genre VALUES (8, 4, 8);
INSERT INTO lab_schema.game_genre VALUES (9, 4, 9);
INSERT INTO lab_schema.game_genre VALUES (10, 4, 6);
INSERT INTO lab_schema.game_genre VALUES (11, 5, 10);
INSERT INTO lab_schema.game_genre VALUES (12, 5, 6);


--
-- Data for Name: genre; Type: TABLE DATA; Schema: lab_schema; Owner: -
--

INSERT INTO lab_schema.genre VALUES (1, 'MOBA');
INSERT INTO lab_schema.genre VALUES (2, 'Strategy');
INSERT INTO lab_schema.genre VALUES (3, 'Sandbox');
INSERT INTO lab_schema.genre VALUES (4, 'Survival');
INSERT INTO lab_schema.genre VALUES (5, 'Metroidvania');
INSERT INTO lab_schema.genre VALUES (6, 'Action');
INSERT INTO lab_schema.genre VALUES (7, 'Platformer');
INSERT INTO lab_schema.genre VALUES (8, 'Roguelike');
INSERT INTO lab_schema.genre VALUES (9, 'Shooter');
INSERT INTO lab_schema.genre VALUES (10, 'Fighting');


--
-- Data for Name: log_game; Type: TABLE DATA; Schema: lab_schema; Owner: -
--

INSERT INTO lab_schema.log_game VALUES (3, 1, '2026-11-10 21:56:10.93907', 0.00, 0.00);


--
-- Data for Name: review; Type: TABLE DATA; Schema: lab_schema; Owner: -
--

INSERT INTO lab_schema.review VALUES (1, 1, 'Alex_Pro', 8, '2024-03-15');
INSERT INTO lab_schema.review VALUES (2, 1, 'GamerGirl', 7, '2024-05-20');
INSERT INTO lab_schema.review VALUES (4, 2, 'Builder228', 10, '2024-01-05');
INSERT INTO lab_schema.review VALUES (6, 3, 'IndieLover', 10, '2024-02-14');
INSERT INTO lab_schema.review VALUES (7, 3, 'HardcoreGamer', 9, '2024-06-30');
INSERT INTO lab_schema.review VALUES (8, 3, 'CasualPlayer', 8, '2024-08-22');
INSERT INTO lab_schema.review VALUES (9, 4, 'RogueMaster', 9, '2024-03-01');
INSERT INTO lab_schema.review VALUES (10, 4, 'SpeedRunner', 10, '2024-07-15');
INSERT INTO lab_schema.review VALUES (11, 5, 'FGC_Veteran', 9, '2024-04-10');
INSERT INTO lab_schema.review VALUES (12, 5, 'AnimeFan', 10, '2024-09-05');
INSERT INTO lab_schema.review VALUES (13, 5, 'Newbie', 7, '2024-10-01');
INSERT INTO lab_schema.review VALUES (5, 2, 'SteveFan', 10, '2024-04-18');


--
-- Name: developer_id_seq; Type: SEQUENCE SET; Schema: lab_schema; Owner: -
--

SELECT pg_catalog.setval('lab_schema.developer_id_seq', 21, true);


--
-- Name: game_genre_id_seq; Type: SEQUENCE SET; Schema: lab_schema; Owner: -
--

SELECT pg_catalog.setval('lab_schema.game_genre_id_seq', 12, true);


--
-- Name: game_id_seq; Type: SEQUENCE SET; Schema: lab_schema; Owner: -
--

SELECT pg_catalog.setval('lab_schema.game_id_seq', 23, true);


--
-- Name: genre_id_seq; Type: SEQUENCE SET; Schema: lab_schema; Owner: -
--

SELECT pg_catalog.setval('lab_schema.genre_id_seq', 10, true);


--
-- Name: log_game_id_seq; Type: SEQUENCE SET; Schema: lab_schema; Owner: -
--

SELECT pg_catalog.setval('lab_schema.log_game_id_seq', 5, true);


--
-- Name: review_id_seq; Type: SEQUENCE SET; Schema: lab_schema; Owner: -
--

SELECT pg_catalog.setval('lab_schema.review_id_seq', 18, true);


--
-- Name: developer developer_name_key; Type: CONSTRAINT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.developer
    ADD CONSTRAINT developer_name_key UNIQUE (name);


--
-- Name: developer developer_pkey; Type: CONSTRAINT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.developer
    ADD CONSTRAINT developer_pkey PRIMARY KEY (id);


--
-- Name: game_genre game_genre_game_id_genre_id_key; Type: CONSTRAINT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.game_genre
    ADD CONSTRAINT game_genre_game_id_genre_id_key UNIQUE (game_id, genre_id);


--
-- Name: game_genre game_genre_pkey; Type: CONSTRAINT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.game_genre
    ADD CONSTRAINT game_genre_pkey PRIMARY KEY (id);


--
-- Name: game game_pkey; Type: CONSTRAINT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.game
    ADD CONSTRAINT game_pkey PRIMARY KEY (id);


--
-- Name: genre genre_name_key; Type: CONSTRAINT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.genre
    ADD CONSTRAINT genre_name_key UNIQUE (name);


--
-- Name: genre genre_pkey; Type: CONSTRAINT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.genre
    ADD CONSTRAINT genre_pkey PRIMARY KEY (id);


--
-- Name: log_game log_game_pkey; Type: CONSTRAINT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.log_game
    ADD CONSTRAINT log_game_pkey PRIMARY KEY (id);


--
-- Name: review review_pkey; Type: CONSTRAINT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.review
    ADD CONSTRAINT review_pkey PRIMARY KEY (id);


--
-- Name: idx_game_developer_id; Type: INDEX; Schema: lab_schema; Owner: -
--

CREATE INDEX idx_game_developer_id ON lab_schema.game USING btree (developer_id);


--
-- Name: idx_game_genre_game_id; Type: INDEX; Schema: lab_schema; Owner: -
--

CREATE INDEX idx_game_genre_game_id ON lab_schema.game_genre USING btree (game_id);


--
-- Name: idx_game_release_year; Type: INDEX; Schema: lab_schema; Owner: -
--

CREATE INDEX idx_game_release_year ON lab_schema.game USING btree (release_year);


--
-- Name: idx_review_game_id; Type: INDEX; Schema: lab_schema; Owner: -
--

CREATE INDEX idx_review_game_id ON lab_schema.review USING btree (game_id);


--
-- Name: game game_price_change_trigger; Type: TRIGGER; Schema: lab_schema; Owner: -
--

CREATE TRIGGER game_price_change_trigger AFTER INSERT OR UPDATE ON lab_schema.game FOR EACH ROW EXECUTE FUNCTION lab_schema.log_game_price_trigger();


--
-- Name: game game_developer_id_fkey; Type: FK CONSTRAINT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.game
    ADD CONSTRAINT game_developer_id_fkey FOREIGN KEY (developer_id) REFERENCES lab_schema.developer(id);


--
-- Name: game_genre game_genre_game_id_fkey; Type: FK CONSTRAINT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.game_genre
    ADD CONSTRAINT game_genre_game_id_fkey FOREIGN KEY (game_id) REFERENCES lab_schema.game(id) ON DELETE CASCADE;


--
-- Name: game_genre game_genre_genre_id_fkey; Type: FK CONSTRAINT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.game_genre
    ADD CONSTRAINT game_genre_genre_id_fkey FOREIGN KEY (genre_id) REFERENCES lab_schema.genre(id) ON DELETE CASCADE;


--
-- Name: log_game log_game_game_id_fkey; Type: FK CONSTRAINT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.log_game
    ADD CONSTRAINT log_game_game_id_fkey FOREIGN KEY (game_id) REFERENCES lab_schema.game(id);


--
-- Name: review review_game_id_fkey; Type: FK CONSTRAINT; Schema: lab_schema; Owner: -
--

ALTER TABLE ONLY lab_schema.review
    ADD CONSTRAINT review_game_id_fkey FOREIGN KEY (game_id) REFERENCES lab_schema.game(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

-- ============================================================================
--  Создание роли приложения lab_test и выдача прав
--  (необязательный блок; требуется для приложений из лабораторных 4-5)
-- ============================================================================
DO $$
DECLARE
    is_super boolean;
    role_exists boolean;
BEGIN
    SELECT rolsuper INTO is_super
    FROM pg_roles
    WHERE rolname = current_user;

    SELECT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'lab_test')
    INTO role_exists;

    IF NOT role_exists AND is_super THEN
        CREATE ROLE lab_test LOGIN PASSWORD 'lab_test';
        role_exists := true;
        RAISE NOTICE 'Роль lab_test создана.';
    END IF;

    IF role_exists THEN
        EXECUTE 'GRANT USAGE ON SCHEMA lab_schema TO lab_test';
        EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA lab_schema TO lab_test';
        EXECUTE 'GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA lab_schema TO lab_test';
        EXECUTE 'GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA lab_schema TO lab_test';
        EXECUTE format('GRANT CONNECT ON DATABASE %I TO lab_test', current_database());
        RAISE NOTICE 'Права для роли lab_test выданы.';
    ELSE
        RAISE NOTICE 'Роль lab_test не создана: недостаточно прав. Создайте её вручную (см. инструкцию в начале файла).';
    END IF;
END
$$;

-- ============================================================================
--  Конец дампа THEDATABASE.sql
-- ============================================================================
