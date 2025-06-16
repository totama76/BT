# Añadir este import al principio del archivo
from app.presentation.user_programs_screen import UserProgramsScreen

# Añadir esta línea después del resto de registros de Factory (alrededor de la línea 1336)
Factory.register('UserProgramsScreen', UserProgramsScreen)