from app.data.database_manager import DatabaseManager
from app.logic.user_service import UserService
from app.logic.program_service import ProgramService
from app.presentation.ui_manager import ElectronicControlApp

class Application:
    def __init__(self):
        # Initialize components
        self.db_manager = DatabaseManager()
        self.user_service = UserService(self.db_manager)
        self.program_service = ProgramService(self.db_manager)
        
        # Initialize translations - lo haremos dentro de UI manager
        # initialize_translations()  # Comentamos esto por ahora
        
        # Initialize Kivy app
        self.kivy_app = ElectronicControlApp(self)

    def run(self):
        self.kivy_app.run()