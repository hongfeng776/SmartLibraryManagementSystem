"""
智能图书管理系统 - 主入口文件

这是一个基于命令行的图书管理系统，
支持图书的增删改查、统计分析和数据备份恢复等功能。

项目采用分层架构设计：
- models:      数据模型层
- storage:     数据存储层
- services:    业务逻辑层
- ui:          用户界面层
"""

from storage.json_storage import JsonStorage
from services.library_service import LibraryService
from ui.console_ui import ConsoleUI


def main() -> None:
    """
    应用程序入口函数

    初始化各层组件并启动用户界面。
    依赖注入：Storage -> Service -> UI
    """
    storage = JsonStorage()
    service = LibraryService(storage)
    ui = ConsoleUI(service)
    ui.run()


if __name__ == "__main__":
    main()
