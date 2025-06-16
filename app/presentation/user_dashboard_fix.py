# En la clase UserDashboardScreen, actualizar este método
def view_programs_action(self, instance):
    """Navegar a la pantalla de ver programas"""
    print("UserDashboard: Navigating to View Programs")
    
    # Comprobar si la pantalla ya existe, y crearla si no
    if not self.manager.has_screen('user_programs'):
        from app.presentation.user_programs_screen import UserProgramsScreen
        user_programs_screen = UserProgramsScreen(name='user_programs')
        self.manager.add_widget(user_programs_screen)
        
    self.manager.current = 'user_programs'