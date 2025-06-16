import kivy
kivy.require('1.11.1') 

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.metrics import dp 
import os 

# Inicializar traducciones primero
from app.i18n.translations import initialize_translations, set_current_language, get_current_language

# Inicializar las traducciones inmediatamente
try:
    initialize_translations()
    print(f"Translations initialized for language: {get_current_language()}")
except Exception as e:
    print(f"Warning: Could not initialize translations: {e}")

# Importar la función _ una sola vez y usarla en todas partes
from app.i18n.translations import _

# Importar la nueva pantalla de programas de usuario
from app.presentation.user_programs_screen import UserProgramsScreen

def get_translation(key, default=None):
    """Helper function to safely get translations"""
    try:
        from app.i18n.translations import _
        return _(key, default if default is not None else key)
    except:
        return default if default is not None else key

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self, *args):
        self.update_text()
        if self.ids.get('username_input'): self.ids.username_input.text = ""
        if self.ids.get('password_input'): self.ids.password_input.text = ""
        if self.ids.get('status_label'): self.ids.status_label.text = ""
        if self.ids.get('username_input'):
            self.ids.username_input.focus = False
        if self.ids.get('password_input'):
            self.ids.password_input.focus = False

    def update_text(self):
        if self.ids.get('app_title_label'): self.ids.app_title_label.text = get_translation("app_title")
        if self.ids.get('username_label_text'): self.ids.username_label_text.text = get_translation("username_label")
        if self.ids.get('password_label_text'): self.ids.password_label_text.text = get_translation("password_label")
        if self.ids.get('login_button_text'): self.ids.login_button_text.text = get_translation("login_button")

    def login(self):
        username_widget = self.ids.get('username_input')
        password_widget = self.ids.get('password_input')
        status_widget = self.ids.get('status_label')

        if not username_widget or not password_widget:
            if status_widget:
                status_widget.text = get_translation("UI Error: Input fields not found.", "UI Error: Input fields not found.")
                status_widget.color = (1,0,0,1)
            return

        username = username_widget.text
        password = password_widget.text

        print(f"Attempting login with username: '{username}' and password: '{password}'")  # Debug

        if not username or not password:
            if status_widget:
                status_widget.text = get_translation("Username and password cannot be empty.", "Username and password cannot be empty.") 
                status_widget.color = (1,0,0,1)
            return

        running_app = App.get_running_app()
        if not running_app:
             if status_widget:
                  status_widget.text = "Internal error: App instance missing."
                  status_widget.color = (1,0,0,1)
             return

        user, message = running_app.user_service.login_user(username, password)
        print(f"Login result - User: {user}, Message: {message}")  # Debug

        if user:
            running_app.current_user = user 
            if user.role == 'admin':
                self.manager.current = 'admin_dashboard' 
            else: 
                self.manager.current = 'user_dashboard'
        else:
            translated_message = get_translation(message, message) 
            if status_widget:
                status_widget.text = translated_message
                status_widget.color = (1,0,0,1)

class BaseDashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_layout()

    def build_layout(self):
        # Crear el layout principal
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Etiqueta de bienvenida
        self.welcome_label = Label(
            text=get_translation("Welcome", "Welcome"),
            font_size='24sp',
            size_hint_y=0.2
        )
        main_layout.add_widget(self.welcome_label)
        
        # Área de contenido (será poblada por las clases hijas)
        self.content_area = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=0.7
        )
        main_layout.add_widget(self.content_area)
        
        # Botón de logout
        self.logout_button = Button(
            text=get_translation("logout_button", "Logout"),
            font_size='20sp',
            size_hint_y=None,
            height=dp(50)
        )
        self.logout_button.bind(on_press=self.logout_pressed)
        main_layout.add_widget(self.logout_button)
        
        self.add_widget(main_layout)

    def logout_pressed(self, instance):
        app = App.get_running_app()
        if app:
            app.logout()

    def on_enter(self):
        self.update_text()

    def update_text(self):
        if self.welcome_label:
            self.welcome_label.text = get_translation("Welcome", "Welcome")
        if self.logout_button:
            self.logout_button.text = get_translation("logout_button", "Logout")
        self.update_welcome_label()
        self.update_action_buttons_text()

    def update_welcome_label(self):
        # Será implementado por las clases hijas
        pass
    
    def update_action_buttons_text(self):
        # Será implementado por las clases hijas
        pass

class AdminDashboardScreen(BaseDashboardScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_admin_content()

    def create_admin_content(self):
        # Crear botones específicos del admin
        self.manage_programs_btn = Button(
            text=get_translation("manage_programs_button", "Manage Programs"),
            font_size='18sp',
            size_hint_y=None,
            height=dp(48)
        )
        self.manage_programs_btn.bind(on_press=self.manage_programs_action)
        
        self.manage_users_btn = Button(
            text=get_translation("manage_users_button", "Manage Users"),
            font_size='18sp',
            size_hint_y=None,
            height=dp(48)
        )
        self.manage_users_btn.bind(on_press=self.manage_users_action)
        
        # Añadir botones al área de contenido
        self.content_area.add_widget(self.manage_programs_btn)
        self.content_area.add_widget(self.manage_users_btn)

    def update_welcome_label(self):
        app = App.get_running_app()
        welcome_text = get_translation("admin_dashboard", "Admin Dashboard")
        if app and app.current_user:
            welcome_text += f": {app.current_user.username}"
        if self.welcome_label:
            self.welcome_label.text = welcome_text

    def update_action_buttons_text(self):
        if hasattr(self, 'manage_programs_btn'):
            self.manage_programs_btn.text = get_translation("manage_programs_button", "Manage Programs")
        if hasattr(self, 'manage_users_btn'):
            self.manage_users_btn.text = get_translation("manage_users_button", "Manage Users")

    def manage_programs_action(self, instance):
        print("AdminDashboard: Navigating to Manage Programs")
        self.manager.current = 'manage_programs'

    def manage_users_action(self, instance):
        print("AdminDashboard: Navigating to Manage Users")
        self.manager.current = 'manage_users'

class UserDashboardScreen(BaseDashboardScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_user_content()

    def create_user_content(self):
        # Crear botones específicos del usuario
        self.view_programs_btn = Button(
            text=get_translation("view_programs_button", "View Programs"),
            font_size='18sp',
            size_hint_y=None,
            height=dp(48)
        )
        self.view_programs_btn.bind(on_press=self.view_programs_action)
        
        # Añadir botones al área de contenido
        self.content_area.add_widget(self.view_programs_btn)

    def update_welcome_label(self):
        app = App.get_running_app()
        welcome_text = get_translation("user_dashboard", "User Dashboard")
        if app and app.current_user:
            welcome_text += f": {app.current_user.username}"
        if self.welcome_label:
            self.welcome_label.text = welcome_text

    def update_action_buttons_text(self):
        if hasattr(self, 'view_programs_btn'):
            self.view_programs_btn.text = get_translation("view_programs_button", "View Programs")

    def view_programs_action(self, instance):
        """Navegar a la pantalla de ver programas"""
        print("UserDashboard: Navigating to View Programs")
        
        # Comprobar si la pantalla ya existe, y crearla si no
        if not self.manager.has_screen('user_programs'):
            from app.presentation.user_programs_screen import UserProgramsScreen
            user_programs_screen = UserProgramsScreen(name='user_programs')
            self.manager.add_widget(user_programs_screen)
            
        self.manager.current = 'user_programs'

class ManageProgramsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.programs = []
        self.build_layout()

    def build_layout(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Título
        self.title_label = Label(
            text=get_translation("manage_programs_title", "Manage Programs"),
            font_size='24sp',
            size_hint_y=None,
            height=dp(50)
        )
        main_layout.add_widget(self.title_label)
        
        # Botones de acción
        action_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.create_btn = Button(
            text=get_translation("create_new_program", "Create New Program"),
            size_hint_x=0.4
        )
        self.create_btn.bind(on_press=self.create_program_action)
        
        self.back_btn = Button(
            text=get_translation("back_button", "Back"),
            size_hint_x=0.3
        )
        self.back_btn.bind(on_press=self.back_action)
        
        action_layout.add_widget(self.create_btn)
        action_layout.add_widget(Label())  # Spacer
        action_layout.add_widget(self.back_btn)
        main_layout.add_widget(action_layout)
        
        # Lista de programas (scrolleable)
        self.scroll_view = ScrollView()
        self.programs_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.programs_layout.bind(minimum_height=self.programs_layout.setter('height'))
        self.scroll_view.add_widget(self.programs_layout)
        main_layout.add_widget(self.scroll_view)
        
        self.add_widget(main_layout)

    def on_enter(self):
        self.update_text()
        self.load_programs()

    def update_text(self):
        if self.title_label:
            self.title_label.text = get_translation("manage_programs_title", "Manage Programs")
        if self.create_btn:
            self.create_btn.text = get_translation("create_new_program", "Create New Program")
        if self.back_btn:
            self.back_btn.text = get_translation("back_button", "Back")

    def load_programs(self):
        """Cargar la lista de programas desde la base de datos"""
        app = App.get_running_app()
        if not app or not app.program_service:
            return
        
        # Limpiar la lista actual
        self.programs_layout.clear_widgets()
        
        # Obtener programas
        self.programs = app.program_service.get_all_programs()
        
        if not self.programs:
            # Mostrar mensaje de "no hay programas"
            no_programs_label = Label(
                text=get_translation("no_programs_available", "No programs available"),
                font_size='16sp',
                size_hint_y=None,
                height=dp(50)
            )
            self.programs_layout.add_widget(no_programs_label)
        else:
            # Crear widgets para cada programa
            for program in self.programs:
                program_widget = self.create_program_widget(program)
                self.programs_layout.add_widget(program_widget)

    def create_program_widget(self, program):
        """Crear widget para mostrar un programa en la lista"""
        # Layout principal del programa
        program_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(80), spacing=dp(10))
        
        # Información del programa
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.6)
        
        name_label = Label(
            text=program.name,
            font_size='18sp',
            bold=True,
            halign='left',
            valign='middle'
        )
        name_label.bind(size=name_label.setter('text_size'))
        
        desc_label = Label(
            text=program.description or "",
            font_size='14sp',
            halign='left',
            valign='middle',
            color=(0.7, 0.7, 0.7, 1)
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        
        info_layout.add_widget(name_label)
        info_layout.add_widget(desc_label)
        
        # Botones de acción
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_x=0.4, spacing=dp(5))
        
        edit_btn = Button(
            text=get_translation("edit_program", "Edit Program"),
            size_hint_x=0.5
        )
        edit_btn.bind(on_press=lambda x, p=program: self.edit_program_action(p))
        
        delete_btn = Button(
            text=get_translation("delete_program", "Delete Program"),
            size_hint_x=0.5
        )
        delete_btn.bind(on_press=lambda x, p=program: self.delete_program_action(p))
        
        buttons_layout.add_widget(edit_btn)
        buttons_layout.add_widget(delete_btn)
        
        program_layout.add_widget(info_layout)
        program_layout.add_widget(buttons_layout)
        
        return program_layout

    def create_program_action(self, instance):
        """Navegar a la pantalla de crear programa"""
        self.manager.current = 'create_edit_program'
        # Limpiar datos de edición
        create_edit_screen = self.manager.get_screen('create_edit_program')
        create_edit_screen.set_create_mode()

    def edit_program_action(self, program):
        """Navegar a la pantalla de editar programa"""
        self.manager.current = 'create_edit_program'
        # Cargar datos del programa para edición
        create_edit_screen = self.manager.get_screen('create_edit_program')
        create_edit_screen.set_edit_mode(program)

    def delete_program_action(self, program):
        """Mostrar confirmación y eliminar programa"""
        self.show_delete_confirmation(program)

    def show_delete_confirmation(self, program):
        """Mostrar popup de confirmación para eliminar"""
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        message = Label(
            text=get_translation("confirm_delete", "Are you sure you want to delete this program?"),
            text_size=(dp(300), None),
            halign='center'
        )
        content.add_widget(message)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        confirm_btn = Button(text=get_translation("delete_program", "Delete Program"))
        cancel_btn = Button(text=get_translation("cancel_button", "Cancel"))
        
        buttons_layout.add_widget(confirm_btn)
        buttons_layout.add_widget(cancel_btn)
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title=get_translation("delete_program", "Delete Program"),
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        confirm_btn.bind(on_press=lambda x: self.confirm_delete_program(program, popup))
        cancel_btn.bind(on_press=popup.dismiss)
        
        popup.open()

    def confirm_delete_program(self, program, popup):
        """Confirmar y ejecutar eliminación del programa"""
        popup.dismiss()
        
        app = App.get_running_app()
        if app and app.program_service:
            success, message = app.program_service.delete_program(program.id)
            if success:
                # Recargar la lista
                self.load_programs()
                # Mostrar mensaje de éxito (opcional)
                print(f"Program deleted successfully: {program.name}")
            else:
                # Mostrar mensaje de error
                print(f"Error deleting program: {message}")

    def back_action(self, instance):
        """Volver al dashboard de admin"""
        self.manager.current = 'admin_dashboard'

class CreateEditProgramScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_edit_mode = False
        self.current_program = None
        self.steps_widgets = []
        self.build_layout()

    def build_layout(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Título
        self.title_label = Label(
            text=get_translation("create_new_program", "Create New Program"),
            font_size='24sp',
            size_hint_y=None,
            height=dp(50)
        )
        main_layout.add_widget(self.title_label)
        
        # Formulario principal en scroll view
        scroll_view = ScrollView()
        form_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Información básica del programa
        basic_info_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(120))
        
        # Nombre del programa
        name_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        name_label = Label(
            text=get_translation("program_name", "Program Name:"),
            size_hint_x=0.3,
            halign='right',
            valign='middle'
        )
        name_label.bind(size=name_label.setter('text_size'))
        self.name_input = TextInput(
            multiline=False,
            size_hint_x=0.7
        )
        name_layout.add_widget(name_label)
        name_layout.add_widget(self.name_input)
        
        # Descripción del programa
        desc_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(70))
        desc_label = Label(
            text=get_translation("program_description", "Description:"),
            size_hint_x=0.3,
            halign='right',
            valign='top'
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        self.desc_input = TextInput(
            multiline=True,
            size_hint_x=0.7
        )
        desc_layout.add_widget(desc_label)
        desc_layout.add_widget(self.desc_input)
        
        basic_info_layout.add_widget(name_layout)
        basic_info_layout.add_widget(desc_layout)
        form_layout.add_widget(basic_info_layout)
        
        # Sección de pasos
        steps_header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        self.steps_title = Label(
            text=get_translation("program_steps", "Program Steps"),
            font_size='18sp',
            bold=True,
            size_hint_x=0.7,
            halign='left',
            valign='middle'
        )
        self.steps_title.bind(size=self.steps_title.setter('text_size'))
        
        self.add_step_btn = Button(
            text=get_translation("add_step", "Add Step"),
            size_hint_x=0.3,
            size_hint_y=None,
            height=dp(35)
        )
        self.add_step_btn.bind(on_press=self.add_step_action)
        
        steps_header_layout.add_widget(self.steps_title)
        steps_header_layout.add_widget(self.add_step_btn)
        form_layout.add_widget(steps_header_layout)
        
        # Container para los pasos
        self.steps_container = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        self.steps_container.bind(minimum_height=self.steps_container.setter('height'))
        form_layout.add_widget(self.steps_container)
        
        scroll_view.add_widget(form_layout)
        main_layout.add_widget(scroll_view)
        
        # Área de mensajes de error/éxito
        self.status_label = Label(
            text="",
            font_size='16sp',
            size_hint_y=None,
            height=dp(30),
            color=(1, 0, 0, 1)  # Color rojo para errores
        )
        main_layout.add_widget(self.status_label)
        
        # Botones de acción
        action_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.save_btn = Button(
            text=get_translation("save_button", "Save"),
            size_hint_x=0.3
        )
        self.save_btn.bind(on_press=self.save_program_action)
        
        self.cancel_btn = Button(
            text=get_translation("cancel_button", "Cancel"),
            size_hint_x=0.3
        )
        self.cancel_btn.bind(on_press=self.cancel_action)
        
        action_layout.add_widget(self.save_btn)
        action_layout.add_widget(Label())  # Spacer
        action_layout.add_widget(self.cancel_btn)
        main_layout.add_widget(action_layout)
        
        self.add_widget(main_layout)

    def show_message(self, message, is_error=True):
        """Mostrar mensaje en la pantalla"""
        if self.status_label:
            self.status_label.text = get_translation(message, message)
            if is_error:
                self.status_label.color = (1, 0, 0, 1)  # Rojo para errores
            else:
                self.status_label.color = (0, 1, 0, 1)  # Verde para éxito

    def clear_message(self):
        """Limpiar mensaje de estado"""
        if self.status_label:
            self.status_label.text = ""

    def on_enter(self):
        self.update_text()
        self.clear_message()

    def update_text(self):
        if self.title_label:
            if self.is_edit_mode:
                self.title_label.text = get_translation("edit_program", "Edit Program")
            else:
                self.title_label.text = get_translation("create_new_program", "Create New Program")
        
        if self.steps_title:
            self.steps_title.text = get_translation("program_steps", "Program Steps")
        if self.add_step_btn:
            self.add_step_btn.text = get_translation("add_step", "Add Step")
        if self.save_btn:
            self.save_btn.text = get_translation("save_button", "Save")
        if self.cancel_btn:
            self.cancel_btn.text = get_translation("cancel_button", "Cancel")

    def set_create_mode(self):
        """Configurar pantalla para crear nuevo programa"""
        self.is_edit_mode = False
        self.current_program = None
        self.clear_form()

    def set_edit_mode(self, program):
        """Configurar pantalla para editar programa existente"""
        self.is_edit_mode = True
        self.current_program = program
        self.load_program_data(program)

    def clear_form(self):
        """Limpiar todos los campos del formulario"""
        self.name_input.text = ""
        self.desc_input.text = ""
        self.steps_container.clear_widgets()
        self.steps_widgets = []
        self.clear_message()

    def load_program_data(self, program):
        """Cargar datos del programa en el formulario"""
        self.clear_form()
        
        self.name_input.text = program.name
        self.desc_input.text = program.description or ""
        
        # Cargar pasos del programa
        app = App.get_running_app()
        if app and app.program_service:
            _, steps = app.program_service.get_program_by_id(program.id)
            for step in steps:
                self.add_step_widget(step.pressure, step.duration)

    def add_step_action(self, instance):
        """Añadir un nuevo paso vacío"""
        self.add_step_widget()

    def add_step_widget(self, pressure=0.0, duration=60):
        """Crear widget para un paso del programa"""
        step_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        
        # Número del paso
        step_num = len(self.steps_widgets) + 1
        step_label = Label(
            text=f"{get_translation('step_number', 'Step')} {step_num}:",
            size_hint_x=0.2,
            halign='right',
            valign='middle'
        )
        step_label.bind(size=step_label.setter('text_size'))
        
        # Presión
        pressure_label = Label(
            text=get_translation("pressure", "Pressure (bar)"),
            size_hint_x=0.25,
            halign='center',
            valign='middle'
        )
        pressure_label.bind(size=pressure_label.setter('text_size'))
        pressure_input = TextInput(
            text=str(pressure),
            multiline=False,
            size_hint_x=0.2,
            input_filter='float'
        )
        
        # Duración
        duration_label = Label(
            text=get_translation("duration", "Duration (sec)"),
            size_hint_x=0.25,
            halign='center',
            valign='middle'
        )
        duration_label.bind(size=duration_label.setter('text_size'))
        duration_input = TextInput(
            text=str(duration),
            multiline=False,
            size_hint_x=0.2,
            input_filter='int'
        )
        
        # Botón eliminar
        delete_btn = Button(
            text=get_translation("delete_step", "Delete"),
            size_hint_x=0.15
        )
        
        step_layout.add_widget(step_label)
        step_layout.add_widget(pressure_label)
        step_layout.add_widget(pressure_input)
        step_layout.add_widget(duration_label)
        step_layout.add_widget(duration_input)
        step_layout.add_widget(delete_btn)
        
        # Guardar referencias
        step_data = {
            'layout': step_layout,
            'pressure_input': pressure_input,
            'duration_input': duration_input,
            'delete_btn': delete_btn
        }
        self.steps_widgets.append(step_data)
        
        # Configurar acción de eliminar
        delete_btn.bind(on_press=lambda x, s=step_data: self.delete_step_action(s))
        
        self.steps_container.add_widget(step_layout)

    def delete_step_action(self, step_data):
        """Eliminar un paso"""
        if step_data in self.steps_widgets:
            self.steps_widgets.remove(step_data)
            self.steps_container.remove_widget(step_data['layout'])
            # Actualizar numeración de pasos
            self.update_step_numbers()

    def update_step_numbers(self):
        """Actualizar la numeración de los pasos"""
        for i, step_data in enumerate(self.steps_widgets, 1):
            # El primer widget del layout es el label del número de paso
            step_label = step_data['layout'].children[-1]  # Último widget añadido es el primero en la lista
            step_label.text = f"{get_translation('step_number', 'Step')} {i}:"

    def save_program_action(self, instance):
        """Guardar el programa"""
        self.clear_message()
        
        # Recopilar datos del formulario
        name = self.name_input.text.strip()
        description = self.desc_input.text.strip()
        
        # Validación básica
        if not name:
            self.show_message("program_name_required", True)
            return
        
        # Recopilar pasos
        steps_data = []
        for i, step_data in enumerate(self.steps_widgets, 1):
            try:
                pressure_text = step_data['pressure_input'].text.strip()
                duration_text = step_data['duration_input'].text.strip()
                
                if not pressure_text:
                    self.show_message(f"Paso {i}: {get_translation('pressure', 'Pressure')} es requerida", True)
                    return
                
                if not duration_text:
                    self.show_message(f"Paso {i}: {get_translation('duration', 'Duration')} es requerida", True)
                    return
                
                pressure = float(pressure_text)
                duration = int(duration_text)
                
                if pressure < 0:
                    self.show_message(f"Paso {i}: {get_translation('invalid_pressure_value', 'Invalid pressure value')}", True)
                    return
                
                if duration <= 0:
                    self.show_message(f"Paso {i}: {get_translation('invalid_duration_value', 'Invalid duration value')}", True)
                    return
                
                steps_data.append({
                    'pressure': pressure,
                    'duration': duration
                })
            except ValueError:
                self.show_message(f"Paso {i}: Valores numéricos inválidos", True)
                return
        
        # Guardar programa
        app = App.get_running_app()
        if app and app.program_service and app.current_user:
            if self.is_edit_mode and self.current_program:
                # Actualizar programa existente
                success, message = app.program_service.update_program(
                    self.current_program.id, name, description, steps_data
                )
            else:
                # Crear nuevo programa
                success, message, _ = app.program_service.create_program(
                    name, description, app.current_user.id, steps_data
                )
            
            if success:
                self.show_message("program_saved", False)  # Mensaje verde de éxito
                # Esperar un poco y luego volver a la lista
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.go_back_to_list(), 1.5)
            else:
                self.show_message(message, True)

    def go_back_to_list(self):
        """Volver a la lista de programas"""
        self.manager.current = 'manage_programs'
        # Recargar la lista
        manage_screen = self.manager.get_screen('manage_programs')
        manage_screen.load_programs()

    def cancel_action(self, instance):
        """Cancelar y volver a la lista de programas"""
        self.manager.current = 'manage_programs'

class ManageUsersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.users = []
        self.build_layout()

    def build_layout(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Título
        self.title_label = Label(
            text=get_translation("manage_users_title", "Manage Users"),
            font_size='24sp',
            size_hint_y=None,
            height=dp(50)
        )
        main_layout.add_widget(self.title_label)
        
        # Botones de acción
        action_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.create_btn = Button(
            text=get_translation("create_new_user", "Create New User"),
            size_hint_x=0.4
        )
        self.create_btn.bind(on_press=self.create_user_action)
        
        self.back_btn = Button(
            text=get_translation("back_button", "Back"),
            size_hint_x=0.3
        )
        self.back_btn.bind(on_press=self.back_action)
        
        action_layout.add_widget(self.create_btn)
        action_layout.add_widget(Label())  # Spacer
        action_layout.add_widget(self.back_btn)
        main_layout.add_widget(action_layout)
        
        # Lista de usuarios (scrolleable)
        self.scroll_view = ScrollView()
        self.users_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.users_layout.bind(minimum_height=self.users_layout.setter('height'))
        self.scroll_view.add_widget(self.users_layout)
        main_layout.add_widget(self.scroll_view)
        
        self.add_widget(main_layout)

    def on_enter(self):
        self.update_text()
        self.load_users()

    def update_text(self):
        if self.title_label:
            self.title_label.text = get_translation("manage_users_title", "Manage Users")
        if self.create_btn:
            self.create_btn.text = get_translation("create_new_user", "Create New User")
        if self.back_btn:
            self.back_btn.text = get_translation("back_button", "Back")

    def load_users(self):
        """Cargar la lista de usuarios desde la base de datos"""
        app = App.get_running_app()
        if not app or not app.user_service:
            return
        
        # Limpiar la lista actual
        self.users_layout.clear_widgets()
        
        # Obtener usuarios
        self.users = app.user_service.get_all_users()
        
        if not self.users:
            # Mostrar mensaje de "no hay usuarios"
            no_users_label = Label(
                text=get_translation("no_users_available", "No users available"),
                font_size='16sp',
                size_hint_y=None,
                height=dp(50)
            )
            self.users_layout.add_widget(no_users_label)
        else:
            # Crear widgets para cada usuario
            for user in self.users:
                user_widget = self.create_user_widget(user)
                self.users_layout.add_widget(user_widget)

    def create_user_widget(self, user):
        """Crear widget para mostrar un usuario en la lista"""
        # Layout principal del usuario
        user_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(80), spacing=dp(10))
        
        # Información del usuario
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.5)
        
        username_label = Label(
            text=user.username,
            font_size='18sp',
            bold=True,
            halign='left',
            valign='middle'
        )
        username_label.bind(size=username_label.setter('text_size'))
        
        role_text = get_translation("role_admin", "Administrator") if user.role == 'admin' else get_translation("role_user", "User")
        status_text = get_translation("status_active", "Active") if user.is_active else get_translation("status_inactive", "Inactive")
        details_label = Label(
            text=f"{get_translation('user_role', 'Role:')} {role_text} | {get_translation('user_status', 'Status:')} {status_text}",
            font_size='14sp',
            halign='left',
            valign='middle',
            color=(0.7, 0.7, 0.7, 1)
        )
        details_label.bind(size=details_label.setter('text_size'))
        
        info_layout.add_widget(username_label)
        info_layout.add_widget(details_label)
        
        # Botones de acción
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_x=0.5, spacing=dp(5))
        
        edit_btn = Button(
            text=get_translation("edit_user", "Edit User"),
            size_hint_x=0.5
        )
        edit_btn.bind(on_press=lambda x, u=user: self.edit_user_action(u))
        
        if user.is_active:
            status_btn = Button(
                text=get_translation("deactivate_user", "Deactivate"),
                size_hint_x=0.5
            )
            status_btn.bind(on_press=lambda x, u=user: self.deactivate_user_action(u))
        else:
            status_btn = Button(
                text=get_translation("activate_user", "Activate"),
                size_hint_x=0.5
            )
            status_btn.bind(on_press=lambda x, u=user: self.activate_user_action(u))
        
        buttons_layout.add_widget(edit_btn)
        buttons_layout.add_widget(status_btn)
        
        user_layout.add_widget(info_layout)
        user_layout.add_widget(buttons_layout)
        
        return user_layout

    def create_user_action(self, instance):
        """Navegar a la pantalla de crear usuario"""
        self.manager.current = 'create_edit_user'
        # Limpiar datos de edición
        create_edit_screen = self.manager.get_screen('create_edit_user')
        create_edit_screen.set_create_mode()

    def edit_user_action(self, user):
        """Navegar a la pantalla de editar usuario"""
        self.manager.current = 'create_edit_user'
        # Cargar datos del usuario para edición
        create_edit_screen = self.manager.get_screen('create_edit_user')
        create_edit_screen.set_edit_mode(user)

    def activate_user_action(self, user):
        """Activar usuario"""
        app = App.get_running_app()
        if app and app.user_service:
            success, message = app.user_service.activate_user(user.id)
            if success:
                # Recargar la lista
                self.load_users()
                print(f"User activated successfully: {user.username}")
            else:
                print(f"Error activating user: {message}")

    def deactivate_user_action(self, user):
        """Mostrar confirmación y desactivar usuario"""
        self.show_deactivate_confirmation(user)

    def show_deactivate_confirmation(self, user):
        """Mostrar popup de confirmación para desactivar"""
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        message = Label(
            text=get_translation("confirm_deactivate", "Are you sure you want to deactivate this user?"),
            text_size=(dp(300), None),
            halign='center'
        )
        content.add_widget(message)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        confirm_btn = Button(text=get_translation("deactivate_user", "Deactivate"))
        cancel_btn = Button(text=get_translation("cancel_button", "Cancel"))
        
        buttons_layout.add_widget(confirm_btn)
        buttons_layout.add_widget(cancel_btn)
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title=get_translation("deactivate_user", "Deactivate User"),
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        confirm_btn.bind(on_press=lambda x: self.confirm_deactivate_user(user, popup))
        cancel_btn.bind(on_press=popup.dismiss)
        
        popup.open()

    def confirm_deactivate_user(self, user, popup):
        """Confirmar y ejecutar desactivación del usuario"""
        popup.dismiss()
        
        app = App.get_running_app()
        if app and app.user_service:
            success, message = app.user_service.deactivate_user(user.id)
            if success:
                # Recargar la lista
                self.load_users()
                print(f"User deactivated successfully: {user.username}")
            else:
                print(f"Error deactivating user: {message}")

    def back_action(self, instance):
        """Volver al dashboard de admin"""
        self.manager.current = 'admin_dashboard'

class CreateEditUserScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_edit_mode = False
        self.current_user = None
        self.build_layout()

    def build_layout(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Título
        self.title_label = Label(
            text=get_translation("create_new_user", "Create New User"),
            font_size='24sp',
            size_hint_y=None,
            height=dp(50)
        )
        main_layout.add_widget(self.title_label)
        
        # Formulario
        form_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=0.6)
        
        # Username
        username_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        username_label = Label(
            text=get_translation("username_label", "Username:"),
            size_hint_x=0.3,
            halign='right',
            valign='middle'
        )
        username_label.bind(size=username_label.setter('text_size'))
        self.username_input = TextInput(
            multiline=False,
            size_hint_x=0.7
        )
        username_layout.add_widget(username_label)
        username_layout.add_widget(self.username_input)
        
        # Password
        password_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        password_label = Label(
            text=get_translation("password_label", "Password:"),
            size_hint_x=0.3,
            halign='right',
            valign='middle'
        )
        password_label.bind(size=password_label.setter('text_size'))
        self.password_input = TextInput(
            multiline=False,
            password=True,
            size_hint_x=0.7
        )
        password_layout.add_widget(password_label)
        password_layout.add_widget(self.password_input)
        
        # Confirm Password
        confirm_password_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        confirm_password_label = Label(
            text=get_translation("confirm_password", "Confirm Password:"),
            size_hint_x=0.3,
            halign='right',
            valign='middle'
        )
        confirm_password_label.bind(size=confirm_password_label.setter('text_size'))
        self.confirm_password_input = TextInput(
            multiline=False,
            password=True,
            size_hint_x=0.7
        )
        confirm_password_layout.add_widget(confirm_password_label)
        confirm_password_layout.add_widget(self.confirm_password_input)
        
        # Role
        role_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        role_label = Label(
            text=get_translation("user_role", "Role:"),
            size_hint_x=0.3,
            halign='right',
            valign='middle'
        )
        role_label.bind(size=role_label.setter('text_size'))
        self.role_spinner = Spinner(
            text=get_translation("role_user", "User"),
            values=[get_translation("role_user", "User"), get_translation("role_admin", "Administrator")],
            size_hint_x=0.7
        )
        role_layout.add_widget(role_label)
        role_layout.add_widget(self.role_spinner)
        
        # Info label for edit mode
        self.info_label = Label(
            text="",
            font_size='14sp',
            size_hint_y=None,
            height=dp(30),
            color=(0.7, 0.7, 0.7, 1)
        )
        
        form_layout.add_widget(username_layout)
        form_layout.add_widget(password_layout)
        form_layout.add_widget(confirm_password_layout)
        form_layout.add_widget(role_layout)
        form_layout.add_widget(self.info_label)
        
        main_layout.add_widget(form_layout)
        
        # Área de mensajes de error/éxito
        self.status_label = Label(
            text="",
            font_size='16sp',
            size_hint_y=None,
            height=dp(30),
            color=(1, 0, 0, 1)  # Color rojo para errores
        )
        main_layout.add_widget(self.status_label)
        
        # Botones de acción
        action_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.save_btn = Button(
            text=get_translation("save_button", "Save"),
            size_hint_x=0.3
        )
        self.save_btn.bind(on_press=self.save_user_action)
        
        self.cancel_btn = Button(
            text=get_translation("cancel_button", "Cancel"),
            size_hint_x=0.3
        )
        self.cancel_btn.bind(on_press=self.cancel_action)
        
        action_layout.add_widget(self.save_btn)
        action_layout.add_widget(Label())  # Spacer
        action_layout.add_widget(self.cancel_btn)
        main_layout.add_widget(action_layout)
        
        self.add_widget(main_layout)

    def show_message(self, message, is_error=True):
        """Mostrar mensaje en la pantalla"""
        if self.status_label:
            self.status_label.text = get_translation(message, message)
            if is_error:
                self.status_label.color = (1, 0, 0, 1)  # Rojo para errores
            else:
                self.status_label.color = (0, 1, 0, 1)  # Verde para éxito

    def clear_message(self):
        """Limpiar mensaje de estado"""
        if self.status_label:
            self.status_label.text = ""

    def on_enter(self):
        self.update_text()
        self.clear_message()

    def update_text(self):
        if self.title_label:
            if self.is_edit_mode:
                self.title_label.text = get_translation("edit_user", "Edit User")
            else:
                self.title_label.text = get_translation("create_new_user", "Create New User")
        
        if self.save_btn:
            self.save_btn.text = get_translation("save_button", "Save")
        if self.cancel_btn:
            self.cancel_btn.text = get_translation("cancel_button", "Cancel")
        
        if self.is_edit_mode:
            self.info_label.text = get_translation("leave_blank_to_keep", "Leave blank to keep current password")
        else:
            self.info_label.text = ""

    def set_create_mode(self):
        """Configurar pantalla para crear nuevo usuario"""
        self.is_edit_mode = False
        self.current_user = None
        self.clear_form()

    def set_edit_mode(self, user):
        """Configurar pantalla para editar usuario existente"""
        self.is_edit_mode = True
        self.current_user = user
        self.load_user_data(user)

    def clear_form(self):
        """Limpiar todos los campos del formulario"""
        self.username_input.text = ""
        self.password_input.text = ""
        self.confirm_password_input.text = ""
        self.role_spinner.text = get_translation("role_user", "User")
        self.clear_message()

    def load_user_data(self, user):
        """Cargar datos del usuario en el formulario"""
        self.clear_form()
        
        self.username_input.text = user.username
        if user.role == 'admin':
            self.role_spinner.text = get_translation("role_admin", "Administrator")
        else:
            self.role_spinner.text = get_translation("role_user", "User")

    def save_user_action(self, instance):
        """Guardar el usuario"""
        self.clear_message()
        
        # Recopilar datos del formulario
        username = self.username_input.text.strip()
        password = self.password_input.text
        confirm_password = self.confirm_password_input.text
        
        # Determinar rol
        role = 'admin' if self.role_spinner.text == get_translation("role_admin", "Administrator") else 'user'
        
        # Validaciones
        if not username:
            self.show_message("username_required", True)
            return
        
        if not self.is_edit_mode:
            # Para crear usuario, la contraseña es obligatoria
            if not password:
                self.show_message("password_required", True)
                return
        
        if password:
            # Si se proporciona contraseña, validar
            if len(password) < 6:
                self.show_message("password_too_short", True)
                return
            
            if password != confirm_password:
                self.show_message("passwords_do_not_match", True)
                return
        
        # Guardar usuario
        app = App.get_running_app()
        if app and app.user_service:
            if self.is_edit_mode and self.current_user:
                # Actualizar usuario existente
                success, message = app.user_service.update_user(
                    self.current_user.id, username, role, password if password else None
                )
            else:
                # Crear nuevo usuario
                success, message, _ = app.user_service.create_user(username, password, role)
            
            if success:
                self.show_message(message, False)  # Mensaje verde de éxito
                # Esperar un poco y luego volver a la lista
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.go_back_to_list(), 1.5)
            else:
                self.show_message(message, True)

    def go_back_to_list(self):
        """Volver a la lista de usuarios"""
        self.manager.current = 'manage_users'
        # Recargar la lista
        manage_screen = self.manager.get_screen('manage_users')
        manage_screen.load_users()

    def cancel_action(self, instance):
        """Cancelar y volver a la lista de usuarios"""
        self.manager.current = 'manage_users'

# Registrar todas las clases en el Factory de Kivy ANTES de cargar el KV
Factory.register('LoginScreen', LoginScreen)
Factory.register('AdminDashboardScreen', AdminDashboardScreen)
Factory.register('UserDashboardScreen', UserDashboardScreen)
Factory.register('ManageProgramsScreen', ManageProgramsScreen)
Factory.register('CreateEditProgramScreen', CreateEditProgramScreen)
Factory.register('ManageUsersScreen', ManageUsersScreen)
Factory.register('CreateEditUserScreen', CreateEditUserScreen)
Factory.register('UserProgramsScreen', UserProgramsScreen)

class ElectronicControlApp(App):
    # CAMBIO CRÍTICO: Permitir que current_user sea None
    current_user = ObjectProperty(allownone=True)
    current_language_display_name = StringProperty()
    available_languages_display_names = ListProperty(["English", "Español", "Français"])
    language_map = {"English": "en", "Español": "es", "Français": "fr"}
    language_map_inverted = {v: k for k, v in language_map.items()}

    def __init__(self, application_instance, **kwargs):
        super().__init__(**kwargs)
        self.application = application_instance
        self.user_service = self.application.user_service
        self.program_service = self.application.program_service
        self.program_execution_service = getattr(self.application, 'program_execution_service', None)
        self.hardware_simulator = getattr(self.application, 'hardware_simulator', None)
        self._set_initial_language_properties()

    def _set_initial_language_properties(self):
        current_lang_code = get_current_language()
        self.current_language_display_name = self.language_map_inverted.get(current_lang_code, "English")

    def build(self):
        try:
            current_dir = os.path.dirname(__file__) 
            kv_file_path = os.path.join(current_dir, 'electronic_control.kv')
            if not os.path.exists(kv_file_path):
                kv_file_path_alt = os.path.join(os.getcwd(), 'app', 'presentation', 'electronic_control.kv')
                if os.path.exists(kv_file_path_alt): kv_file_path = kv_file_path_alt
                else: raise FileNotFoundError(f"KV file 'electronic_control.kv' not found.")
            
            # Cargar el archivo KV
            root_widget = Builder.load_file(kv_file_path)
            
            # Forzar actualización inmediata de textos después de cargar
            self.update_ui_texts_recursive(root_widget)
            
            return root_widget
        except Exception as e:
            print(f"Error loading KV file: {e}")
            error_label = Label(text=f"Error loading UI. Check KV file and console output.\nDetails: {str(e)[:500]}...")
            error_label.bind(size=error_label.setter('text_size'))
            return error_label

    def on_start(self):
        if self.root and hasattr(self.root, 'current') and isinstance(self.root, ScreenManager):
            self.root.current = 'login' 
            # Forzar actualización de textos al iniciar
            self.update_ui_texts_recursive(self.root) 
        else:
            if self.root: print(f"Root widget type: {type(self.root)}")
            else: print("Root widget not found at on_start.")

    def logout(self):
        self.current_user = None 
        if self.root and hasattr(self.root, 'current'):
            self.root.current = 'login'

    def change_language_from_spinner(self, display_name):
        lang_code = self.language_map.get(display_name)
        if lang_code and lang_code != get_current_language():
            set_current_language(lang_code)
            self.current_language_display_name = display_name
            self.update_ui_texts_recursive(self.root)

    def update_ui_texts_recursive(self, widget):
        if not widget: return
        if hasattr(widget, 'update_text') and callable(widget.update_text):
            widget.update_text()
        for child in widget.children:
            self.update_ui_texts_recursive(child)