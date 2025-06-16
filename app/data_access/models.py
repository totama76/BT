class User:
    def __init__(self, user_id, username, password_hash, role, is_active=True):
        self.user_id = user_id 
        self.username = username
        self.password_hash = password_hash 
        self.role = role 
        self.is_active = is_active

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', role='{self.role}')>"

class Program:
    def __init__(self, program_id, name, description, min_pressure, max_pressure,
                 time_to_min_pressure, program_duration, created_by_user_id,
                 created_at=None, updated_at=None):
        self.program_id = program_id 
        self.name = name
        self.description = description
        self.min_pressure = min_pressure
        self.max_pressure = max_pressure
        self.time_to_min_pressure = time_to_min_pressure 
        self.program_duration = program_duration 
        self.created_by_user_id = created_by_user_id
        self.created_at = created_at 
        self.updated_at = updated_at 

    def __repr__(self):
        return f"<Program(program_id={self.program_id}, name='{self.name}')>"