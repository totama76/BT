def load_program(self, program):
    """Carga un programa específico para ejecutar"""
    self.selected_program = program
    self.show_execution_panel()
    
    # Cargar el programa en el servicio de ejecución
    app = App.get_running_app()
    if app and hasattr(app, 'program_execution_service'):
        success, message = app.program_execution_service.load_program(program.id)
        if success:
            self.program_name_label.text = program.name
            self.reset_execution_display()
        else:
            self.show_message(message, True)