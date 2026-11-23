-- ============================================================================
-- Лабораторная работа №4. Функции PL/pgSQL для работы приложения C# с БД
-- ============================================================================

-- 1. Получение списка всех разработчиков (родительская таблица)
CREATE OR REPLACE FUNCTION lab_schema.get_all_developers()
RETURNS TABLE(
    id BIGINT,
    name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT d.id, d.name
    FROM lab_schema.developer d
    ORDER BY d.name;
END;
$$ LANGUAGE plpgsql;

-- 2. Получение списка всех игр с названиями разработчиков
CREATE OR REPLACE FUNCTION lab_schema.get_games_with_developers()
RETURNS TABLE(
    id BIGINT,
    title VARCHAR(150),
    developer_name VARCHAR(100),
    release_year INTEGER,
    price NUMERIC(10, 2),
    is_released BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT g.id, g.title, d.name, g.release_year, g.price, g.is_released
    FROM lab_schema.game g
    JOIN lab_schema.developer d ON g.developer_id = d.id
    ORDER BY g.id;
END;
$$ LANGUAGE plpgsql;

-- 3. Регистронезависимая фильтрация игр по названию (с использованием UPPER)
CREATE OR REPLACE FUNCTION lab_schema.filter_games_by_title(
    _title_pattern VARCHAR(150)
)
RETURNS TABLE(
    id BIGINT,
    title VARCHAR(150),
    developer_name VARCHAR(100),
    release_year INTEGER,
    price NUMERIC(10, 2),
    is_released BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT g.id, g.title, d.name, g.release_year, g.price, g.is_released
    FROM lab_schema.game g
    JOIN lab_schema.developer d ON g.developer_id = d.id
    WHERE UPPER(g.title) LIKE UPPER(_title_pattern)
    ORDER BY g.id;
END;
$$ LANGUAGE plpgsql;

-- 4. Сохранение (добавление или изменение) строки таблицы game с проверкой дубликатов
CREATE OR REPLACE FUNCTION lab_schema.save_game(
    _id BIGINT,
    _title VARCHAR(150),
    _developer_id BIGINT,
    _release_year INTEGER,
    _price NUMERIC(10, 2),
    _is_released BOOLEAN
)
RETURNS BIGINT AS $$
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
$$ LANGUAGE plpgsql;

-- 5. Удаление строки таблицы game по id
CREATE OR REPLACE FUNCTION lab_schema.delete_game(
    _id BIGINT
)
RETURNS VOID AS $$
BEGIN
    DELETE FROM lab_schema.log_game WHERE game_id = _id;
    DELETE FROM lab_schema.game WHERE id = _id;
EXCEPTION
    WHEN foreign_key_violation THEN
        RAISE EXCEPTION 'Невозможно удалить игру, так как на неё есть ссылки из других таблиц.';
END;
$$ LANGUAGE plpgsql;
