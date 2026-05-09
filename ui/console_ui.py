from services.library_service import LibraryService
from models.book import Book


class ConsoleUI:
    def __init__(self, service: LibraryService):
        self.service = service

    def run(self) -> None:
        while True:
            self._print_menu()
            choice = input("请选择操作 (1-5): ").strip()
            if choice == "1":
                self._add_book()
            elif choice == "2":
                self._search_book()
            elif choice == "3":
                self._delete_book()
            elif choice == "4":
                self._list_all_books()
            elif choice == "5":
                print("再见！")
                break
            else:
                print("无效选项，请重新输入。")
            print()

    def _print_menu(self) -> None:
        print("=" * 30)
        print("    图书管理系统")
        print("=" * 30)
        print("1. 添加图书")
        print("2. 搜索图书")
        print("3. 删除图书")
        print("4. 查看所有图书")
        print("5. 退出")
        print("-" * 30)

    def _add_book(self) -> None:
        print("\n--- 添加图书 ---")
        title = input("书名: ").strip()
        author = input("作者: ").strip()
        try:
            year = int(input("出版年份: ").strip())
        except ValueError:
            print("年份必须是数字，添加失败。")
            return
        if not title or not author:
            print("书名和作者不能为空。")
            return
        book = self.service.add_book(title, author, year)
        print(f"添加成功！图书ID: {book.book_id}")

    def _search_book(self) -> None:
        print("\n--- 搜索图书 ---")
        keyword = input("请输入书名或作者关键词: ").strip()
        if not keyword:
            print("关键词不能为空。")
            return
        results = self.service.search_books(keyword)
        if results:
            print(f"找到 {len(results)} 本图书:")
            self._print_books(results)
        else:
            print("未找到匹配的图书。")

    def _delete_book(self) -> None:
        print("\n--- 删除图书 ---")
        book_id = input("请输入要删除的图书ID: ").strip()
        if not book_id:
            print("图书ID不能为空。")
            return
        book = self.service.find_book_by_id(book_id)
        if not book:
            print("未找到该图书。")
            return
        confirm = input(f"确定删除《{book.title}》吗? (y/n): ").strip().lower()
        if confirm == "y":
            self.service.delete_book(book_id)
            print("删除成功！")
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
        print("-" * 60)
        print(f"{'ID':<12} {'书名':<20} {'作者':<15} {'年份':<6}")
        print("-" * 60)
        for book in books:
            print(f"{book.book_id:<12} {book.title:<20} {book.author:<15} {book.year:<6}")
        print("-" * 60)
