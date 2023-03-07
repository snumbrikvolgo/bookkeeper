from bookkeeper.view.view import View
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.view.bookkeeper import Bookkeeper

if __name__ == '__main__':
    view = View()
    app = Bookkeeper(view, SQLiteRepository)
    app.run()