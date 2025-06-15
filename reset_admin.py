from app.data.database_manager import DatabaseManager

def reset_admin():
    """Reset admin user with known credentials"""
    db = DatabaseManager()
    
    # Delete existing admin if exists
    try:
        with db.db_path as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = 'admin'")
            conn.commit()
    except:
        pass
    
    # Create new admin
    admin_id = db.create_user("admin", "admin123", "admin")
    print(f"Admin user created with ID: {admin_id}")
    print("Credentials: admin / admin123")

if __name__ == "__main__":
    reset_admin()