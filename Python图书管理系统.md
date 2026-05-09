# Python图书管理系统

> **Workspace:** c:\Users\whftn\Desktop\SmartLibraryManagementSystem

---

## User
帮我写个简单的小项目用Python。要求跨模块，多文件，不要一个文件写完。就做个最简单的图书管理，能加、能查、能删就行。分几个文件写清楚。需要多文件夹多模块

## Assistant
我来帮你创建一个多模块的图书管理系统。首先让我查看一下当前目录结构。

现在我来为你创建一个清晰的多模块图书管理系统。让我先规划一下任务。

我先查看一下现有的文件，避免覆盖可能有用的代码。


项目目前基本是空的。让我先创建所有目录结构和模块文件。


现在让我创建所有核心模块文件。



现在创建各模块的 `__init__.py` 文件，并验证项目能否正常运行。




现在让我检查一下项目是否有语法错误，并确认项目结构完整。





完美！项目结构已经创建完成，没有任何诊断错误。让我为你总结一下这个多模块图书管理系统的设计。

---

## 项目结构

```
SmartLibraryManagementSystem/
├── main.py                 # 主程序入口
├── __init__.py             # 包初始化文件
├── models/                 # 数据模型层
│   ├── __init__.py
│   └── book.py             # Book 数据类
├── services/               # 业务逻辑层
│   ├── __init__.py
│   └── library_service.py  # LibraryService 核心服务
├── storage/                # 数据持久化层
│   ├── __init__.py
│   └── json_storage.py     # JsonStorage JSON 文件存储
└── ui/                     # 用户界面层
    ├── __init__.py
    └── console_ui.py       # ConsoleUI 控制台交互
```

## 模块职责说明

| 模块 | 路径 | 职责 |
|------|------|------|
| **models** | `models/book.py` | 定义数据结构，使用 `@dataclass` 实现 `Book` 类，包含序列化/反序列化方法 |
| **storage** | `storage/json_storage.py` | 数据持久化，通过 JSON 文件保存和加载图书数据 |
| **services** | `services/library_service.py` | 核心业务逻辑：添加、删除、搜索、查询所有图书 |
| **ui** | `ui/console_ui.py` | 用户交互界面，提供命令行菜单和操作 |
| **main** | `main.py` | 组装各模块，启动程序 |

## 运行方式

在项目根目录下执行：

```bash
python main.py
```

## 功能特性

- ✅ **添加图书**：输入书名、作者、年份，自动生成 8 位图书 ID
- ✅ **搜索图书**：按书名或作者关键词模糊搜索
- ✅ **删除图书**：按图书 ID 删除，带确认提示
- ✅ **查看所有图书**：以表格形式列出所有图书
- ✅ **数据持久化**：图书数据保存在 `books.json` 文件中

