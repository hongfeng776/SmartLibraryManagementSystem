"""
CSV 存储模块

负责图书数据的CSV格式导入和导出功能。
与JSON存储完全独立，用于批量数据交换和备份。
"""

import csv
import os
from typing import List, Dict, Any, Optional
from models.book import Book


class CsvStorageError(Exception):
    pass


class CsvInvalidFormatError(CsvStorageError):
    pass


class CsvStorage:
    """
    CSV 存储管理器

    提供图书数据的CSV导入和导出功能。
    支持标准CSV格式，可与Excel等软件兼容。

    CSV格式说明：
    - 必需列: title, author, year
    - 可选列: isbn, publisher, book_id
    - 如果没有book_id列，导入时会自动生成
    """

    REQUIRED_FIELDS = ["title", "author", "year"]
    OPTIONAL_FIELDS = ["isbn", "publisher", "book_id"]
    ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS

    def __init__(self, file_path: str = "books_export.csv") -> None:
        """
        初始化CSV存储管理器

        Args:
            file_path: CSV文件路径，可以是相对路径或绝对路径。
                       如果是相对路径，将解析到当前工作目录。
        """
        if os.path.isabs(file_path):
            self.file_path = file_path
        else:
            self.file_path = os.path.abspath(file_path)

    def export_books(self, books: List[Book]) -> int:
        """
        将图书列表导出到CSV文件

        Args:
            books: 要导出的图书对象列表

        Returns:
            导出的图书数量

        Raises:
            CsvStorageError: 导出失败时抛出
        """
        try:
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            fieldnames = ["book_id", "title", "author", "year", "isbn", "publisher"]

            with open(self.file_path, "w", encoding="utf-8-sig", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()

                count = 0
                for book in books:
                    writer.writerow({
                        "book_id": book.book_id,
                        "title": book.title,
                        "author": book.author,
                        "year": book.year,
                        "isbn": book.isbn,
                        "publisher": book.publisher,
                    })
                    count += 1

                return count

        except PermissionError:
            raise CsvStorageError(f"没有权限写入文件: {self.file_path}")
        except Exception as error:
            raise CsvStorageError(f"导出CSV失败: {error}")

    def import_books(self, skip_duplicates: bool = True) -> tuple[List[Book], List[Dict[str, Any]], List[str]]:
        """
        从CSV文件导入图书数据

        Args:
            skip_duplicates: 是否跳过重复ISBN的图书

        Returns:
            元组: (成功导入的图书列表, 失败的行列表, 警告信息列表)

        Raises:
            CsvStorageError: 文件不存在或格式错误时抛出
            CsvInvalidFormatError: CSV格式不符合要求时抛出
        """
        if not os.path.exists(self.file_path):
            raise CsvStorageError(f"CSV文件不存在: {self.file_path}")

        warnings: List[str] = []
        failed_rows: List[Dict[str, Any]] = []
        imported_books: List[Book] = []
        seen_isbns: set = set()

        try:
            with open(self.file_path, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)

                if reader.fieldnames is None:
                    raise CsvInvalidFormatError("CSV文件为空或没有表头")

                fieldnames_lower = {fn.lower(): fn for fn in reader.fieldnames}

                missing_fields = []
                for required in self.REQUIRED_FIELDS:
                    if required.lower() not in fieldnames_lower:
                        missing_fields.append(required)

                if missing_fields:
                    raise CsvInvalidFormatError(
                        f"CSV文件缺少必需的列: {', '.join(missing_fields)}。"
                        f"必需列: {', '.join(self.REQUIRED_FIELDS)}"
                    )

                field_mapping = {
                    "title": fieldnames_lower.get("title", "title"),
                    "author": fieldnames_lower.get("author", "author"),
                    "year": fieldnames_lower.get("year", "year"),
                    "isbn": fieldnames_lower.get("isbn", "isbn"),
                    "publisher": fieldnames_lower.get("publisher", "publisher"),
                    "book_id": fieldnames_lower.get("book_id", "book_id"),
                }

                for row_num, row in enumerate(reader, start=2):
                    try:
                        title = str(row.get(field_mapping["title"], "")).strip()
                        author = str(row.get(field_mapping["author"], "")).strip()
                        year_str = str(row.get(field_mapping["year"], "")).strip()
                        isbn = str(row.get(field_mapping["isbn"], "")).strip()
                        publisher = str(row.get(field_mapping["publisher"], "")).strip()
                        book_id = str(row.get(field_mapping["book_id"], "")).strip()

                        if not title:
                            raise ValueError("书名为空")
                        if not author:
                            raise ValueError("作者为空")
                        if not year_str:
                            raise ValueError("年份为空")

                        try:
                            year = int(year_str)
                            if year <= 0:
                                raise ValueError("年份必须是正整数")
                        except ValueError:
                            raise ValueError(f"年份 '{year_str}' 不是有效的整数")

                        if isbn and skip_duplicates:
                            if isbn in seen_isbns:
                                warnings.append(
                                    f"第 {row_num} 行: ISBN '{isbn}' 重复，已跳过"
                                )
                                failed_rows.append({
                                    "row_num": row_num,
                                    "data": row,
                                    "error": f"ISBN重复: {isbn}"
                                })
                                continue
                            seen_isbns.add(isbn)

                        book = Book(
                            book_id=book_id,
                            title=title,
                            author=author,
                            year=year,
                            isbn=isbn,
                            publisher=publisher,
                        )

                        imported_books.append(book)

                    except Exception as error:
                        failed_rows.append({
                            "row_num": row_num,
                            "data": row,
                            "error": str(error)
                        })
                        warnings.append(f"第 {row_num} 行: {error}")

            return imported_books, failed_rows, warnings

        except CsvInvalidFormatError:
            raise
        except PermissionError:
            raise CsvStorageError(f"没有权限读取文件: {self.file_path}")
        except csv.Error as error:
            raise CsvStorageError(f"CSV格式错误: {error}")
        except Exception as error:
            raise CsvStorageError(f"导入CSV失败: {error}")

    def preview_csv(self, max_rows: int = 5) -> Dict[str, Any]:
        """
        预览CSV文件内容，用于导入前检查

        Args:
            max_rows: 最多预览的行数

        Returns:
            包含预览信息的字典
        """
        if not os.path.exists(self.file_path):
            return {
                "exists": False,
                "path": self.file_path,
            }

        try:
            with open(self.file_path, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames or []

                rows = []
                for i, row in enumerate(reader):
                    if i >= max_rows:
                        break
                    rows.append(row)

                file.seek(0)
                reader = csv.DictReader(file)
                total_rows = sum(1 for _ in reader)

                return {
                    "exists": True,
                    "path": self.file_path,
                    "headers": list(headers),
                    "total_rows": total_rows,
                    "preview_rows": rows,
                    "required_fields_present": all(
                        rf.lower() in [h.lower() for h in headers]
                        for rf in self.REQUIRED_FIELDS
                    ),
                }

        except Exception as error:
            return {
                "exists": True,
                "path": self.file_path,
                "error": str(error),
            }
