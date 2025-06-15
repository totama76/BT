from app.data.database_manager import DatabaseManager
import hashlib

def debug_users():
    """Debug script to check users in database"""
    db = DatabaseManager()
    
    print("=== DEBUG: Checking users in database ===")
    
    # Get all users
    users = db.get_all_users(include_inactive=True)
    
    if not users:
        print("No users found in database!")
        print("Creating default admin user...")
        db._create_default_admin()
        users = db.get_all_users(include_inactive=True)
    
    print(f"Found {len(users)} users:")
    for user in users:
        print(f"  ID: {user.id}")
        print(f"  Username: '{user.username}'")
        print(f"  Role: {user.role}")
        print(f"  Active: {user.is_active}")
        print(f"  Password Hash: {user.password_hash}")
        print("  ---")
    
    # Test password verification for admin
    admin_user = db.get_user_by_username("admin")
    if admin_user:
        print("\n=== Testing admin password ===")
        test_passwords = ["admin123", "admin", "password", "123456"]
        
        for password in test_passwords:
            test_hash = hashlib.sha256(password.encode()).hexdigest()
            is_valid = db.verify_password(admin_user, password)
            print(f"Password '{password}' -> Hash: {test_hash[:20]}... -> Valid: {is_valid}")
            
            if is_valid:
                print(f"*** CORRECT PASSWORD: '{password}' ***")
                break
    else:
        print("Admin user not found!")
    
    print("\n=== Manual password test ===")
    print("Enter username and password to test:")
    username = input("Username: ")
    password = input("Password: ")
    
    user = db.get_user_by_username(username)
    if user:
        is_valid = db.verify_password(user, password)
        print(f"Login test result: {is_valid}")
        if not user.is_active:
            print("WARNING: User account is inactive!")
    else:
        print("User not found!")

if __name__ == "__main__":
    debug_users()