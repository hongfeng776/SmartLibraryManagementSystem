class Book:
    def __init__(self, book_id, title, author, year):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.year = year

    def to_dict(self):
        return {
            'book_id': self.book_id,
            'title': self.title,
            'author': self.author,
            'year': self.year
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            book_id=data['book_id'],
            title=data['title'],
            author=data['author'],
            year=data['year']
        )

    def __str__(self):
        return f"[ID: {self.book_id}] 《{self.title}》 - {self.author} ({self.year}年)"
