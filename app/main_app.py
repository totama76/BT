from app.data.database_manager import DatabaseManager
from app.logic.user_service import UserService
from app.logic.program_service import ProgramService
from app.logic.program_execution_service import ProgramExecutionService
from app.hardware.hardware_simulator import HardwareSimulator
from app.presentation.ui_manager import ElectronicControlApp

class Application:
    def __init__(self):
        # Initialize components
        self.db_manager = DatabaseManager()
        self.user_service = UserService(self.db_manager)
        self.program_service = ProgramService(self.db_manager)
        
        # Initialize hardware simulator
        self.hardware_simulator = HardwareSimulator()
        self.hardware_simulator.start()
        
        # Initialize program execution service
        self.program_execution_service = ProgramExecutionService(self.program_service, self.hardware_simulator)
        
        # Initialize Kivy app
        self.kivy_app = ElectronicControlApp(self)

    def run(self):
        self.kivy_app.run()