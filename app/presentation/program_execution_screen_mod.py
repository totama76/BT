# Añadir un método mejorado para volver atrás
def back_action(self, instance):
    """Vuelve a la pantalla anterior"""
    # Asegurarse de detener cualquier ejecución
    app = App.get_running_app()
    if app and hasattr(app, 'program_execution_service'):
        app.program_execution_service.stop_execution()
        
    # Detener el reloj de actualización
    if self.clock_event:
        self.clock_event.cancel()
        self.clock_event = None
        
    # Volver a la pantalla de programas de usuario si venimos de ahí
    if self.manager.has_screen('user_programs'):
        self.manager.current = 'user_programs'
    else:
        # En caso contrario, volver al dashboard apropiado
        role = 'user'
        if app and hasattr(app, 'current_user') and app.current_user:
            role = app.current_user.role
            
        if role == 'admin':
            self.manager.current = 'admin_dashboard'
        else:
            self.manager.current = 'user_dashboard'