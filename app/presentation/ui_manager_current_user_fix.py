# Modificar la definición de la clase ElectronicControlApp
class ElectronicControlApp(App):
    # Permitir None como valor para current_user
    current_user = ObjectProperty(allownone=True)
    current_language_display_name = StringProperty()
    available_languages_display_names = ListProperty(["English", "Español", "Français"])
    language_map = {"English": "en", "Español": "es", "Français": "fr"}
    language_map_inverted = {v: k for k, v in language_map.items()}

    # El resto de la clase permanece igual