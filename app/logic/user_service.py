from app.data.models import User
import hashlib

class UserService:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def login_user(self, username, password):
        """Authenticate user login
        
        Returns:
            (user: User or None, message: str)
        """
        try:
            user = self.db_manager.get_user_by_username(username)
            
            if not user:
                return None, "Invalid username or password."
            
            if not user.is_active:
                return None, "User account is inactive."
            
            if self.db_manager.verify_password(user, password):
                return user, "Login successful"
            else:
                return None, "Invalid username or password."
                
        except Exception as e:
            print(f"Login error: {e}")
            return None, "An error occurred during login."

    def get_all_users(self, include_inactive=True):
        """Get all users"""
        return self.db_manager.get_all_users(include_inactive)

    def get_user_by_id(self, user_id):
        """Get a specific user by ID"""
        return self.db_manager.get_user_by_id(user_id)

    def create_user(self, username, password, role):
        """Create a new user
        
        Returns:
            (success: bool, message: str, user_id: int or None)
        """
        try:
            # Validate input
            if not username or not username.strip():
                return False, "username_required", None
            
            if not password or len(password.strip()) < 6:
                return False, "password_too_short", None
            
            if role not in ['admin', 'user']:
                return False, "invalid_role", None
            
            # Check if username already exists
            if self.db_manager.username_exists(username.strip()):
                return False, "username_already_exists", None
            
            # Create user
            user_id = self.db_manager.create_user(username.strip(), password, role)
            return True, "user_saved", user_id
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return False, "error_saving_user", None

    def update_user(self, user_id, username, role, password=None):
        """Update an existing user
        
        Returns:
            (success: bool, message: str)
        """
        try:
            # Validate input
            if not username or not username.strip():
                return False, "username_required"
            
            if role not in ['admin', 'user']:
                return False, "invalid_role"
            
            # Check if username already exists (excluding current user)
            if self.db_manager.username_exists(username.strip(), user_id):
                return False, "username_already_exists"
            
            # Validate password if provided
            if password and len(password.strip()) < 6:
                return False, "password_too_short"
            
            # Update user
            self.db_manager.update_user(user_id, username.strip(), role, password.strip() if password else None)
            return True, "user_updated"
            
        except Exception as e:
            print(f"Error updating user: {e}")
            return False, "error_updating_user"

    def activate_user(self, user_id):
        """Activate a user
        
        Returns:
            (success: bool, message: str)
        """
        try:
            self.db_manager.activate_user(user_id)
            return True, "user_activated"
        except Exception as e:
            print(f"Error activating user: {e}")
            return False, "error_updating_user"

    def deactivate_user(self, user_id):
        """Deactivate a user
        
        Returns:
            (success: bool, message: str)
        """
        try:
            self.db_manager.deactivate_user(user_id)
            return True, "user_deactivated"
        except Exception as e:
            print(f"Error deactivating user: {e}")
            return False, "error_updating_user"