"""
UI工具模块

提供用户界面相关的工具函数，
处理路径操作、格式化等通用功能。
"""

import os


def get_file_name_from_path(file_path: str) -> str:
    """
    从文件路径中提取文件名

    跨平台支持Windows和Unix路径分隔符。

    Args:
        file_path: 文件路径

    Returns:
        文件名
    """
    if "\\" in file_path:
        return file_path.split("\\")[-1]
    return file_path.split("/")[-1]


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小为人类可读格式

    Args:
        size_bytes: 文件大小（字节）

    Returns:
        格式化后的文件大小字符串
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def ensure_file_extension(file_path: str, default_ext: str) -> str:
    """
    确保文件路径有指定的扩展名

    Args:
        file_path: 文件路径
        default_ext: 默认扩展名（不含点）

    Returns:
        带有扩展名的文件路径
    """
    ext = f".{default_ext}"
    if not file_path.lower().endswith(ext):
        return file_path + ext
    return file_path


def is_valid_file_name(name: str) -> bool:
    """
    检查文件名是否有效（不包含非法字符）

    Args:
        name: 文件名

    Returns:
        有效返回 True，否则返回 False
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        if char in name:
            return False
    return True


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断文本到指定长度

    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀

    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
