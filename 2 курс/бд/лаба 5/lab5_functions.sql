-- ============================================================================
-- Лабораторная работа №5. Функции PL/pgSQL для приложения на Python
-- Работа с таблицей отзывов lab_schema.review (внешний ключ на lab_schema.game)
-- ============================================================================

-- 1. Получение списка игр (родительская таблица для выбора внешнего ключа)
CREATE OR REPLACE FUNCTION lab_schema.get_all_games_list()
RETURNS TABLE(
    id BIGINT,
    title VARCHAR(150)
) AS $$
BEGIN
    RETURN QUERY
    SELECT g.id, g.title
    FROM lab_schema.game g
    ORDER BY g.title;
END;
$$ LANGUAGE plpgsql;

-- 2. Получение всех отзывов с названиями игр
CREATE OR REPLACE FUNCTION lab_schema.get_reviews_with_games()
RETURNS TABLE(
    id BIGINT,
    game_id BIGINT,
    game_title VARCHAR(150),
    reviewer_name VARCHAR(100),
    score INTEGER,
    review_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT r.id, r.game_id, g.title, r.reviewer_name, r.score, r.review_date
    FROM lab_schema.review r
    JOIN lab_schema.game g ON r.game_id = g.id
    ORDER BY r.id;
END;
$$ LANGUAGE plpgsql;

-- 3. Регистронезависимая фильтрация отзывов по имени автора (с функцией UPPER)
CREATE OR REPLACE FUNCTION lab_schema.filter_reviews_by_reviewer(
    _pattern VARCHAR(100)
)
RETURNS TABLE(
    id BIGINT,
    game_id BIGINT,
    game_title VARCHAR(150),
    reviewer_name VARCHAR(100),
    score INTEGER,
    review_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT r.id, r.game_id, g.title, r.reviewer_name, r.score, r.review_date
    FROM lab_schema.review r
    JOIN lab_schema.game g ON r.game_id = g.id
    WHERE UPPER(r.reviewer_name) LIKE UPPER(_pattern)
    ORDER BY r.id;
END;
$$ LANGUAGE plpgsql;

-- 4. Сохранение (добавление или изменение) отзыва с проверкой дубликатов
CREATE OR REPLACE FUNCTION lab_schema.save_review(
    _id BIGINT,
    _game_id BIGINT,
    _reviewer_name VARCHAR(100),
    _score INTEGER,
    _review_date DATE
)
RETURNS BIGINT AS $$
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
$$ LANGUAGE plpgsql;

-- 5. Удаление отзыва по id
CREATE OR REPLACE FUNCTION lab_schema.delete_review(
    _id BIGINT
)
RETURNS VOID AS $$
BEGIN
    DELETE FROM lab_schema.review WHERE id = _id;
EXCEPTION
    WHEN foreign_key_violation THEN
        RAISE EXCEPTION 'Невозможно удалить запись, так как на неё существуют внешние ссылки.';
END;
$$ LANGUAGE plpgsql;
