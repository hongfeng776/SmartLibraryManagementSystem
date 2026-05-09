from typing import List, Optional
from models.book import Book
from storage.json_storage import JsonStorage
import uuid


class LibraryService:
    def __init__(self, storage: JsonStorage):
        self.storage = storage
        self.books: List[Book] = self.storage.load()

    def add_book(self, title: str, author: str, year: int) -> Book:
        book_id = str(uuid.uuid4())[:8]
        book = Book(book_id=book_id, title=title, author=author, year=year)
        self.books.append(book)
        self.storage.save(self.books)
        return book

    def delete_book(self, book_id: str) -> bool:
        for i, book in enumerate(self.books):
            if book.book_id == book_id:
                self.books.pop(i)
                self.storage.save(self.books)
                return True
        return False

    def find_book_by_id(self, book_id: str) -> Optional[Book]:
        for book in self.books:
            if book.book_id == book_id:
                return book
        return None

    def search_books(self, keyword: str) -> List[Book]:
        keyword_lower = keyword.lower()
        return [
            book
            for book in self.books
            if keyword_lower in book.title.lower()
            or keyword_lower in book.author.lower()
        ]

    def get_all_books(self) -> List[Book]:
        return list(self.books)
