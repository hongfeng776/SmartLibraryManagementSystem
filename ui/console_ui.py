from typing import Optional
from services.library_service import (
    LibraryService,
    LibraryServiceError,
    DuplicateIsbnError,
    InvalidInputError,
)
from models.book import Book


class ConsoleUI:
    def __init__(self, service: LibraryService):
        self.service = service

    def run(self) -> None:
        count = self.service.get_book_count()
        print("欢迎使用图书管理系统！")
        print(f"已加载 {count} 条图书记录。")
        try:
            while True:
                self._print_menu()
                choice = input("请选择操作 (1-6): ").strip()
                if choice == "1":
                    self._add_book()
                elif choice == "2":
                    self._search_book()
                elif choice == "3":
                    self._update_book()
                elif choice == "4":
                    self._delete_book()
                elif choice == "5":
                    self._list_all_books()
                elif choice == "6":
                    self._shutdown()
                    break
                else:
                    print("无效选项，请输入 1-6 之间的数字。")
                print()
        except KeyboardInterrupt:
            print("\n\n检测到中断，正在保存数据并退出...")
            self._shutdown()
        except EOFError:
            print("\n\n输入流已结束，正在保存数据并退出...")
            self._shutdown()

    def _shutdown(self) -> None:
        try:
            self.service.flush()
            print("数据已保存。再见！")
        except Exception as e:
            print(f"保存数据时出错: {e}")

    def _print_menu(self) -> None:
        print("=" * 32)
        print("      图书管理系统")
        print("=" * 32)
        print("1. 添加图书")
        print("2. 搜索图书")
        print("3. 修改图书信息")
        print("4. 删除图书")
        print("5. 查看所有图书")
        print("6. 退出")
        print("-" * 32)

    def _input_int(
        self, prompt: str, min_value: Optional[int] = None, max_value: Optional[int] = None
    ) -> Optional[int]:
        raw = input(prompt).strip()
        if not raw:
            return None
        try:
            value = int(raw)
        except ValueError:
            print("输入无效，请输入数字。")
            return None
        if min_value is not None and value < min_value:
            print(f"输入无效，不能小于 {min_value}。")
            return None
        if max_value is not None and value > max_value:
            print(f"输入无效，不能大于 {max_value}。")
            return None
        return value

    def _input_required(self, prompt: str) -> Optional[str]:
        value = input(prompt).strip()
        if not value:
            print("输入不能为空。")
            return None
        return value

    def _input_choice(self, prompt: str, choices: list[str]) -> Optional[str]:
        value = input(prompt).strip()
        if value not in choices:
            print(f"输入无效，请选择: {', '.join(choices)}")
            return None
        return value

    def _add_book(self) -> None:
        print("\n--- 添加图书 ---")
        title = self._input_required("书名: ")
        if not title:
            return
        author = self._input_required("作者: ")
        if not author:
            return
        isbn = input("ISBN (可选): ").strip()
        publisher = input("出版社 (可选): ").strip()
        year = self._input_int("出版年份: ", min_value=1)
        if year is None:
            return
        try:
            book = self.service.add_book(title, author, year, isbn, publisher)
            print(f"添加成功！图书ID: {book.book_id}")
        except DuplicateIsbnError as e:
            print(f"添加失败: {e}")
        except InvalidInputError as e:
            print(f"输入无效: {e}")

    def _search_book(self) -> None:
        print("\n--- 搜索图书 ---")
        keyword = self._input_required("请输入书名/作者/ISBN关键词: ")
        if not keyword:
            return
        results = self.service.search_books(keyword)
        if results:
            print(f"找到 {len(results)} 本图书:")
            self._print_books(results)
        else:
            print("未找到匹配的图书。")

    def _update_book(self) -> None:
        print("\n--- 修改图书信息 ---")
        print("请选择查找方式:")
        print("1. 按书名查找")
        print("2. 按 ISBN 查找")
        mode = self._input_choice("请选择 (1/2): ", ["1", "2"])
        if not mode:
            return

        book = None
        if mode == "1":
            title = self._input_required("请输入书名: ")
            if not title:
                return
            matches = self.service.find_books_by_title(title)
            if not matches:
                print("未找到匹配的图书。")
                return
            if len(matches) == 1:
                book = matches[0]
            else:
                print(f"找到 {len(matches)} 本匹配的图书:")
                self._print_books(matches)
                book_id = self._input_required("请输入要修改的图书ID: ")
                if not book_id:
                    return
                book = self.service.find_book_by_id(book_id)
        elif mode == "2":
            isbn = self._input_required("请输入 ISBN: ")
            if not isbn:
                return
            book = self.service.find_book_by_isbn(isbn)

        if not book:
            print("未找到该图书。")
            return

        print("\n当前图书信息:")
        self._print_book_detail(book)

        print("\n请输入新信息（直接回车表示不修改）:")
        new_title = input(f"书名 [{book.title}]: ").strip() or None
        new_author = input(f"作者 [{book.author}]: ").strip() or None
        new_isbn = input(f"ISBN [{book.isbn or '(空)'}]: ").strip() or None
        new_publisher = input(f"出版社 [{book.publisher or '(空)'}]: ").strip() or None
        new_year_str = input(f"年份 [{book.year}]: ").strip()

        updates = {}
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
                print("年份输入无效，年份未修改。")

        if not updates:
            print("没有修改任何信息。")
            return

        try:
            updated = self.service.update_book(book.book_id, **updates)
            if updated:
                print("修改成功！")
                print("\n修改后信息:")
                self._print_book_detail(updated)
            else:
                print("修改失败：图书不存在。")
        except DuplicateIsbnError as e:
            print(f"修改失败: {e}")
        except InvalidInputError as e:
            print(f"输入无效: {e}")

    def _delete_book(self) -> None:
        print("\n--- 删除图书 ---")
        book_id = self._input_required("请输入要删除的图书ID: ")
        if not book_id:
            return
        book = self.service.find_book_by_id(book_id)
        if not book:
            print("未找到该图书，删除失败。")
            return
        confirm = input(f"确定删除《{book.title}》吗? (y/n): ").strip().lower()
        if confirm == "y":
            success = self.service.delete_book(book_id)
            if success:
                print("删除成功！")
            else:
                print("删除失败：图书不存在。")
        else:
            print("已取消删除。")

    def _list_all_books(self) -> None:
        print("\n--- 所有图书 ---")
        books = self.service.get_all_books()
        if books:
            print(f"共 {len(books)} 本图书:")
            self._print_books(books)
        else:
            print("暂无图书。")

    def _print_books(self, books: list[Book]) -> None:
        print("-" * 70)
        print(f"{'ID':<12} {'书名':<20} {'作者':<12} {'出版社':<12} {'年份':<6}")
        print("-" * 70)
        for book in books:
            pub = book.publisher or "-"
            print(f"{book.book_id:<12} {book.title:<20} {book.author:<12} {pub:<12} {book.year:<6}")
        print("-" * 70)

    def _print_book_detail(self, book: Book) -> None:
        print("-" * 40)
        print(f"图书ID:   {book.book_id}")
        print(f"书名:     {book.title}")
        print(f"作者:     {book.author}")
        print(f"ISBN:     {book.isbn or '(未设置)'}")
        print(f"出版社:   {book.publisher or '(未设置)'}")
        print(f"出版年份: {book.year}")
        print("-" * 40)
