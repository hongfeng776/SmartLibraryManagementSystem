"""
JSON 存储模块

负责图书数据的持久化存储和备份恢复功能。
使用 JSON 格式存储数据，支持自动创建目录、
错误处理、数据备份和恢复等功能。
"""

import json
import os
import shutil
from datetime import datetime
from typing import List, Optional

from models.book import Book


class JsonStorage:
    """
    JSON 存储管理器

    提供图书数据的加载、保存、备份和恢复功能。
    自动处理数据文件路径、目录创建和异常处理。

    Attributes:
        file_path: 主数据文件的完整路径
        backup_dir: 备份文件存放目录的完整路径
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

        self.backup_dir = os.path.join(os.path.dirname(self.file_path), "backups")

    def load(self) -> List[Book]:
        """
        从 JSON 文件加载图书数据

        处理多种异常情况：
        - 文件不存在：返回空列表
        - JSON 格式错误：返回空列表并打印警告
        - 单条记录损坏：跳过损坏记录继续加载

        Returns:
            图书对象列表，加载失败时返回空列表
        """
        if not os.path.exists(self.file_path):
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                print(f"警告: 数据文件格式错误，将使用空列表。文件: {self.file_path}")
                return []

            books: List[Book] = []
            for item in data:
                try:
                    if isinstance(item, dict):
                        books.append(Book.from_dict(item))
                except (KeyError, TypeError, ValueError) as error:
                    print(f"警告: 跳过损坏的图书记录: {error}")

            return books

        except json.JSONDecodeError as error:
            print(f"错误: 数据文件JSON格式损坏，将使用空列表。文件: {self.file_path}")
            print(f"       错误详情: {error}")
            return []

        except Exception as error:
            print(f"错误: 读取数据文件时发生异常，将使用空列表。")
            print(f"       错误详情: {error}")
            return []

    def save(self, books: List[Book]) -> None:
        """
        将图书数据保存到 JSON 文件

        自动创建不存在的目录，使用 UTF-8 编码和缩进格式化输出。

        Args:
            books: 要保存的图书对象列表
        """
        try:
            data = [book.to_dict() for book in books]
            directory = os.path.dirname(self.file_path)

            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)

        except Exception as error:
            print(f"错误: 保存数据失败。")
            print(f"       文件: {self.file_path}")
            print(f"       错误详情: {error}")

    def create_backup(self) -> Optional[str]:
        """
        创建当前数据的备份

        备份文件命名格式：books_backup_YYYYMMDD_HHMMSS_MS.json
        包含毫秒级时间戳，避免同一秒内的备份覆盖。

        Returns:
            备份文件的完整路径，创建失败时返回 None
        """
        try:
            if not os.path.exists(self.file_path):
                return None

            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            backup_file_name = f"{base_name}_backup_{timestamp}.json"
            backup_path = os.path.join(self.backup_dir, backup_file_name)

            shutil.copy2(self.file_path, backup_path)
            return backup_path

        except Exception as error:
            print(f"错误: 创建备份失败。")
            print(f"       错误详情: {error}")
            return None

    def list_backups(self) -> List[str]:
        """
        获取所有备份文件列表

        返回按时间倒序排列的备份文件路径列表，
        最新的备份排在最前面。

        Returns:
            备份文件路径列表，无备份时返回空列表
        """
        try:
            if not os.path.exists(self.backup_dir):
                return []

            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            backups: List[str] = []

            for file_name in os.listdir(self.backup_dir):
                if file_name.startswith(f"{base_name}_backup_") and file_name.endswith(".json"):
                    backup_path = os.path.join(self.backup_dir, file_name)
                    backups.append(backup_path)

            backups.sort(reverse=True)
            return backups

        except Exception as error:
            print(f"错误: 获取备份列表失败。")
            print(f"       错误详情: {error}")
            return []

    def restore_from_backup(self, backup_path: str) -> bool:
        """
        从指定备份文件恢复数据

        恢复前会自动创建当前数据的备份，防止误操作导致数据丢失。

        Args:
            backup_path: 备份文件的完整路径

        Returns:
            恢复成功返回 True，失败返回 False
        """
        try:
            if not os.path.exists(backup_path):
                print(f"错误: 备份文件不存在: {backup_path}")
                return False

            self.create_backup()
            shutil.copy2(backup_path, self.file_path)
            return True

        except Exception as error:
            print(f"错误: 恢复备份失败。")
            print(f"       错误详情: {error}")
            return False

    def get_latest_backup(self) -> Optional[str]:
        """
        获取最新的备份文件路径

        Returns:
            最新备份文件的完整路径，无备份时返回 None
        """
        backups = self.list_backups()
        return backups[0] if backups else None
