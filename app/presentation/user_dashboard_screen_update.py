def view_programs_action(self, instance):
    """Navegar a la pantalla de ver programas"""
    print("UserDashboard: Navigating to User Programs")
    # Verificamos si la pantalla existe y la creamos si no
    if not self.manager.has_screen('user_programs'):
        from app.presentation.user_programs_screen import UserProgramsScreen
        user_programs_screen = UserProgramsScreen(name='user_programs')
        self.manager.add_widget(user_programs_screen)
    self.manager.current = 'user_programs'

# Podemos comentar o eliminar el método execute_program_action
# ya que esta funcionalidad se integrará en la pantalla de programas de usuario
# def execute_program_action(self, instance):
#     print("UserDashboard: This functionality is now in User Programs screen")
#     self.view_programs_action(instance)