"""
图书管理服务层模块

提供图书管理的核心业务逻辑，包括：
- 图书的增删改查操作
- 数据验证和业务规则
- 搜索和统计功能
- 备份和恢复服务
"""

import uuid
from typing import List, Optional, Dict, Any, Tuple

from models.book import Book
from storage.json_storage import JsonStorage
from storage.csv_storage import (
    CsvStorage,
    CsvStorageError,
    CsvInvalidFormatError,
)


class LibraryServiceError(Exception):
    """图书服务基异常类"""
    pass


class DuplicateIsbnError(LibraryServiceError):
    """ISBN重复异常"""
    pass


class BookNotFoundError(LibraryServiceError):
    """图书不存在异常"""
    pass


class InvalidInputError(LibraryServiceError):
    """输入数据无效异常"""
    pass


class LibraryService:
    """
    图书管理服务类

    封装图书管理的所有业务逻辑，作为 UI 层和存储层之间的桥梁。
    负责数据验证、业务规则处理和协调各模块的交互。

    Attributes:
        storage: 存储管理器实例
        books: 内存中的图书列表
    """

    def __init__(self, storage: JsonStorage) -> None:
        """
        初始化图书管理服务

        Args:
            storage: JsonStorage 实例，负责数据持久化
        """
        self.storage = storage
        self.books: List[Book] = self.storage.load()

    def flush(self) -> None:
        """
        将内存中的数据同步到持久化存储

        在退出程序或需要手动保存时调用。
        """
        self.storage.save(self.books)

    def get_book_count(self) -> int:
        """
        获取图书总数量

        Returns:
            图书馆中的图书总数
        """
        return len(self.books)

    def _is_isbn_taken(self, isbn: str, exclude_book_id: Optional[str] = None) -> bool:
        """
        检查 ISBN 是否已被使用

        内部方法，用于添加和更新图书时的 ISBN 唯一性检查。

        Args:
            isbn: 要检查的 ISBN 编号
            exclude_book_id: 排除检查的图书 ID（用于更新时跳过自身）

        Returns:
            ISBN 已被占用返回 True，否则返回 False
        """
        isbn_stripped = isbn.strip()
        if not isbn_stripped:
            return False

        for book in self.books:
            if book.book_id == exclude_book_id:
                continue
            if book.isbn and book.isbn == isbn_stripped:
                return True

        return False

    def add_book(
        self,
        title: str,
        author: str,
        year: int,
        isbn: str = "",
        publisher: str = "",
    ) -> Book:
        """
        添加新图书

        自动生成 8 位 UUID 作为图书 ID，
        验证输入数据并检查 ISBN 唯一性。

        Args:
            title: 图书标题（不能为空）
            author: 作者姓名（不能为空）
            year: 出版年份（必须为正整数）
            isbn: ISBN 编号（可选，不能重复）
            publisher: 出版社名称（可选）

        Returns:
            新创建的 Book 实例

        Raises:
            InvalidInputError: 输入数据无效时抛出
            DuplicateIsbnError: ISBN 已存在时抛出
        """
        title = title.strip()
        author = author.strip()

        if not title:
            raise InvalidInputError("书名不能为空")
        if not author:
            raise InvalidInputError("作者不能为空")
        if year <= 0:
            raise InvalidInputError("年份必须是正整数")

        isbn = isbn.strip()
        if self._is_isbn_taken(isbn):
            raise DuplicateIsbnError(f"ISBN {isbn} 已存在")

        book_id = str(uuid.uuid4())[:8]
        new_book = Book(
            book_id=book_id,
            title=title,
            author=author,
            year=year,
            isbn=isbn,
            publisher=publisher.strip(),
        )

        self.books.append(new_book)
        self.storage.save(self.books)

        return new_book

    def delete_book(self, book_id: str) -> bool:
        """
        删除图书

        Args:
            book_id: 要删除的图书 ID

        Returns:
            删除成功返回 True，图书不存在返回 False
        """
        for index, book in enumerate(self.books):
            if book.book_id == book_id:
                self.books.pop(index)
                self.storage.save(self.books)
                return True

        return False

    def find_book_by_id(self, book_id: str) -> Optional[Book]:
        """
        根据图书 ID 查找图书

        Args:
            book_id: 图书 ID

        Returns:
            找到的 Book 实例，未找到返回 None
        """
        for book in self.books:
            if book.book_id == book_id:
                return book

        return None

    def find_book_by_isbn(self, isbn: str) -> Optional[Book]:
        """
        根据 ISBN 查找图书

        Args:
            isbn: ISBN 编号

        Returns:
            找到的 Book 实例，未找到返回 None
        """
        isbn_stripped = isbn.strip()

        for book in self.books:
            if book.isbn and book.isbn == isbn_stripped:
                return book

        return None

    def find_books_by_title(self, title: str) -> List[Book]:
        """
        根据书名关键词搜索图书

        不区分大小写，支持模糊匹配。

        Args:
            title: 书名关键词

        Returns:
            匹配的图书列表
        """
        title_lower = title.lower().strip()

        return [
            book for book in self.books
            if title_lower in book.title.lower()
        ]

    def find_books_by_author(self, author: str) -> List[Book]:
        """
        根据作者关键词搜索图书

        不区分大小写，支持模糊匹配。

        Args:
            author: 作者关键词

        Returns:
            匹配的图书列表
        """
        author_lower = author.lower().strip()

        return [
            book for book in self.books
            if author_lower in book.author.lower()
        ]

    def search_books(self, keyword: str) -> List[Book]:
        """
        全局搜索图书

        在书名、作者、ISBN 三个字段中进行模糊搜索。

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的图书列表
        """
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
        """
        更新图书信息

        只更新传入的非 None 字段，
        验证新数据并检查 ISBN 唯一性（排除自身）。

        Args:
            book_id: 要更新的图书 ID
            title: 新书名（可选）
            author: 新作者（可选）
            year: 新年份（可选）
            isbn: 新 ISBN（可选）
            publisher: 新出版社（可选）

        Returns:
            更新后的 Book 实例，图书不存在返回 None

        Raises:
            InvalidInputError: 输入数据无效时抛出
            DuplicateIsbnError: 新 ISBN 已被其他图书使用时抛出
        """
        book = self.find_book_by_id(book_id)
        if not book:
            return None

        if title is not None:
            title = title.strip()
            if not title:
                raise InvalidInputError("书名不能为空")
            book.title = title

        if author is not None:
            author = author.strip()
            if not author:
                raise InvalidInputError("作者不能为空")
            book.author = author

        if year is not None:
            if year <= 0:
                raise InvalidInputError("年份必须是正整数")
            book.year = year

        if isbn is not None:
            isbn = isbn.strip()
            if self._is_isbn_taken(isbn, exclude_book_id=book_id):
                raise DuplicateIsbnError(f"ISBN {isbn} 已存在")
            book.isbn = isbn

        if publisher is not None:
            book.publisher = publisher.strip()

        self.storage.save(self.books)
        return book

    def get_all_books(self) -> List[Book]:
        """
        获取所有图书列表

        Returns:
            所有图书的副本列表（防止外部直接修改内部数据）
        """
        return list(self.books)

    def count_books_by_author(self, author: str) -> int:
        """
        统计指定作者的藏书数量

        Args:
            author: 作者姓名或关键词

        Returns:
            该作者的藏书数量
        """
        return len(self.find_books_by_author(author))

    def get_author_statistics(self) -> List[Dict]:
        """
        获取作者统计排名

        统计每个作者的藏书数量，按数量降序排列。

        Returns:
            作者统计列表，每项包含 author 和 count 字段
        """
        author_counts: Dict[str, int] = {}

        for book in self.books:
            author = book.author.strip()
            author_counts[author] = author_counts.get(author, 0) + 1

        statistics = [
            {"author": author, "count": count}
            for author, count in author_counts.items()
        ]

        statistics.sort(key=lambda x: x["count"], reverse=True)
        return statistics

    def create_backup(self) -> Optional[str]:
        """
        创建当前数据的备份

        Returns:
            备份文件路径，失败返回 None
        """
        return self.storage.create_backup()

    def list_backups(self) -> List[str]:
        """
        获取所有备份文件列表

        Returns:
            备份文件路径列表，按时间倒序排列
        """
        return self.storage.list_backups()

    def restore_from_backup(self, backup_path: str) -> bool:
        """
        从指定备份文件恢复数据

        恢复后会重新从存储加载数据到内存。

        Args:
            backup_path: 备份文件的完整路径

        Returns:
            恢复成功返回 True，失败返回 False
        """
        success = self.storage.restore_from_backup(backup_path)
        if success:
            self.books = self.storage.load()
        return success

    def get_latest_backup(self) -> Optional[str]:
        """
        获取最新的备份文件路径

        Returns:
            最新备份文件路径，无备份返回 None
        """
        return self.storage.get_latest_backup()

    def export_to_csv(self, file_path: str) -> int:
        """
        将所有图书导出到CSV文件

        与JSON存储完全独立，使用单独的CSV存储模块。

        Args:
            file_path: 导出的CSV文件路径

        Returns:
            导出的图书数量

        Raises:
            CsvStorageError: 导出失败时抛出
        """
        csv_storage = CsvStorage(file_path)
        count = csv_storage.export_books(self.books)
        return count

    def preview_csv_import(self, file_path: str, max_rows: int = 5) -> Dict[str, Any]:
        """
        预览CSV文件内容，用于导入前检查

        Args:
            file_path: CSV文件路径
            max_rows: 最多预览的行数

        Returns:
            包含预览信息的字典
        """
        csv_storage = CsvStorage(file_path)
        return csv_storage.preview_csv(max_rows)

    def import_from_csv(
        self,
        file_path: str,
        skip_existing_isbn: bool = True,
        skip_duplicates_in_file: bool = True,
    ) -> Tuple[int, int, List[str]]:
        """
        从CSV文件导入图书

        与JSON存储配合使用：导入的图书会添加到现有库中，
        并通过JSON存储持久化。

        Args:
            file_path: CSV文件路径
            skip_existing_isbn: 是否跳过书库中已存在的ISBN
            skip_duplicates_in_file: 是否跳过CSV文件内部重复的ISBN

        Returns:
            元组: (成功导入数量, 跳过/失败数量, 警告信息列表)

        Raises:
            CsvStorageError: 导入失败时抛出
            CsvInvalidFormatError: CSV格式错误时抛出
        """
        csv_storage = CsvStorage(file_path)
        imported_books, failed_rows, warnings = csv_storage.import_books(
            skip_duplicates=skip_duplicates_in_file
        )

        success_count = 0
        skipped_count = 0
        final_warnings = list(warnings)

        for book in imported_books:
            try:
                if book.isbn and skip_existing_isbn:
                    if self._is_isbn_taken(book.isbn):
                        skipped_count += 1
                        final_warnings.append(
                            f"ISBN '{book.isbn}' 在书库中已存在，已跳过: 《{book.title}》"
                        )
                        continue

                if book.book_id:
                    if self.find_book_by_id(book.book_id):
                        new_id = str(uuid.uuid4())[:8]
                        final_warnings.append(
                            f"图书ID '{book.book_id}' 已存在，已自动生成新ID: {new_id}"
                        )
                        book.book_id = new_id
                else:
                    book.book_id = str(uuid.uuid4())[:8]

                self.books.append(book)
                success_count += 1

            except Exception as error:
                skipped_count += 1
                final_warnings.append(
                    f"导入失败: 《{book.title}》- {error}"
                )

        if success_count > 0:
            self.storage.save(self.books)

        total_failed = skipped_count + len(failed_rows)
        return success_count, total_failed, final_warnings
