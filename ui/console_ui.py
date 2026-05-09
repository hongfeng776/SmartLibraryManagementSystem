"""
控制台用户界面模块

提供图书管理系统的命令行交互界面，
包含菜单展示、用户输入处理、数据展示等功能。
"""

from typing import Optional

from models.book import Book
from services.library_service import (
    LibraryService,
    DuplicateIsbnError,
    InvalidInputError,
)
from storage.csv_storage import CsvStorageError, CsvInvalidFormatError
from ui.ui_utils import get_file_name_from_path


class ConsoleUI:
    """
    控制台用户界面类

    负责处理与用户的所有交互，
    包括菜单展示、输入验证、调用服务层方法和结果展示。

    Attributes:
        service: 图书管理服务实例
        LINE: 粗分割线（50 个等号）
        THIN_LINE: 细分割线（50 个减号）
    """

    LINE = "=" * 50
    THIN_LINE = "-" * 50

    def __init__(self, service: LibraryService) -> None:
        """
        初始化控制台界面

        Args:
            service: LibraryService 实例，用于处理业务逻辑
        """
        self.service = service

    def run(self) -> None:
        """
        启动应用程序主循环

        显示欢迎信息，然后进入主菜单循环处理用户输入。
        支持 KeyboardInterrupt 和 EOFError 异常的优雅退出。
        """
        book_count = self.service.get_book_count()

        self._clear_section()
        print("  📚 欢迎使用智能图书管理系统！")

        if book_count > 0:
            print(f"  ℹ️  已加载 {book_count} 条图书记录")
        else:
            print("  ℹ️  当前书库为空，快去添加一些图书吧！")

        try:
            while True:
                self._print_main_menu()
                choice = input("\n  👉 请选择操作 (1-9): ").strip()

                if choice == "1":
                    self._add_book()
                elif choice == "2":
                    self._search_books()
                elif choice == "3":
                    self._update_book()
                elif choice == "4":
                    self._delete_book()
                elif choice == "5":
                    self._list_all_books()
                elif choice == "6":
                    self._show_statistics()
                elif choice == "7":
                    self._show_backup_menu()
                elif choice == "8":
                    self._show_csv_menu()
                elif choice == "9":
                    self._shutdown()
                    break
                else:
                    self._print_error("无效选项，请输入 1-9 之间的数字哦")

                input("\n  按回车键返回主菜单...")

        except KeyboardInterrupt:
            self._clear_section()
            print("\n  ⚠️  检测到中断，正在保存数据并退出...")
            self._shutdown()

        except EOFError:
            self._clear_section()
            print("\n  ⚠️  输入流已结束，正在保存数据并退出...")
            self._shutdown()

    def _shutdown(self) -> None:
        """
        关闭程序

        保存数据并显示告别信息。
        """
        try:
            self.service.flush()
            print("  ✅ 数据已保存。")

            if self.service.get_book_count() > 0:
                backup_path = self.service.create_backup()
                if backup_path:
                    print(f"  💾 已自动创建备份: {backup_path}")

            print("  👋 再见！")
        except Exception as error:
            self._print_error(f"保存数据时出错: {error}")

    def _clear_section(self) -> None:
        """
        打印分割线，用于分隔不同的界面区域
        """
        print()
        print(self.LINE)

    def _print_success(self, message: str) -> None:
        """
        打印成功信息

        Args:
            message: 要显示的成功信息
        """
        print(f"  ✅ {message}")

    def _print_error(self, message: str) -> None:
        """
        打印错误信息

        Args:
            message: 要显示的错误信息
        """
        print(f"  ❌ {message}")

    def _print_info(self, message: str) -> None:
        """
        打印提示信息

        Args:
            message: 要显示的提示信息
        """
        print(f"  ℹ️  {message}")

    def _print_warning(self, message: str) -> None:
        """
        打印警告信息

        Args:
            message: 要显示的警告信息
        """
        print(f"  ⚠️  {message}")

    def _print_main_menu(self) -> None:
        """
        打印主菜单
        """
        self._clear_section()
        print("  📖         图书管理系统          📖")
        print(self.LINE)
        print("  1️⃣  ➕ 添加图书")
        print("  2️⃣  🔍 搜索图书")
        print("  3️⃣  ✏️  修改图书信息")
        print("  4️⃣  🗑️  删除图书")
        print("  5️⃣  📋 查看所有图书")
        print("  6️⃣  📊 统计信息")
        print("  7️⃣  💾 备份与恢复")
        print("  8️⃣  � CSV导入导出")
        print("  9️⃣  � 退出系统")
        print(self.LINE)

    def _input_int(
        self,
        prompt: str,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
    ) -> Optional[int]:
        """
        获取整数输入

        验证输入是否为有效整数，并可选择验证取值范围。

        Args:
            prompt: 输入提示信息
            min_value: 允许的最小值（可选）
            max_value: 允许的最大值（可选）

        Returns:
            输入的整数，输入无效时返回 None
        """
        raw_input = input(f"  {prompt}").strip()

        if not raw_input:
            return None

        try:
            value = int(raw_input)
        except ValueError:
            self._print_error("输入无效，请输入数字哦")
            return None

        if min_value is not None and value < min_value:
            self._print_error(f"输入无效，不能小于 {min_value}")
            return None

        if max_value is not None and value > max_value:
            self._print_error(f"输入无效，不能大于 {max_value}")
            return None

        return value

    def _input_required(self, prompt: str) -> Optional[str]:
        """
        获取必填字符串输入

        Args:
            prompt: 输入提示信息

        Returns:
            输入的字符串，输入为空时返回 None
        """
        value = input(f"  {prompt}").strip()

        if not value:
            self._print_error("这里不能为空哦")
            return None

        return value

    def _input_choice(self, prompt: str, choices: list[str]) -> Optional[str]:
        """
        获取选项输入

        验证输入是否在允许的选项列表中。

        Args:
            prompt: 输入提示信息
            choices: 允许的选项列表

        Returns:
            输入的选项，输入无效时返回 None
        """
        value = input(f"  {prompt}").strip()

        if value not in choices:
            self._print_error(f"输入无效，请选择: {', '.join(choices)}")
            return None

        return value

    def _add_book(self) -> None:
        """
        添加新图书功能

        引导用户输入图书信息，验证输入，
        调用服务层添加图书并显示结果。
        """
        self._clear_section()
        print("  ➕ 添加图书")
        print(self.THIN_LINE)

        title = self._input_required("📕 书名: ")
        if not title:
            return

        author = self._input_required("✍️  作者: ")
        if not author:
            return

        isbn = input("  📝 ISBN (回车跳过): ").strip()
        publisher = input("  🏢 出版社 (回车跳过): ").strip()

        year = self._input_int("📅 出版年份: ", min_value=1)
        if year is None:
            return

        try:
            new_book = self.service.add_book(title, author, year, isbn, publisher)
            self._print_success(f"图书添加成功！图书ID: {new_book.book_id}")
        except DuplicateIsbnError as error:
            self._print_error(f"添加失败，ISBN 已存在: {error}")
        except InvalidInputError as error:
            self._print_error(f"输入有误: {error}")

    def _search_books(self) -> None:
        """
        搜索图书功能

        提供多种搜索方式：按书名、按作者、按 ISBN、全局搜索。
        """
        self._clear_section()
        print("  🔍 搜索图书")
        print(self.THIN_LINE)

        print("  请选择搜索方式:")
        print("  1️⃣  按书名搜索")
        print("  2️⃣  按作者搜索")
        print("  3️⃣  按 ISBN 搜索")
        print("  4️⃣  全局搜索（书名/作者/ISBN）")

        mode = self._input_choice("请选择 (1-4): ", ["1", "2", "3", "4"])
        if not mode:
            return

        results: list[Book] = []
        search_type = ""

        if mode == "1":
            keyword = self._input_required("请输入书名关键词: ")
            if not keyword:
                return
            results = self.service.find_books_by_title(keyword)
            search_type = "书名"

        elif mode == "2":
            keyword = self._input_required("请输入作者关键词: ")
            if not keyword:
                return
            results = self.service.find_books_by_author(keyword)
            search_type = "作者"

        elif mode == "3":
            keyword = self._input_required("请输入 ISBN: ")
            if not keyword:
                return
            book = self.service.find_book_by_isbn(keyword)
            if book:
                results = [book]
            search_type = "ISBN"

        elif mode == "4":
            keyword = self._input_required("请输入关键词: ")
            if not keyword:
                return
            results = self.service.search_books(keyword)
            search_type = "全局"

        if results:
            self._print_info(f"按{search_type}搜索，找到 {len(results)} 本匹配的图书:")
            self._print_book_list(results)
        else:
            self._print_info(f"按{search_type}搜索，没有找到匹配的图书，换个关键词试试？")

    def _update_book(self) -> None:
        """
        修改图书信息功能

        先按书名或 ISBN 查找图书，
        然后允许用户修改各个字段（直接回车表示不修改）。
        """
        self._clear_section()
        print("  ✏️  修改图书信息")
        print(self.THIN_LINE)

        print("  请选择查找方式:")
        print("  1️⃣  按书名查找")
        print("  2️⃣  按 ISBN 查找")

        mode = self._input_choice("请选择 (1/2): ", ["1", "2"])
        if not mode:
            return

        target_book = None

        if mode == "1":
            title = self._input_required("请输入书名: ")
            if not title:
                return

            matches = self.service.find_books_by_title(title)
            if not matches:
                self._print_info("没有找到匹配的图书")
                return

            if len(matches) == 1:
                target_book = matches[0]
            else:
                self._print_info(f"找到 {len(matches)} 本匹配的图书:")
                self._print_book_list(matches)
                book_id = self._input_required("请输入要修改的图书ID: ")
                if not book_id:
                    return
                valid_ids = [book.book_id for book in matches]
                if book_id not in valid_ids:
                    self._print_error("输入的ID不在搜索结果中，请重新操作")
                    return
                target_book = self.service.find_book_by_id(book_id)

        elif mode == "2":
            isbn = self._input_required("请输入 ISBN: ")
            if not isbn:
                return
            target_book = self.service.find_book_by_isbn(isbn)

        if not target_book:
            self._print_error("没找到这本书哦")
            return

        print()
        self._print_info("当前图书信息:")
        self._print_book_detail(target_book)

        self._print_info("\n请输入新信息（直接回车表示不修改）:")
        new_title = input(f"  📕 书名 [{target_book.title}]: ").strip() or None
        new_author = input(f"  ✍️  作者 [{target_book.author}]: ").strip() or None
        new_isbn = input(f"  📝 ISBN [{target_book.isbn or '(未设置)'}]: ").strip() or None
        new_publisher = input(f"  🏢 出版社 [{target_book.publisher or '(未设置)'}]: ").strip() or None
        new_year_str = input(f"  📅 年份 [{target_book.year}]: ").strip()

        updates: dict = {}

        if new_title is not None:
            updates["title"] = new_title
        if new_author is not None:
            updates["author"] = new_author
        if new_isbn is not None:
            updates["isbn"] = new_isbn
        if new_publisher is not None:
            updates["publisher"] = new_publisher
        if new_year_str:
            try:
                updates["year"] = int(new_year_str)
            except ValueError:
                self._print_error("年份输入无效，年份未修改")

        if not updates:
            self._print_warning("没有修改任何信息")
            return

        try:
            updated_book = self.service.update_book(target_book.book_id, **updates)
            if updated_book:
                self._print_success("修改成功！")
                self._print_info("\n修改后信息:")
                self._print_book_detail(updated_book)
            else:
                self._print_error("修改失败，图书不存在")
        except DuplicateIsbnError as error:
            self._print_error(f"修改失败，ISBN 已存在: {error}")
        except InvalidInputError as error:
            self._print_error(f"输入有误: {error}")

    def _delete_book(self) -> None:
        """
        删除图书功能

        提供两种查找方式：按书名或按 ID。
        找到图书后需要用户确认才能删除。
        """
        self._clear_section()
        print("  🗑️  删除图书")
        print(self.THIN_LINE)

        print("  请选择查找方式:")
        print("  1️⃣  按书名查找")
        print("  2️⃣  按图书ID查找")

        mode = self._input_choice("请选择 (1/2): ", ["1", "2"])
        if not mode:
            return

        target_book = None

        if mode == "1":
            title = self._input_required("请输入书名: ")
            if not title:
                return

            matches = self.service.find_books_by_title(title)
            if not matches:
                self._print_info("没有找到匹配的图书")
                return

            if len(matches) == 1:
                target_book = matches[0]
            else:
                self._print_info(f"找到 {len(matches)} 本匹配的图书:")
                self._print_book_list(matches)
                book_id = self._input_required("请输入要删除的图书ID: ")
                if not book_id:
                    return
                valid_ids = [book.book_id for book in matches]
                if book_id not in valid_ids:
                    self._print_error("输入的ID不在搜索结果中，请重新操作")
                    return
                target_book = self.service.find_book_by_id(book_id)

        elif mode == "2":
            book_id = self._input_required("请输入要删除的图书ID: ")
            if not book_id:
                return
            target_book = self.service.find_book_by_id(book_id)

        if not target_book:
            self._print_error("没找到这本书哦")
            return

        print()
        self._print_info("要删除的图书信息:")
        self._print_book_detail(target_book)

        confirm = input(f"\n  ⚠️  确定要删除《{target_book.title}》吗? (y/n): ").strip().lower()

        if confirm == "y":
            success = self.service.delete_book(target_book.book_id)
            if success:
                self._print_success("删除成功！")
            else:
                self._print_error("删除失败，图书不存在")
        else:
            self._print_info("已取消删除")

    def _list_all_books(self) -> None:
        """
        列出所有图书功能

        显示图书馆中的所有图书列表。
        """
        self._clear_section()
        print("  📋 所有图书")
        print(self.THIN_LINE)

        books = self.service.get_all_books()

        if books:
            self._print_info(f"共 {len(books)} 本图书:")
            self._print_book_list(books)
        else:
            self._print_info("书库空空如也，快去添加一些图书吧！📚")

    def _show_statistics(self) -> None:
        """
        统计信息功能菜单

        提供两种统计方式：
        1. 查看所有作者统计排名
        2. 查询特定作者的藏书量
        """
        while True:
            self._clear_section()
            print("  📊 统计信息")
            print(self.THIN_LINE)

            total_books = self.service.get_book_count()
            self._print_info(f"📚 图书馆总藏书: {total_books} 本")

            print()
            print("  请选择查看方式:")
            print("  1️⃣  查看所有作者统计排名")
            print("  2️⃣  查询特定作者的藏书量")
            print("  3️⃣  返回主菜单")

            choice = input("\n  👉 请选择 (1-3): ").strip()

            if choice == "1":
                self._show_author_ranking()
                input("\n  按回车键继续...")
            elif choice == "2":
                self._query_author_books()
                input("\n  按回车键继续...")
            elif choice == "3":
                break
            else:
                self._print_error("无效选项，请输入 1-3 之间的数字")
                input("\n  按回车键继续...")

    def _show_author_ranking(self) -> None:
        """
        显示作者藏书量排名

        按藏书量降序排列，前三名显示奖牌 emoji。
        """
        author_stats = self.service.get_author_statistics()

        if author_stats:
            print()
            self._print_info("👤 作者统计（按藏书量排序）:")
            print("  " + "-" * 40)
            print(f"  {'排名':<6} {'作者':<20} {'藏书量':<8}")
            print("  " + "-" * 40)

            for rank, stat in enumerate(author_stats, 1):
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
                print(f"  {medal} {rank:<3} {stat['author']:<20} {stat['count']:<8} 本")

            print("  " + "-" * 40)
        else:
            print()
            self._print_info("暂无作者统计数据")

    def _query_author_books(self) -> None:
        """
        查询特定作者的藏书

        输入作者名，显示该作者的藏书数量和具体图书列表。
        """
        author = self._input_required("请输入作者姓名: ")
        if not author:
            return

        book_count = self.service.count_books_by_author(author)

        if book_count > 0:
            self._print_success(f"📚 作者「{author}」在图书馆共有 {book_count} 本藏书")
            books = self.service.find_books_by_author(author)
            self._print_info("📖 具体图书列表:")
            self._print_book_list(books)
        else:
            self._print_warning(f"图书馆中没有找到作者「{author}」的藏书")

    def _show_backup_menu(self) -> None:
        """
        备份与恢复功能菜单

        提供一键备份、一键恢复最新备份、查看备份历史等功能。
        """
        while True:
            self._clear_section()
            print("  💾 备份与恢复")
            print(self.THIN_LINE)

            backups = self.service.list_backups()
            backup_count = len(backups)
            self._print_info(f"📦 当前备份数量: {backup_count} 个")

            print()
            print("  请选择操作:")
            print("  1️⃣  📤 一键备份当前数据")
            print("  2️⃣  📥 一键恢复最新备份")
            print("  3️⃣  📋 查看所有备份记录")
            print("  4️⃣  🔙 返回主菜单")

            choice = input("\n  👉 请选择 (1-4): ").strip()

            if choice == "1":
                self._create_backup()
                input("\n  按回车键继续...")
            elif choice == "2":
                self._restore_latest_backup()
                input("\n  按回车键继续...")
            elif choice == "3":
                self._list_backup_history()
                input("\n  按回车键继续...")
            elif choice == "4":
                break
            else:
                self._print_error("无效选项，请输入 1-4 之间的数字")
                input("\n  按回车键继续...")

    def _create_backup(self) -> None:
        """
        一键备份当前数据
        """
        self._print_info("正在创建备份...")
        backup_path = self.service.create_backup()

        if backup_path:
            self._print_success("备份成功！✅")
            self._print_info(f"📁 备份文件: {backup_path}")
        else:
            self._print_warning("没有可备份的数据（当前书库为空）")

    def _restore_latest_backup(self) -> None:
        """
        一键恢复最新备份
        """
        latest_backup = self.service.get_latest_backup()

        if not latest_backup:
            self._print_warning("没有找到任何备份文件")
            return

        self._print_info(f"找到最新备份: {latest_backup}")

        confirm = input("\n  ⚠️  恢复备份将覆盖当前数据，确定要继续吗? (y/n): ").strip().lower()

        if confirm != "y":
            self._print_info("已取消恢复")
            return

        self._print_info("正在恢复...")
        success = self.service.restore_from_backup(latest_backup)

        if success:
            book_count = self.service.get_book_count()
            self._print_success(f"恢复成功！✅ 已恢复 {book_count} 条图书记录")
        else:
            self._print_error("恢复失败，请检查备份文件")

    def _list_backup_history(self) -> None:
        """
        查看所有备份历史并可选择恢复
        """
        backups = self.service.list_backups()

        if not backups:
            self._print_info("暂无备份记录")
            return

        self._print_info(f"📦 共找到 {len(backups)} 个备份:")
        print("  " + "-" * 60)
        print(f"  {'序号':<6} {'备份文件':<50}")
        print("  " + "-" * 60)

        for index, backup in enumerate(backups, 1):
            file_name = get_file_name_from_path(backup)
            marker = " 🔄 最新" if index == 1 else ""
            print(f"  {index:<6} {file_name:<50}{marker}")

        print("  " + "-" * 60)

        print()
        choice = input("  👉 要恢复某个备份吗？请输入序号（回车跳过）: ").strip()

        if choice:
            try:
                selected_index = int(choice) - 1

                if 0 <= selected_index < len(backups):
                    selected_backup = backups[selected_index]
                    self._print_info(f"已选择: {selected_backup}")

                    confirm = input("  ⚠️  恢复将覆盖当前数据，确定继续? (y/n): ").strip().lower()

                    if confirm == "y":
                        self._print_info("正在恢复...")
                        success = self.service.restore_from_backup(selected_backup)

                        if success:
                            book_count = self.service.get_book_count()
                            self._print_success(f"恢复成功！✅ 已恢复 {book_count} 条图书记录")
                        else:
                            self._print_error("恢复失败")
                    else:
                        self._print_info("已取消恢复")
                else:
                    self._print_error("序号无效")

            except ValueError:
                self._print_error("请输入有效的数字序号")

    def _show_csv_menu(self) -> None:
        """
        CSV导入导出功能菜单

        提供从CSV文件批量导入和导出图书数据的功能。
        """
        while True:
            self._clear_section()
            print("  📄 CSV导入导出")
            print(self.THIN_LINE)

            book_count = self.service.get_book_count()
            self._print_info(f"📚 当前书库藏书: {book_count} 本")

            print()
            print("  请选择操作:")
            print("  1️⃣  📤 导出所有图书到CSV")
            print("  2️⃣  📥 从CSV文件导入图书")
            print("  3️⃣  🔍 预览CSV文件内容")
            print("  4️⃣  🔙 返回主菜单")

            choice = input("\n  👉 请选择 (1-4): ").strip()

            if choice == "1":
                self._export_to_csv()
                input("\n  按回车键继续...")
            elif choice == "2":
                self._import_from_csv()
                input("\n  按回车键继续...")
            elif choice == "3":
                self._preview_csv_file()
                input("\n  按回车键继续...")
            elif choice == "4":
                break
            else:
                self._print_error("无效选项，请输入 1-4 之间的数字")
                input("\n  按回车键继续...")

    def _export_to_csv(self) -> None:
        """
        导出所有图书到CSV文件
        """
        book_count = self.service.get_book_count()
        if book_count == 0:
            self._print_warning("当前书库为空，没有可导出的图书")
            return

        print()
        self._print_info("💡 提示:")
        self._print_info("   - 导出的CSV文件可以用Excel或其他表格软件打开")
        self._print_info("   - UTF-8编码，支持中文")
        self._print_info("   - 默认文件名: books_export.csv")
        print()

        file_path = input("  📁 请输入导出文件路径 (回车使用默认): ").strip()
        if not file_path:
            file_path = "books_export.csv"

        try:
            self._print_info(f"正在导出到: {file_path} ...")
            exported_count = self.service.export_to_csv(file_path)
            self._print_success(f"✅ 导出成功！共导出 {exported_count} 本图书")
            self._print_info(f"📁 文件路径: {file_path}")
        except CsvStorageError as error:
            self._print_error(f"导出失败: {error}")
        except Exception as error:
            self._print_error(f"导出时发生未知错误: {error}")

    def _import_from_csv(self) -> None:
        """
        从CSV文件导入图书
        """
        print()
        self._print_info("💡 CSV格式要求:")
        self._print_info("   - 必需列: title, author, year")
        self._print_info("   - 可选列: isbn, publisher, book_id")
        self._print_info("   - 如果没有book_id列，会自动生成")
        self._print_info("   - 第一行必须是表头")
        print()

        file_path = input("  📁 请输入CSV文件路径: ").strip()
        if not file_path:
            self._print_warning("未输入文件路径")
            return

        preview = self.service.preview_csv_import(file_path)

        if not preview.get("exists", False):
            self._print_error(f"文件不存在: {file_path}")
            return

        if "error" in preview:
            self._print_error(f"无法读取文件: {preview['error']}")
            return

        if not preview.get("required_fields_present", False):
            self._print_error("CSV格式错误：缺少必需的列")
            self._print_info("必需列: title, author, year")
            self._print_info(f"实际列: {', '.join(preview.get('headers', []))}")
            return

        print()
        self._print_info(f"📋 预览信息:")
        self._print_info(f"   - 文件路径: {preview['path']}")
        self._print_info(f"   - 数据行数: {preview['total_rows']} 行")
        self._print_info(f"   - 列名: {', '.join(preview['headers'])}")

        if preview.get("preview_rows"):
            print()
            self._print_info("📖 前几行数据预览:")
            for i, row in enumerate(preview["preview_rows"][:3], 1):
                title = row.get("title", "")[:20]
                author = row.get("author", "")[:15]
                year = row.get("year", "")
                print(f"   {i}. 《{title}》- {author} ({year})")

        print()
        self._print_info("⚠️  导入选项:")
        self._print_info("   - 1 = 跳过书库中已存在的ISBN（推荐）")
        self._print_info("   - 2 = 允许导入重复ISBN（可能失败）")
        print()

        mode = input("  👉 请选择导入模式 (1/2，默认1): ").strip() or "1"

        if mode == "1":
            skip_existing = True
        elif mode == "2":
            skip_existing = False
        else:
            self._print_error("无效选项")
            return

        confirm = input("\n  ⚠️  确定要开始导入吗? (y/n): ").strip().lower()

        if confirm != "y":
            self._print_info("已取消导入")
            return

        try:
            self._print_info("正在导入...")
            success_count, failed_count, warnings = self.service.import_from_csv(
                file_path,
                skip_existing_isbn=skip_existing,
                skip_duplicates_in_file=True,
            )

            print()
            self._print_success(f"✅ 导入完成！")
            self._print_info(f"   - 成功导入: {success_count} 本")
            self._print_info(f"   - 跳过/失败: {failed_count} 本")

            if warnings:
                print()
                self._print_warning("⚠️  警告信息:")
                for warning in warnings[:10]:
                    print(f"   - {warning}")
                if len(warnings) > 10:
                    print(f"   ... 还有 {len(warnings) - 10} 条警告")

        except CsvInvalidFormatError as error:
            self._print_error(f"CSV格式错误: {error}")
        except CsvStorageError as error:
            self._print_error(f"导入失败: {error}")
        except Exception as error:
            self._print_error(f"导入时发生未知错误: {error}")

    def _preview_csv_file(self) -> None:
        """
        预览CSV文件内容
        """
        file_path = input("  📁 请输入CSV文件路径: ").strip()
        if not file_path:
            self._print_warning("未输入文件路径")
            return

        preview = self.service.preview_csv_import(file_path, max_rows=10)

        if not preview.get("exists", False):
            self._print_error(f"文件不存在: {file_path}")
            return

        if "error" in preview:
            self._print_error(f"无法读取文件: {preview['error']}")
            return

        print()
        self._print_info(f"📋 文件信息:")
        self._print_info(f"   - 路径: {preview['path']}")
        self._print_info(f"   - 数据行数: {preview['total_rows']} 行")
        self._print_info(f"   - 列名: {', '.join(preview['headers'])}")
        self._print_info(
            f"   - 必需列检查: {'✅ 通过' if preview.get('required_fields_present') else '❌ 缺少必需列'}"
        )

        if preview.get("preview_rows"):
            print()
            self._print_info("📖 数据预览:")
            print("  " + "-" * 70)
            for i, row in enumerate(preview["preview_rows"], 1):
                title = (row.get("title") or "")[:25]
                author = (row.get("author") or "")[:15]
                year = row.get("year") or "-"
                isbn = (row.get("isbn") or "-")[:13]
                print(f"  {i:<3} {title:<27} {author:<17} {year:<6} {isbn:<13}")
            print("  " + "-" * 70)

        if preview.get("required_fields_present"):
            self._print_success("✅ 该CSV文件格式正确，可以导入")
        else:
            self._print_warning("⚠️  该CSV文件缺少必需的列，无法导入")
            self._print_info("必需列: title, author, year")

    def _print_book_list(self, books: list[Book]) -> None:
        """
        打印图书列表（表格形式）

        Args:
            books: 要显示的图书列表
        """
        print()
        print("  " + "-" * 72)
        print(f"  {'ID':<10} {'书名':<20} {'作者':<12} {'出版社':<12} {'年份':<6}")
        print("  " + "-" * 72)

        for book in books:
            publisher = book.publisher or "-"
            print(f"  {book.book_id:<10} {book.title:<20} {book.author:<12} {publisher:<12} {book.year:<6}")

        print("  " + "-" * 72)

    def _print_book_detail(self, book: Book) -> None:
        """
        打印单本图书的详细信息

        Args:
            book: 要显示的图书对象
        """
        print("  " + "-" * 42)
        print(f"  🆔 图书ID:   {book.book_id}")
        print(f"  📕 书名:     {book.title}")
        print(f"  ✍️  作者:     {book.author}")
        print(f"  📝 ISBN:     {book.isbn or '(未设置)'}")
        print(f"  🏢 出版社:   {book.publisher or '(未设置)'}")
        print(f"  📅 出版年份: {book.year}")
        print("  " + "-" * 42)
