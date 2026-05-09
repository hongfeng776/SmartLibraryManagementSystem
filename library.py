from book import Book
from storage import load_books, save_books


class Library:
    def __init__(self):
        self.books = load_books()

    def add_book(self, book_id, title, author, year):
        for book in self.books:
            if book.book_id == book_id:
                return False, f"图书ID {book_id} 已存在"
        book = Book(book_id, title, author, year)
        self.books.append(book)
        save_books(self.books)
        return True, f"图书《{title}》添加成功"

    def search_books(self, keyword):
        results = []
        for book in self.books:
            if keyword.lower() in book.title.lower() or \
               keyword.lower() in book.author.lower() or \
               keyword == str(book.book_id):
                results.append(book)
        return results

    def delete_book(self, book_id):
        for i, book in enumerate(self.books):
            if book.book_id == book_id:
                deleted_book = self.books.pop(i)
                save_books(self.books)
                return True, f"图书《{deleted_book.title}》已删除"
        return False, f"未找到ID为 {book_id} 的图书"

    def list_all_books(self):
        return self.books

    def get_book_count(self):
        return len(self.books)
