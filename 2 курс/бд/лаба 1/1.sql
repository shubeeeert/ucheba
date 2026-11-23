-- 1. Создаем нового пользователя (роль) с паролем
CREATE USER lab_test WITH PASSWORD 'lab_test';

-- 2. Создаем пустую базу данных и делаем lab_test её владельцем
CREATE DATABASE lab_db OWNER lab_test;