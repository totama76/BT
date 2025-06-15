from app.data.models import Program, ProgramStep

class ProgramService:
    def __init__(self, db_manager):  # Solo db_manager, sin config
        self.db_manager = db_manager

    def get_all_programs(self, active_only=True):
        """Get all programs"""
        return self.db_manager.get_all_programs(active_only)

    def get_program_by_id(self, program_id):
        """Get a specific program with its steps"""
        program = self.db_manager.get_program_by_id(program_id)
        if program:
            # Also load the steps
            steps = self.db_manager.get_program_steps(program_id)
            return program, steps
        return None, []

    def create_program(self, name, description, created_by, steps_data=None):
        """Create a new program with steps
        
        Args:
            name: Program name
            description: Program description  
            created_by: User ID of creator
            steps_data: List of dicts with 'pressure' and 'duration' keys
        
        Returns:
            (success: bool, message: str, program_id: int or None)
        """
        try:
            # Validate input
            if not name or not name.strip():
                return False, "program_name_required", None
            
            # Prepare steps
            steps = []
            if steps_data:
                for i, step_data in enumerate(steps_data, 1):
                    try:
                        pressure = float(step_data['pressure'])
                        duration = int(step_data['duration'])
                        
                        if pressure < 0:
                            return False, "invalid_pressure_value", None
                        if duration <= 0:
                            return False, "invalid_duration_value", None
                        
                        # Create a ProgramStep object (we'll use None for id since it's auto-generated)
                        step = ProgramStep(None, None, i, pressure, duration)
                        steps.append(step)
                    except (ValueError, KeyError):
                        return False, "invalid_pressure_value", None
            
            # Create program in database
            program_id = self.db_manager.create_program(name.strip(), description, created_by, steps)
            return True, "program_saved", program_id
            
        except Exception as e:
            print(f"Error creating program: {e}")
            return False, "error_saving_program", None

    def update_program(self, program_id, name, description, steps_data=None):
        """Update an existing program
        
        Returns:
            (success: bool, message: str)
        """
        try:
            # Validate input
            if not name or not name.strip():
                return False, "program_name_required"
            
            # Prepare steps
            steps = []
            if steps_data:
                for i, step_data in enumerate(steps_data, 1):
                    try:
                        pressure = float(step_data['pressure'])
                        duration = int(step_data['duration'])
                        
                        if pressure < 0:
                            return False, "invalid_pressure_value"
                        if duration <= 0:
                            return False, "invalid_duration_value"
                        
                        step = ProgramStep(None, program_id, i, pressure, duration)
                        steps.append(step)
                    except (ValueError, KeyError):
                        return False, "invalid_pressure_value"
            
            # Update program in database
            self.db_manager.update_program(program_id, name.strip(), description, steps)
            return True, "program_saved"
            
        except Exception as e:
            print(f"Error updating program: {e}")
            return False, "error_saving_program"

    def delete_program(self, program_id):
        """Delete a program
        
        Returns:
            (success: bool, message: str)
        """
        try:
            self.db_manager.delete_program(program_id)
            return True, "program_deleted"
        except Exception as e:
            print(f"Error deleting program: {e}")
            return False, "error_deleting_program"