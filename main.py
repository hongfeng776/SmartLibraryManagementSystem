from library import Library


def print_menu():
    print("\n" + "=" * 40)
    print("     图书管理系统")
    print("=" * 40)
    print("  1. 添加图书")
    print("  2. 查询图书")
    print("  3. 删除图书")
    print("  4. 查看所有图书")
    print("  5. 退出系统")
    print("=" * 40)


def add_book_ui(library):
    print("\n--- 添加图书 ---")
    try:
        book_id = int(input("请输入图书ID: "))
        title = input("请输入图书名称: ").strip()
        author = input("请输入作者: ").strip()
        year = int(input("请输入出版年份: "))
        
        if not title or not author:
            print("错误: 书名和作者不能为空！")
            return
        
        success, message = library.add_book(book_id, title, author, year)
        print(message)
    except ValueError:
        print("错误: ID和年份必须是数字！")


def search_books_ui(library):
    print("\n--- 查询图书 ---")
    keyword = input("请输入查询关键词(书名/作者/ID): ").strip()
    if not keyword:
        print("错误: 关键词不能为空！")
        return
    
    results = library.search_books(keyword)
    if results:
        print(f"\n找到 {len(results)} 本图书:")
        for book in results:
            print(book)
    else:
        print("未找到匹配的图书。")


def delete_book_ui(library):
    print("\n--- 删除图书 ---")
    try:
        book_id = int(input("请输入要删除的图书ID: "))
        success, message = library.delete_book(book_id)
        print(message)
    except ValueError:
        print("错误: ID必须是数字！")


def list_all_books_ui(library):
    print("\n--- 所有图书 ---")
    books = library.list_all_books()
    if books:
        print(f"共 {len(books)} 本图书:")
        for book in books:
            print(book)
    else:
        print("图书馆暂无图书。")


def main():
    library = Library()
    print("欢迎使用图书管理系统！")
    
    while True:
        print_menu()
        choice = input("请选择操作 (1-5): ").strip()
        
        if choice == '1':
            add_book_ui(library)
        elif choice == '2':
            search_books_ui(library)
        elif choice == '3':
            delete_book_ui(library)
        elif choice == '4':
            list_all_books_ui(library)
        elif choice == '5':
            print("感谢使用，再见！")
            break
        else:
            print("无效的选择，请输入 1-5 之间的数字。")


if __name__ == '__main__':
    main()
