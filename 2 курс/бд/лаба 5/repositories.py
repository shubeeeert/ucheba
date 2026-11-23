from typing import List, Optional
from database import Database
from models import GameItem, Review


class GameRepository:
    """Репозиторий для работы с родительской таблицей игр (lab_schema.game)."""

    def __init__(self, db: Database):
        self._db = db

    def get_all(self) -> List[GameItem]:
        self._db.openConnection()
        try:
            rows = self._db.query("SELECT * FROM lab_schema.get_all_games_list()")
            return [GameItem(id=row[0], title=row[1]) for row in rows]
        finally:
            self._db.closeConnection()


class ReviewRepository:
    """Репозиторий для работы с таблицей отзывов (lab_schema.review)."""

    def __init__(self, db: Database):
        self._db = db

    def get_all(self) -> List[Review]:
        """Получение всех отзывов вместе с названиями игр."""
        self._db.openConnection()
        try:
            rows = self._db.query("SELECT * FROM lab_schema.get_reviews_with_games()")
            return [
                Review(
                    id=row[0],
                    game_id=row[1],
                    game_title=row[2],
                    reviewer_name=row[3],
                    score=row[4],
                    review_date=row[5],
                )
                for row in rows
            ]
        finally:
            self._db.closeConnection()

    def filter_by_reviewer(self, pattern: str) -> List[Review]:
        """Регистронезависимая фильтрация отзывов по имени автора через запрос к БД."""
        self._db.openConnection()
        try:
            rows = self._db.query(
                "SELECT * FROM lab_schema.filter_reviews_by_reviewer(%s)",
                (f"%{pattern}%",),
            )
            return [
                Review(
                    id=row[0],
                    game_id=row[1],
                    game_title=row[2],
                    reviewer_name=row[3],
                    score=row[4],
                    review_date=row[5],
                )
                for row in rows
            ]
        finally:
            self._db.closeConnection()

    def exists(self, game_id: int, reviewer_name: str, exclude_id: Optional[int] = None) -> bool:
        """Проверка наличия дубликата в БД (без учёта регистра)."""
        self._db.openConnection()
        try:
            sql = """
                SELECT EXISTS (
                    SELECT 1 FROM lab_schema.review
                    WHERE game_id = %s
                      AND UPPER(TRIM(reviewer_name)) = UPPER(TRIM(%s))
                      AND (%s IS NULL OR id <> %s)
                )
            """
            result = self._db.execute_scalar(
                sql, (game_id, reviewer_name.strip(), exclude_id, exclude_id)
            )
            return bool(result)
        finally:
            self._db.closeConnection()

    def save(self, review: Review) -> int:
        """Сохранение (добавление или изменение) строки с помощью функции PL/pgSQL save_review."""
        self._db.openConnection()
        try:
            saved_id = self._db.execute_scalar(
                "SELECT lab_schema.save_review(%s, %s, %s, %s, %s)",
                (
                    review.id,
                    review.game_id,
                    review.reviewer_name.strip(),
                    review.score,
                    review.review_date,
                ),
            )
            return int(saved_id)
        finally:
            self._db.closeConnection()

    def delete(self, review_id: int) -> None:
        """Удаление строки с помощью функции PL/pgSQL delete_review."""
        self._db.openConnection()
        try:
            self._db.execute_scalar("SELECT lab_schema.delete_review(%s)", (review_id,))
        finally:
            self._db.closeConnection()
