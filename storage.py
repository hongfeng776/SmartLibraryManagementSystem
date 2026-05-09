import json
import os
from book import Book

DATA_FILE = 'books.json'


def load_books():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [Book.from_dict(item) for item in data]


def save_books(books):
    data = [book.to_dict() for book in books]
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
