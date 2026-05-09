"""
存储工具模块

提供文件操作、备份管理等通用功能，
供不同存储实现复用。
"""

import json
import os
import shutil
import tempfile
from datetime import datetime
from typing import Any, List, Optional


def ensure_directory_exists(directory: str) -> bool:
    """
    确保目录存在，不存在则创建

    Args:
        directory: 目录路径

    Returns:
        创建成功或已存在返回 True，失败返回 False
    """
    if not directory:
        return True

    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except OSError:
        return False


def write_json_atomic(file_path: str, data: Any) -> bool:
    """
    原子写入JSON文件

    使用临时文件+重命名方式确保写入原子性，
    防止写入中断导致文件损坏。

    Args:
        file_path: 目标文件路径
        data: 要写入的数据（可JSON序列化）

    Returns:
        写入成功返回 True，失败返回 False
    """
    directory = os.path.dirname(file_path)
    if not ensure_directory_exists(directory):
        return False

    file_dir = directory or "."

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=file_dir,
            prefix=".temp_",
            suffix=".json",
            delete=False
        ) as temp_file:
            json.dump(data, temp_file, ensure_ascii=False, indent=2)
            temp_path = temp_file.name

        try:
            os.replace(temp_path, file_path)
            return True
        except Exception:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            raise

    except Exception:
        return False


def read_json_safe(file_path: str) -> Optional[Any]:
    """
    安全读取JSON文件

    Args:
        file_path: 文件路径

    Returns:
        成功返回解析后的数据，失败返回 None
    """
    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return None


def generate_backup_filename(base_name: str) -> str:
    """
    生成备份文件名

    格式：{base_name}_backup_YYYYMMDD_HHMMSS_MS.json

    Args:
        base_name: 基础文件名（不含扩展名）

    Returns:
        备份文件名
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    return f"{base_name}_backup_{timestamp}.json"


def create_file_backup(source_path: str, backup_dir: str) -> Optional[str]:
    """
    创建文件备份

    Args:
        source_path: 源文件路径
        backup_dir: 备份目录

    Returns:
        备份文件路径，失败返回 None
    """
    if not os.path.exists(source_path):
        return None

    if not ensure_directory_exists(backup_dir):
        return None

    try:
        base_name = os.path.splitext(os.path.basename(source_path))[0]
        backup_file_name = generate_backup_filename(base_name)
        backup_path = os.path.join(backup_dir, backup_file_name)

        shutil.copy2(source_path, backup_path)
        return backup_path

    except Exception:
        return None


def list_backup_files(backup_dir: str, base_name: str) -> List[str]:
    """
    列出指定目录下的备份文件

    Args:
        backup_dir: 备份目录
        base_name: 基础文件名（不含扩展名）

    Returns:
        按时间倒序排列的备份文件路径列表
    """
    if not os.path.exists(backup_dir):
        return []

    try:
        backups: List[str] = []
        prefix = f"{base_name}_backup_"

        for file_name in os.listdir(backup_dir):
            if file_name.startswith(prefix) and file_name.endswith(".json"):
                backup_path = os.path.join(backup_dir, file_name)
                backups.append(backup_path)

        backups.sort(reverse=True)
        return backups

    except Exception:
        return []


def get_latest_backup(backup_dir: str, base_name: str) -> Optional[str]:
    """
    获取最新的备份文件

    Args:
        backup_dir: 备份目录
        base_name: 基础文件名（不含扩展名）

    Returns:
        最新备份文件路径，无备份返回 None
    """
    backups = list_backup_files(backup_dir, base_name)
    return backups[0] if backups else None


def restore_from_backup(
    backup_path: str,
    target_path: str,
    create_backup_before_restore: bool = True
) -> bool:
    """
    从备份恢复文件

    Args:
        backup_path: 备份文件路径
        target_path: 目标文件路径
        create_backup_before_restore: 恢复前是否创建当前文件的备份

    Returns:
        恢复成功返回 True，失败返回 False
    """
    if not os.path.exists(backup_path):
        return False

    try:
        if create_backup_before_restore and os.path.exists(target_path):
            backup_dir = os.path.join(os.path.dirname(target_path), "backups")
            create_file_backup(target_path, backup_dir)

        shutil.copy2(backup_path, target_path)
        return True

    except Exception:
        return False


def create_empty_json_file(file_path: str) -> bool:
    """
    创建空的JSON文件（内容为 []）

    Args:
        file_path: 文件路径

    Returns:
        创建成功返回 True，失败返回 False
    """
    return write_json_atomic(file_path, [])


def get_base_name(file_path: str) -> str:
    """
    获取文件的基础名称（不含路径和扩展名）

    Args:
        file_path: 文件路径

    Returns:
        基础文件名
    """
    return os.path.splitext(os.path.basename(file_path))[0]
