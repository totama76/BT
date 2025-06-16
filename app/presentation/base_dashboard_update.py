# Este método ya debería existir en BaseDashboardScreen
def logout_pressed(self, instance):
    """Cierra la sesión actual y vuelve a la pantalla de login"""
    app = App.get_running_app()
    if app:
        app.logout()