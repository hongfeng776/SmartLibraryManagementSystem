import json
import os
from typing import List
from models.book import Book


class JsonStorage:
    def __init__(self, file_path: str = "books.json"):
        self.file_path = file_path

    def load(self) -> List[Book]:
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Book.from_dict(item) for item in data]

    def save(self, books: List[Book]) -> None:
        data = [book.to_dict() for book in books]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
