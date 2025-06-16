from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock

# Usar una función segura de traducción
def translate(key, default=None):
    """Helper function to safely get translations"""
    try:
        from app.i18n.translations import _
        return _(key, default if default is not None else key)
    except Exception as e:
        print(f"Translation error: {e}")
        return default if default is not None else key

class UserProgramsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.programs = []
        self.selected_program = None
        self.build_layout()
        
    def build_layout(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Título
        self.title_label = Label(
            text=translate("view_programs_title", "Programs"),
            font_size='24sp',
            size_hint_y=None,
            height=dp(50)
        )
        main_layout.add_widget(self.title_label)
        
        # Panel principal con división
        main_panel = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=0.8
        )
        
        # Panel izquierdo - Lista de programas
        list_panel = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_x=0.4
        )
        
        # Título de la lista
        list_title = Label(
            text=translate("available_programs", "Available Programs"),
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        list_panel.add_widget(list_title)
        
        # Lista de programas (scrolleable)
        self.scroll_view = ScrollView(
            bar_width=dp(10),
            bar_color=[0.7, 0.7, 0.7, 0.9],
            effect_cls='ScrollEffect'
        )
        
        self.programs_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        self.programs_layout.bind(minimum_height=self.programs_layout.setter('height'))
        self.scroll_view.add_widget(self.programs_layout)
        list_panel.add_widget(self.scroll_view)
        
        # Panel derecho - Detalles del programa
        detail_panel = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_x=0.6
        )
        
        # Título de detalles
        detail_title = Label(
            text=translate("program_details", "Program Details"),
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        detail_panel.add_widget(detail_title)
        
        # Contenido de detalles
        self.detail_content = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(150)
        )
        
        # Nombre del programa
        self.detail_content.add_widget(Label(
            text=translate("program_name", "Program name:"),
            halign='right',
            valign='middle',
            size_hint_x=0.3
        ))
        
        self.program_name_label = Label(
            text="",
            halign='left',
            valign='middle',
            size_hint_x=0.7
        )
        self.detail_content.add_widget(self.program_name_label)
        
        # Descripción
        self.detail_content.add_widget(Label(
            text=translate("program_description", "Description:"),
            halign='right',
            valign='top',
            size_hint_x=0.3
        ))
        
        self.program_desc_label = Label(
            text="",
            halign='left',
            valign='top',
            size_hint_x=0.7
        )
        self.detail_content.add_widget(self.program_desc_label)
        
        # Número de pasos
        self.detail_content.add_widget(Label(
            text=translate("program_steps_count", "Steps:"),
            halign='right',
            valign='middle',
            size_hint_x=0.3
        ))
        
        self.program_steps_label = Label(
            text="",
            halign='left',
            valign='middle',
            size_hint_x=0.7
        )
        self.detail_content.add_widget(self.program_steps_label)
        
        detail_panel.add_widget(self.detail_content)
        
        # Lista de pasos (scrolleable)
        steps_title = Label(
            text=translate("program_steps", "Program Steps"),
            font_size='16sp',
            size_hint_y=None,
            height=dp(30)
        )
        detail_panel.add_widget(steps_title)
        
        self.steps_scroll = ScrollView(
            bar_width=dp(10),
            bar_color=[0.7, 0.7, 0.7, 0.9],
            effect_cls='ScrollEffect'
        )
        
        self.steps_layout = GridLayout(
            cols=3,
            spacing=dp(5),
            size_hint_y=None
        )
        self.steps_layout.bind(minimum_height=self.steps_layout.setter('height'))
        
        # Añadir cabecera de pasos
        self.steps_layout.add_widget(Label(
            text=translate("step_number", "Step"),
            bold=True,
            size_hint_x=0.2
        ))
        self.steps_layout.add_widget(Label(
            text=translate("pressure", "Pressure (bar)"),
            bold=True,
            size_hint_x=0.4
        ))
        self.steps_layout.add_widget(Label(
            text=translate("duration", "Duration (sec)"),
            bold=True,
            size_hint_x=0.4
        ))
        
        self.steps_scroll.add_widget(self.steps_layout)
        detail_panel.add_widget(self.steps_scroll)
        
        # Botones de acción para el programa seleccionado
        action_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50),
            padding=[0, dp(10), 0, 0]
        )
        
        self.execute_button = Button(
            text=translate("execute_program_button", "Execute Program"),
            size_hint_x=0.5,
            disabled=True
        )
        self.execute_button.bind(on_press=self.execute_program_action)
        action_layout.add_widget(self.execute_button)
        
        detail_panel.add_widget(action_layout)
        
        # Añadir paneles al panel principal
        main_panel.add_widget(list_panel)
        main_panel.add_widget(detail_panel)
        main_layout.add_widget(main_panel)
        
        # Botón de volver
        back_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50)
        )
        
        back_button = Button(
            text=translate("back_button", "Back"),
            size_hint_x=0.3
        )
        back_button.bind(on_press=self.back_action)
        
        back_layout.add_widget(back_button)
        back_layout.add_widget(Label(size_hint_x=0.7))  # Spacer
        main_layout.add_widget(back_layout)
        
        # Añadir el layout principal a la pantalla
        self.add_widget(main_layout)
    
    def on_enter(self):
        # Programar el cargado de programas para que ocurra después de que la pantalla sea visible
        Clock.schedule_once(lambda dt: self.load_programs(), 0.1)
        print("UserProgramsScreen: on_enter called")
    
    def load_programs(self):
        """Cargar la lista de programas desde la base de datos"""
        print("UserProgramsScreen: Loading programs...")
        self.programs_layout.clear_widgets()
        
        app = App.get_running_app()
        if app and hasattr(app, 'program_service'):
            # Obtener solo programas activos para usuarios normales
            self.programs = app.program_service.get_all_programs(active_only=True)
            
            if not self.programs:
                print("UserProgramsScreen: No programs available")
                no_programs_label = Label(
                    text=translate("no_programs_available", "No programs available"),
                    size_hint_y=None,
                    height=dp(40)
                )
                self.programs_layout.add_widget(no_programs_label)
            else:
                print(f"UserProgramsScreen: Loaded {len(self.programs)} programs")
                for program in self.programs:
                    program_button = Button(
                        text=program.name,
                        size_hint_y=None,
                        height=dp(50)
                    )
                    program_button.bind(on_press=lambda btn, p=program: self.select_program(p))
                    self.programs_layout.add_widget(program_button)
        else:
            print("UserProgramsScreen: program_service not available")
    
    def select_program(self, program):
        """Seleccionar un programa para ver sus detalles"""
        self.selected_program = program
        self.program_name_label.text = program.name
        self.program_desc_label.text = program.description or translate("no_description", "No description available")
        
        # Limpiar los pasos anteriores (excepto la cabecera)
        self.steps_layout.clear_widgets()
        
        # Añadir cabecera de pasos
        self.steps_layout.add_widget(Label(
            text=translate("step_number", "Step"),
            bold=True,
            size_hint_x=0.2
        ))
        self.steps_layout.add_widget(Label(
            text=translate("pressure", "Pressure (bar)"),
            bold=True,
            size_hint_x=0.4
        ))
        self.steps_layout.add_widget(Label(
            text=translate("duration", "Duration (sec)"),
            bold=True,
            size_hint_x=0.4
        ))
        
        # Cargar pasos
        app = App.get_running_app()
        if app and hasattr(app, 'program_service'):
            _, steps = app.program_service.get_program_by_id(program.id)
            
            if steps:
                self.program_steps_label.text = str(len(steps))
                
                for step in steps:
                    # Número de paso
                    step_num_label = Label(
                        text=str(step.step_number),
                        size_hint_x=0.2,
                        size_hint_y=None,
                        height=dp(30)
                    )
                    self.steps_layout.add_widget(step_num_label)
                    
                    # Presión
                    pressure_label = Label(
                        text=f"{step.pressure}",
                        size_hint_x=0.4,
                        size_hint_y=None,
                        height=dp(30)
                    )
                    self.steps_layout.add_widget(pressure_label)
                    
                    # Duración
                    duration_label = Label(
                        text=f"{step.duration}",
                        size_hint_x=0.4,
                        size_hint_y=None,
                        height=dp(30)
                    )
                    self.steps_layout.add_widget(duration_label)
            else:
                self.program_steps_label.text = "0"
        else:
            self.program_steps_label.text = "?"
        
        # Habilitar botón de ejecución
        self.execute_button.disabled = False
    
    def execute_program_action(self, instance):
        """Ejecutar el programa seleccionado"""
        if not self.selected_program:
            return
            
        # Si la pantalla de ejecución existe, nos movemos a ella
        if self.manager.has_screen('execute_program'):
            execute_screen = self.manager.get_screen('execute_program')
            if hasattr(execute_screen, 'select_program'):
                execute_screen.select_program(self.selected_program)
                self.manager.current = 'execute_program'
            else:
                print("Error: execute_screen doesn't have select_program method")
        else:
            # Si no existe, mostramos un mensaje
            print("Error: execute_program screen does not exist")
    
    def back_action(self, instance):
        """Volver al dashboard"""
        self.manager.current = 'user_dashboard'