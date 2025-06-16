import sqlite3
import os
import configparser
from .models import User, Program 
import hashlib 
import datetime

SALT_DEFAULT = "default_salt_please_change_in_production" 

def hash_password(password, salt=SALT_DEFAULT):
    salted_password = salt + password
    hashed_password = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
    return hashed_password

def verify_password(stored_password_hash, provided_password, salt=SALT_DEFAULT):
    return stored_password_hash == hash_password(provided_password, salt)

class DatabaseManager:
    def __init__(self, config_path='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        try:
            db_name = self.config.get('Database', 'name', fallback='app_database.db')
        except (configparser.NoSectionError, configparser.NoOptionError):
            db_name = 'app_database.db'

        project_root_dir = os.path.dirname(config_path)
        self.db_path = os.path.join(project_root_dir, db_name)
        
        self.conn = None
        self.connect()
        self._create_tables()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row 
        except sqlite3.Error as e:
            print(f"Error connecting to database {self.db_path}: {e}")

    def close_connection(self):
        if self.conn:
            self.conn.close()

    def _execute_query(self, query, params=None, fetch_one=False, fetch_all=False, commit=False):
        if not self.conn:
            self.connect()
            if not self.conn:
                return None 

        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params or ())
            if commit:
                self.conn.commit()
                return cursor.lastrowid 
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
            return cursor 
        except sqlite3.Error as e:
            print(f"Database query error: {e}\nQuery: {query}\nParams: {params}")
            if commit: 
                try:
                    self.conn.rollback()
                except sqlite3.Error as rb_err:
                    print(f"Rollback error: {rb_err}")
            return None

    def _create_tables(self):
        users_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'normal_user')),
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        programs_table_query = """
        CREATE TABLE IF NOT EXISTS programs (
            program_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            min_pressure REAL NOT NULL,
            max_pressure REAL NOT NULL,
            time_to_min_pressure INTEGER NOT NULL,
            program_duration INTEGER NOT NULL,
            created_by_user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by_user_id) REFERENCES users (user_id)
        );
        """
        self._execute_query(users_table_query, commit=True) 
        self._execute_query(programs_table_query, commit=True)
        self.ensure_admin_user_exists()


    def ensure_admin_user_exists(self):
        admin_username = self.config.get('DefaultAdmin', 'username', fallback='admin')
        admin_password = self.config.get('DefaultAdmin', 'password', fallback='admin123')
        
        user = self.get_user_by_username(admin_username)
        if not user:
            print(f"Default admin user '{admin_username}' not found. Creating...")
            self.create_user(admin_username, admin_password, 'admin')
            print(f"Default admin user '{admin_username}' created with password '{admin_password}'. PLEASE CHANGE THIS PASSWORD.")

    def create_user(self, username, password, role, is_active=True):
        if role not in ['admin', 'normal_user']:
            return None
        
        hashed_pass = hash_password(password, SALT_DEFAULT)
        query = """
        INSERT INTO users (username, password_hash, role, is_active)
        VALUES (?, ?, ?, ?)
        """
        try:
            user_id = self._execute_query(query, (username, hashed_pass, role, is_active), commit=True)
            if user_id:
                return User(user_id, username, hashed_pass, role, is_active)
        except sqlite3.IntegrityError: 
            return None
        return None

    def get_user_by_username(self, username):
        query = "SELECT * FROM users WHERE username = ?"
        row = self._execute_query(query, (username,), fetch_one=True)
        if row:
            return User(user_id=row['user_id'], username=row['username'],
                        password_hash=row['password_hash'], role=row['role'],
                        is_active=bool(row['is_active']))
        return None

    def get_user_by_id(self, user_id):
        query = "SELECT * FROM users WHERE user_id = ?"
        row = self._execute_query(query, (user_id,), fetch_one=True)
        if row:
            return User(user_id=row['user_id'], username=row['username'],
                        password_hash=row['password_hash'], role=row['role'],
                        is_active=bool(row['is_active']))
        return None

    def update_user(self, user_id, username=None, password=None, role=None, is_active=None):
        fields = []
        params = []
        if username is not None:
            fields.append("username = ?")
            params.append(username)
        if password is not None:
            fields.append("password_hash = ?")
            params.append(hash_password(password, SALT_DEFAULT)) 
        if role is not None:
            if role not in ['admin', 'normal_user']:
                return False
            fields.append("role = ?")
            params.append(role)
        if is_active is not None:
            fields.append("is_active = ?")
            params.append(is_active)

        if not fields:
            return False 

        query = f"UPDATE users SET {', '.join(fields)} WHERE user_id = ?"
        params.append(user_id)
        self._execute_query(query, tuple(params), commit=True)
        return True 

    def delete_user(self, user_id):
        query = "DELETE FROM users WHERE user_id = ?"
        self._execute_query(query, (user_id,), commit=True)
        return True 

    def list_users(self):
        query = "SELECT * FROM users ORDER BY username"
        rows = self._execute_query(query, fetch_all=True)
        users = []
        if rows:
            for row in rows:
                users.append(User(user_id=row['user_id'], username=row['username'],
                                  password_hash=row['password_hash'], role=row['role'],
                                  is_active=bool(row['is_active'])))
        return users

    def create_program(self, name, description, min_pressure, max_pressure,
                       time_to_min_pressure, program_duration, created_by_user_id):
        query = """
        INSERT INTO programs (name, description, min_pressure, max_pressure,
                              time_to_min_pressure, program_duration, created_by_user_id, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        params = (name, description, min_pressure, max_pressure,
                  time_to_min_pressure, program_duration, created_by_user_id)
        try:
            program_id = self._execute_query(query, params, commit=True)
            if program_id:
                return self.get_program_by_id(program_id)
        except sqlite3.Error:
            pass
        return None

    def get_program_by_id(self, program_id):
        query = "SELECT * FROM programs WHERE program_id = ?"
        row = self._execute_query(query, (program_id,), fetch_one=True)
        if row:
            return Program(program_id=row['program_id'], name=row['name'], description=row['description'],
                           min_pressure=row['min_pressure'], max_pressure=row['max_pressure'],
                           time_to_min_pressure=row['time_to_min_pressure'],
                           program_duration=row['program_duration'],
                           created_by_user_id=row['created_by_user_id'],
                           created_at=row['created_at'], updated_at=row['updated_at'])
        return None

    def list_programs(self):
        query = "SELECT * FROM programs ORDER BY name"
        rows = self._execute_query(query, fetch_all=True)
        programs = []
        if rows:
            for row in rows:
                programs.append(Program(program_id=row['program_id'], name=row['name'], description=row['description'],
                               min_pressure=row['min_pressure'], max_pressure=row['max_pressure'],
                               time_to_min_pressure=row['time_to_min_pressure'],
                               program_duration=row['program_duration'],
                               created_by_user_id=row['created_by_user_id'],
                               created_at=row['created_at'], updated_at=row['updated_at']))
        return programs

    def update_program(self, program_id, name=None, description=None, min_pressure=None,
                       max_pressure=None, time_to_min_pressure=None, program_duration=None):
        fields = []
        params = []

        if name is not None: fields.append("name = ?"); params.append(name)
        if description is not None: fields.append("description = ?"); params.append(description)
        if min_pressure is not None: fields.append("min_pressure = ?"); params.append(min_pressure)
        if max_pressure is not None: fields.append("max_pressure = ?"); params.append(max_pressure)
        if time_to_min_pressure is not None: fields.append("time_to_min_pressure = ?"); params.append(time_to_min_pressure)
        if program_duration is not None: fields.append("program_duration = ?"); params.append(program_duration)

        if not fields:
            return False

        fields.append("updated_at = CURRENT_TIMESTAMP")
        query = f"UPDATE programs SET {', '.join(fields)} WHERE program_id = ?"
        params.append(program_id)
        self._execute_query(query, tuple(params), commit=True)
        return True

    def delete_program(self, program_id):
        query = "DELETE FROM programs WHERE program_id = ?"
        self._execute_query(query, (program_id,), commit=True)
        return True