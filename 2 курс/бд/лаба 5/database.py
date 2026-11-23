import psycopg2
from psycopg2 import OperationalError, DatabaseError


class Database:
    """Класс для управления подключением и выполнением запросов к БД PostgreSQL."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5432,
        user: str = "lab_test",
        password: str = "lab_test",
        dbname: str = "lab_db",
    ):
        self._connection = None
        self._db_params = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "dbname": dbname,
        }

    def openConnection(self):
        """Открытие соединения с базой данных."""
        try:
            self._connection = psycopg2.connect(**self._db_params)
        except OperationalError as ex:
            print(f"Ошибка! Клиенту не удалось установить соединение с сервером: {ex}")
            raise
        except DatabaseError as ex:
            print(f"Ошибка драйвера базы данных: {ex}")
            raise

    def closeConnection(self):
        """Закрытие соединения с базой данных."""
        if self._connection is not None and not self._connection.closed:
            self._connection.close()
            self._connection = None

    def query(self, sql: str, params: tuple = None) -> list:
        """Выполнение SELECT-запроса с возвратом всех строк."""
        if self._connection is None or self._connection.closed:
            raise RuntimeError("Ошибка! Соединение закрыто или никогда не было подключено.")
        with self._connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    def execute_scalar(self, sql: str, params: tuple = None):
        """Выполнение запроса/функции в транзакции с возвратом скалярного значения."""
        if self._connection is None or self._connection.closed:
            raise RuntimeError("Ошибка! Соединение закрыто или никогда не было подключено.")
        try:
            with self._connection.cursor() as cursor:
                cursor.execute(sql, params)
                row = cursor.fetchone()
            self._connection.commit()
            return row[0] if row else None
        except Exception:
            self._connection.rollback()
            raise
