from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Book:
    book_id: str
    title: str
    author: str
    year: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Book":
        return cls(
            book_id=data["book_id"],
            title=data["title"],
            author=data["author"],
            year=data["year"],
        )
