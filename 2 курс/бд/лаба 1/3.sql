-- Создание таблиц

-- Таблица разработчиков
CREATE TABLE lab_schema.developer (
    id bigserial PRIMARY KEY,
    name varchar(100) NOT NULL UNIQUE,
    country varchar(50),
    is_active boolean NOT NULL DEFAULT true -- Булево поле с префиксом is_
);

-- Таблица жанров
CREATE TABLE lab_schema.genre (
    id bigserial PRIMARY KEY,
    name varchar(50) NOT NULL UNIQUE
);

-- Таблица игр (содержит числовые данные: release_year, price)
CREATE TABLE lab_schema.game (
    id bigserial PRIMARY KEY,
    title varchar(150) NOT NULL,
    developer_id bigint NOT NULL REFERENCES lab_schema.developer(id), -- Внешний ключ
    release_year integer CHECK (release_year >= 1970 AND release_year <= 2030), -- Ограничение CHECK
    price numeric(10, 2) CHECK (price >= 0), -- Числовые данные + ограничение
    is_released boolean NOT NULL DEFAULT false
);

-- Промежуточная таблица для связи "Игра - Жанр" (многие-ко-многим)
CREATE TABLE lab_schema.game_genre (
    id bigserial PRIMARY KEY,
    game_id bigint NOT NULL REFERENCES lab_schema.game(id) ON DELETE CASCADE,
    genre_id bigint NOT NULL REFERENCES lab_schema.genre(id) ON DELETE CASCADE,
    UNIQUE (game_id, genre_id) -- Уникальный индекс: один жанр не может дублироваться у одной игры
);

-- Таблица отзывов
CREATE TABLE lab_schema.review (
    id bigserial PRIMARY KEY,
    game_id bigint NOT NULL REFERENCES lab_schema.game(id) ON DELETE CASCADE,
    reviewer_name varchar(100) NOT NULL,
    score integer NOT NULL CHECK (score >= 1 AND score <= 10), -- Оценка строго от 1 до 10
    review_date date NOT NULL DEFAULT CURRENT_DATE
);


-- Создание индексов для производительности

-- Индексы по внешним ключам и полям, по которым часто будет идти поиск/сортировка
CREATE INDEX idx_game_developer_id ON lab_schema.game(developer_id);
CREATE INDEX idx_game_release_year ON lab_schema.game(release_year);
CREATE INDEX idx_review_game_id ON lab_schema.review(game_id);
CREATE INDEX idx_game_genre_game_id ON lab_schema.game_genre(game_id);

-- Выдача прав пользователю lab_test
-- Выдаем права на все созданные таблицы
GRANT ALL ON ALL TABLES IN SCHEMA lab_schema TO lab_test;
-- Выдаем права на последовательности (sequences), иначе пользователь не сможет 
-- добавлять новые записи, так как bigserial использует их для автоинкремента id
GRANT ALL ON ALL SEQUENCES IN SCHEMA lab_schema TO lab_test; 