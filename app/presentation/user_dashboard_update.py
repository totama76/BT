def view_programs_action(self, instance):
    """Navegar a la pantalla de ver programas"""
    print("UserDashboard: Navigating to View Programs")
    self.manager.current = 'user_programs'

# Eliminar o comentar el método execute_program_action ya que ahora esa funcionalidad
# se integra en la pantalla de programas de usuario