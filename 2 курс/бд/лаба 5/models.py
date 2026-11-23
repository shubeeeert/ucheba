from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class GameItem:
    """Сущность «Видеоигра» (родительская таблица lab_schema.game)."""
    id: int
    title: str

    def __str__(self) -> str:
        return self.title


@dataclass
class Review:
    """Сущность «Отзыв» (дочерняя таблица lab_schema.review)."""
    id: Optional[int]
    game_id: int
    game_title: str
    reviewer_name: str
    score: int
    review_date: date
