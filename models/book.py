"""
图书数据模型模块

定义图书数据结构和序列化/反序列化方法，
用于在内存和持久化存储之间转换图书数据。
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class Book:
    """
    图书数据模型类

    使用 dataclass 简化图书对象的定义，
    包含图书的基本属性和序列化方法。

    Attributes:
        book_id: 图书唯一标识符（8位UUID）
        title: 图书标题
        author: 作者姓名
        year: 出版年份
        isbn: ISBN编号（可选）
        publisher: 出版社名称（可选）
    """

    book_id: str
    title: str
    author: str
    year: int
    isbn: str = ""
    publisher: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """
        将图书对象转换为字典格式

        用于序列化为 JSON 存储。

        Returns:
            包含图书所有属性的字典
        """
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "isbn": self.isbn,
            "publisher": self.publisher,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Book":
        """
        从字典数据创建图书对象

        用于从 JSON 反序列化。

        Args:
            data: 包含图书属性的字典

        Returns:
            新创建的 Book 实例

        Raises:
            KeyError: 缺少必需字段时抛出
            TypeError: 字段类型不匹配时抛出
        """
        return cls(
            book_id=data["book_id"],
            title=data["title"],
            author=data["author"],
            year=data["year"],
            isbn=data.get("isbn", ""),
            publisher=data.get("publisher", ""),
        )
