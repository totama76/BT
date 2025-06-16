import sqlite3
import hashlib
from datetime import datetime
from .models import User, Program, ProgramStep

class DatabaseManager:
    def __init__(self, db_path="electronic_control.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('admin', 'user')),
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Programs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS programs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            
            # Program steps table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS program_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    program_id INTEGER NOT NULL,
                    step_number INTEGER NOT NULL,
                    pressure REAL NOT NULL,
                    duration INTEGER NOT NULL,
                    FOREIGN KEY (program_id) REFERENCES programs (id) ON DELETE CASCADE,
                    UNIQUE(program_id, step_number)
                )
            ''')
            
            conn.commit()
            self._create_default_admin()

    def _create_default_admin(self):
        """Create default admin user if none exists"""
        try:
            admin = self.get_user_by_username("admin")
            if not admin:
                self.create_user("admin", "admin123", "admin")
                print("Default admin user created (username: admin, password: admin123)")
        except Exception as e:
            print(f"Error creating default admin: {e}")

    # User methods (existing + new)
    def get_user_by_username(self, username):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, password_hash, role, is_active FROM users WHERE username = ?', 
                         (username,))
            row = cursor.fetchone()
            return User(*row) if row else None

    def get_user_by_id(self, user_id):
        """Get a specific user by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, password_hash, role, is_active FROM users WHERE id = ?', 
                         (user_id,))
            row = cursor.fetchone()
            return User(*row) if row else None

    def get_all_users(self, include_inactive=True):
        """Get all users, optionally filter by active status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if include_inactive:
                cursor.execute('''
                    SELECT id, username, password_hash, role, is_active 
                    FROM users 
                    ORDER BY username
                ''')
            else:
                cursor.execute('''
                    SELECT id, username, password_hash, role, is_active 
                    FROM users 
                    WHERE is_active = 1 
                    ORDER BY username
                ''')
            
            users = []
            for row in cursor.fetchall():
                users.append(User(*row))
            return users

    def create_user(self, username, password, role):
        """Create a new user"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password_hash, role) 
                VALUES (?, ?, ?)
            ''', (username, password_hash, role))
            conn.commit()
            return cursor.lastrowid

    def update_user(self, user_id, username, role, password=None):
        """Update an existing user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if password:
                # Update with new password
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute('''
                    UPDATE users 
                    SET username = ?, role = ?, password_hash = ? 
                    WHERE id = ?
                ''', (username, role, password_hash, user_id))
            else:
                # Update without changing password
                cursor.execute('''
                    UPDATE users 
                    SET username = ?, role = ? 
                    WHERE id = ?
                ''', (username, role, user_id))
            
            conn.commit()

    def activate_user(self, user_id):
        """Activate a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET is_active = 1 WHERE id = ?', (user_id,))
            conn.commit()

    def deactivate_user(self, user_id):
        """Deactivate a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET is_active = 0 WHERE id = ?', (user_id,))
            conn.commit()

    def verify_password(self, user, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return user.password_hash == password_hash

    def username_exists(self, username, exclude_user_id=None):
        """Check if username already exists (optionally excluding a specific user)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if exclude_user_id:
                cursor.execute('SELECT id FROM users WHERE username = ? AND id != ?', 
                             (username, exclude_user_id))
            else:
                cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            return cursor.fetchone() is not None

    # Program methods (existing, no changes)
    def get_all_programs(self, active_only=True):
        """Get all programs, optionally filter by active status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if active_only:
                cursor.execute('''
                    SELECT id, name, description, created_by, created_at, is_active 
                    FROM programs WHERE is_active = 1 
                    ORDER BY name
                ''')
            else:
                cursor.execute('''
                    SELECT id, name, description, created_by, created_at, is_active 
                    FROM programs 
                    ORDER BY name
                ''')
            
            programs = []
            for row in cursor.fetchall():
                programs.append(Program(*row))
            return programs

    def get_program_by_id(self, program_id):
        """Get a specific program by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, description, created_by, created_at, is_active 
                FROM programs WHERE id = ?
            ''', (program_id,))
            row = cursor.fetchone()
            return Program(*row) if row else None

    def create_program(self, name, description, created_by, steps=None):
        """Create a new program with optional steps"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert program
            cursor.execute('''
                INSERT INTO programs (name, description, created_by) 
                VALUES (?, ?, ?)
            ''', (name, description, created_by))
            program_id = cursor.lastrowid
            
            # Insert steps if provided
            if steps:
                for step in steps:
                    cursor.execute('''
                        INSERT INTO program_steps (program_id, step_number, pressure, duration)
                        VALUES (?, ?, ?, ?)
                    ''', (program_id, step.step_number, step.pressure, step.duration))
            
            conn.commit()
            return program_id

    def update_program(self, program_id, name, description, steps=None):
        """Update an existing program"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Update program basic info
            cursor.execute('''
                UPDATE programs 
                SET name = ?, description = ? 
                WHERE id = ?
            ''', (name, description, program_id))
            
            # Update steps if provided
            if steps is not None:
                # Delete existing steps
                cursor.execute('DELETE FROM program_steps WHERE program_id = ?', (program_id,))
                
                # Insert new steps
                for step in steps:
                    cursor.execute('''
                        INSERT INTO program_steps (program_id, step_number, pressure, duration)
                        VALUES (?, ?, ?, ?)
                    ''', (program_id, step.step_number, step.pressure, step.duration))
            
            conn.commit()

    def delete_program(self, program_id):
        """Delete a program (soft delete - set is_active to False)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE programs SET is_active = 0 WHERE id = ?', (program_id,))
            conn.commit()

    def get_program_steps(self, program_id):
        """Get all steps for a specific program"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, program_id, step_number, pressure, duration 
                FROM program_steps 
                WHERE program_id = ? 
                ORDER BY step_number
            ''', (program_id,))
            
            steps = []
            for row in cursor.fetchall():
                steps.append(ProgramStep(*row))
            return steps