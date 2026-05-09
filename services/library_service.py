from typing import List, Optional
from models.book import Book
from storage.json_storage import JsonStorage
import uuid


class LibraryService:
    def __init__(self, storage: JsonStorage):
        self.storage = storage
        self.books: List[Book] = self.storage.load()

    def add_book(
        self,
        title: str,
        author: str,
        year: int,
        isbn: str = "",
        publisher: str = "",
    ) -> Book:
        book_id = str(uuid.uuid4())[:8]
        book = Book(
            book_id=book_id,
            title=title,
            author=author,
            year=year,
            isbn=isbn,
            publisher=publisher,
        )
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

    def find_book_by_isbn(self, isbn: str) -> Optional[Book]:
        isbn_stripped = isbn.strip()
        for book in self.books:
            if book.isbn and book.isbn == isbn_stripped:
                return book
        return None

    def find_books_by_title(self, title: str) -> List[Book]:
        title_lower = title.lower().strip()
        return [
            book for book in self.books if title_lower in book.title.lower()
        ]

    def search_books(self, keyword: str) -> List[Book]:
        keyword_lower = keyword.lower()
        return [
            book
            for book in self.books
            if keyword_lower in book.title.lower()
            or keyword_lower in book.author.lower()
            or keyword_lower in (book.isbn or "").lower()
        ]

    def update_book(
        self,
        book_id: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
        year: Optional[int] = None,
        isbn: Optional[str] = None,
        publisher: Optional[str] = None,
    ) -> Optional[Book]:
        book = self.find_book_by_id(book_id)
        if not book:
            return None
        if title is not None:
            book.title = title
        if author is not None:
            book.author = author
        if year is not None:
            book.year = year
        if isbn is not None:
            book.isbn = isbn
        if publisher is not None:
            book.publisher = publisher
        self.storage.save(self.books)
        return book

    def get_all_books(self) -> List[Book]:
        return list(self.books)
