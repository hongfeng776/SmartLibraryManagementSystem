from storage.json_storage import JsonStorage
from services.library_service import LibraryService
from ui.console_ui import ConsoleUI


def main() -> None:
    storage = JsonStorage()
    service = LibraryService(storage)
    ui = ConsoleUI(service)
    ui.run()


if __name__ == "__main__":
    main()
