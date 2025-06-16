# ----- CAMBIOS EN ui_manager.py -----

# 1. CAMBIAR LA PROPIEDAD current_user PARA PERMITIR VALORES NULOS
class ElectronicControlApp(App):
    current_user = ObjectProperty(allownone=True)  # Permitir None como valor
    # ... resto de la clase sin cambios

# 2. AÑADIR IMPORTACIÓN AL INICIO DEL ARCHIVO
from app.presentation.user_programs_screen import UserProgramsScreen

# 3. AÑADIR REGISTRO DE FACTORY DESPUÉS DE LOS OTROS REGISTROS
Factory.register('UserProgramsScreen', UserProgramsScreen)

# 4. ACTUALIZAR EL MÉTODO view_programs_action EN UserDashboardScreen
def view_programs_action(self, instance):
    """Navegar a la pantalla de ver programas"""
    print("UserDashboard: Navigating to View Programs")
    
    # Comprobar si la pantalla ya existe, y crearla si no
    if not self.manager.has_screen('user_programs'):
        from app.presentation.user_programs_screen import UserProgramsScreen
        user_programs_screen = UserProgramsScreen(name='user_programs')
        self.manager.add_widget(user_programs_screen)
        
    self.manager.current = 'user_programs'