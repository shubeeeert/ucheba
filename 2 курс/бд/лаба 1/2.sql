-- 3. Создаем схему (чтобы не мусорить в стандартной public)
CREATE SCHEMA lab_schema AUTHORIZATION lab_test;

-- 4. Выдаем пользователю все права на эту схему
GRANT ALL ON SCHEMA lab_schema TO lab_test;

-- 5. Выдаем права на все таблицы, которые мы скоро создадим в этой схеме
GRANT ALL ON ALL TABLES IN SCHEMA lab_schema TO lab_test;