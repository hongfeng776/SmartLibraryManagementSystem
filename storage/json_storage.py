"""
JSON 存储模块

负责图书数据的持久化存储和备份恢复功能。
使用 JSON 格式存储数据，支持自动创建目录、
错误处理、数据备份和恢复等功能。
"""

import os
from typing import List, Optional

from models.book import Book
from storage.storage_utils import (
    write_json_atomic,
    read_json_safe,
    create_file_backup,
    list_backup_files,
    restore_from_backup,
    get_latest_backup,
    create_empty_json_file,
    get_base_name,
)


class JsonStorage:
    """
    JSON 存储管理器

    提供图书数据的加载、保存、备份和恢复功能。
    自动处理数据文件路径、目录创建和异常处理。

    Attributes:
        file_path: 主数据文件的完整路径
        backup_dir: 备份文件存放目录的完整路径
        base_name: 文件基础名称（不含扩展名）
    """

    def __init__(self, file_path: str = "books.json") -> None:
        """
        初始化存储管理器

        Args:
            file_path: 数据文件路径，可以是相对路径或绝对路径。
                       如果是相对路径，将解析到项目根目录下。
        """
        if os.path.isabs(file_path):
            self.file_path = file_path
        else:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.file_path = os.path.join(project_root, file_path)

        self.base_name = get_base_name(self.file_path)
        self.backup_dir = os.path.join(os.path.dirname(self.file_path), "backups")

    def _create_empty_file(self) -> bool:
        """
        创建一个空的数据文件

        Returns:
            创建成功返回 True，失败返回 False
        """
        return create_empty_json_file(self.file_path)

    def _try_restore_from_backup(self) -> Optional[List[Book]]:
        """
        尝试从最新备份恢复数据

        Returns:
            成功恢复返回图书列表，失败返回 None
        """
        latest_backup = self.get_latest_backup()
        if not latest_backup:
            return None

        print("[WARNING] Data file corrupted, trying to restore from latest backup...")
        print(f"         Backup file: {latest_backup}")

        data = read_json_safe(latest_backup)
        if data is None or not isinstance(data, list):
            print(f"警告: 备份文件格式错误，恢复失败。")
            return None

        books: List[Book] = []
        for item in data:
            try:
                if isinstance(item, dict):
                    books.append(Book.from_dict(item))
            except (KeyError, TypeError, ValueError) as error:
                print(f"警告: 跳过备份中损坏的记录: {error}")

        if self.save(books):
            print(f"[OK] Restored {len(books)} books from backup")
            return books

        return None

    def load(self) -> List[Book]:
        """
        从 JSON 文件加载图书数据

        处理多种异常情况：
        - 文件不存在：自动创建空文件并返回空列表
        - JSON 格式错误：尝试从备份恢复，失败则创建空文件
        - 单条记录损坏：跳过损坏记录继续加载

        Returns:
            图书对象列表，加载失败时返回空列表
        """
        if not os.path.exists(self.file_path):
            print("[INFO] Data file not found, creating empty file...")
            if self._create_empty_file():
                print(f"[OK] Created empty data file: {self.file_path}")
            return []

        data = read_json_safe(self.file_path)
        if data is None:
            print(f"[ERROR] Data file JSON format corrupted. File: {self.file_path}")
            restored = self._try_restore_from_backup()
            if restored is not None:
                return restored
            print("[INFO] Creating new empty data file...")
            self._create_empty_file()
            return []

        if not isinstance(data, list):
            print(f"[WARNING] Data file format error, trying to restore from backup. File: {self.file_path}")
            restored = self._try_restore_from_backup()
            if restored is not None:
                return restored
            self._create_empty_file()
            return []

        books: List[Book] = []
        for item in data:
            try:
                if isinstance(item, dict):
                    books.append(Book.from_dict(item))
            except (KeyError, TypeError, ValueError) as error:
                print(f"警告: 跳过损坏的图书记录: {error}")

        return books

    def save(self, books: List[Book]) -> bool:
        """
        将图书数据保存到 JSON 文件

        使用原子写入方式：先写入临时文件，成功后再替换原文件。
        这样可以防止写入过程中断导致文件损坏。

        Args:
            books: 要保存的图书对象列表

        Returns:
            保存成功返回 True，失败返回 False
        """
        data = [book.to_dict() for book in books]
        return write_json_atomic(self.file_path, data)

    def create_backup(self) -> Optional[str]:
        """
        创建当前数据的备份

        备份文件命名格式：books_backup_YYYYMMDD_HHMMSS_MS.json

        Returns:
            备份文件的完整路径，创建失败时返回 None
        """
        return create_file_backup(self.file_path, self.backup_dir)

    def list_backups(self) -> List[str]:
        """
        获取所有备份文件列表

        返回按时间倒序排列的备份文件路径列表，
        最新的备份排在最前面。

        Returns:
            备份文件路径列表，无备份时返回空列表
        """
        return list_backup_files(self.backup_dir, self.base_name)

    def restore_from_backup(self, backup_path: str) -> bool:
        """
        从指定备份文件恢复数据

        恢复前会自动创建当前数据的备份，防止误操作导致数据丢失。

        Args:
            backup_path: 备份文件的完整路径

        Returns:
            恢复成功返回 True，失败返回 False
        """
        return restore_from_backup(backup_path, self.file_path, create_backup_before_restore=True)

    def get_latest_backup(self) -> Optional[str]:
        """
        获取最新的备份文件路径

        Returns:
            最新备份文件的完整路径，无备份时返回 None
        """
        return get_latest_backup(self.backup_dir, self.base_name)
