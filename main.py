from app.main_app import Application

def run_application():
    """Run the Electronic Control System application"""
    try:
        print("Starting application in language: es")
        print("Sistema de Control Electrónico")
        print("Sistema de Control Electrónico - Initializing Kivy UI...")
        
        app_instance = Application()
        app_instance.run()
        
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("Kivy application has finished.")

if __name__ == "__main__":
    run_application()