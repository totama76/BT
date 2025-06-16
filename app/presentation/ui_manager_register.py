# Importación al principio del archivo
from app.presentation.user_programs_screen import UserProgramsScreen

# Justo antes de la definición de ElectronicControlApp, con los otros registros de Factory
Factory.register('UserProgramsScreen', UserProgramsScreen)