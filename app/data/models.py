# Actualizamos el archivo models.py existente
class User:
    def __init__(self, id, username, password_hash, role, is_active=True):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role  # 'admin' or 'user'
        self.is_active = is_active

class Program:
    def __init__(self, id, name, description, created_by, created_at=None, is_active=True):
        self.id = id
        self.name = name
        self.description = description
        self.created_by = created_by
        self.created_at = created_at
        self.is_active = is_active

class ProgramStep:
    def __init__(self, id, program_id, step_number, pressure, duration):
        self.id = id
        self.program_id = program_id
        self.step_number = step_number  # Orden del paso (1, 2, 3, etc.)
        self.pressure = pressure  # Presión en bar
        self.duration = duration  # Duración en segundos