from app.data.database_manager import DatabaseManager
from app.logic.user_service import UserService
from app.logic.program_service import ProgramService
from app.presentation.ui_manager import ElectronicControlApp
from app.i18n.translations import initialize_translations

class Application:
    def __init__(self):
        # Initialize components
        self.db_manager = DatabaseManager()
        self.user_service = UserService(self.db_manager)
        self.program_service = ProgramService(self.db_manager)
        
        # Initialize translations
        initialize_translations()
        
        # Initialize Kivy app
        self.kivy_app = ElectronicControlApp(self)

    def run(self):
        self.kivy_app.run()

if __name__ == "__main__":
    app = Application()
    app.run()