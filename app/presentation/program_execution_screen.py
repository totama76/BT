from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
from kivy.properties import NumericProperty, StringProperty

from app.i18n.translations import get_translation, _

class ExecuteProgramScreen(Screen):
    progress_value = NumericProperty(0)
    elapsed_time = StringProperty("00:00")
    remaining_time = StringProperty("--:--")
    current_step = StringProperty("--")
    current_pressure = StringProperty("0.0")
    current_duration = StringProperty("0")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_program = None
        self.clock_event = None
        self.build_layout()
        
    def build_layout(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Título
        self.title_label = Label(
            text=get_translation("execute_program_title", "Execute Program"),
            font_size='24sp',
            size_hint_y=None,
            height=dp(50)
        )
        main_layout.add_widget(self.title_label)
        
        # Panel de selección de programa
        self.program_selection_panel = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None,
            height=dp(300)
        )
        self.rebuild_program_list()
        main_layout.add_widget(self.program_selection_panel)
        
        # Panel de ejecución (inicialmente oculto)
        self.execution_panel = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(10)
        )
        
        # Información del programa
        self.program_info = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(180)
        )
        
        # Nombre del programa
        self.program_info.add_widget(Label(
            text=get_translation("program_name", "Program name:"),
            halign='right',
            valign='middle',
            size_hint_x=0.4
        ))
        
        self.program_name_label = Label(
            text="",
            halign='left',
            valign='middle',
            size_hint_x=0.6
        )
        self.program_info.add_widget(self.program_name_label)
        
        # Progreso
        self.program_info.add_widget(Label(
            text=get_translation("progress", "Progress:"),
            halign='right',
            valign='middle'
        ))
        
        progress_layout = BoxLayout(orientation='vertical')
        self.progress_bar = ProgressBar(max=100, value=0)
        self.progress_text = Label(
            text="0%",
            size_hint_y=None,
            height=dp(20)
        )
        progress_layout.add_widget(self.progress_bar)
        progress_layout.add_widget(self.progress_text)
        self.program_info.add_widget(progress_layout)
        
        # Tiempo transcurrido
        self.program_info.add_widget(Label(
            text=get_translation("elapsed_time", "Elapsed time:"),
            halign='right',
            valign='middle'
        ))
        
        self.elapsed_label = Label(
            text="00:00",
            halign='left',
            valign='middle'
        )
        self.program_info.add_widget(self.elapsed_label)
        
        # Tiempo restante
        self.program_info.add_widget(Label(
            text=get_translation("remaining_time", "Remaining time:"),
            halign='right',
            valign='middle'
        ))
        
        self.remaining_label = Label(
            text="--:--",
            halign='left',
            valign='middle'
        )
        self.program_info.add_widget(self.remaining_label)
        
        # Paso actual
        self.program_info.add_widget(Label(
            text=get_translation("current_step", "Current step:"),
            halign='right',
            valign='middle'
        ))
        
        self.step_label = Label(
            text="--",
            halign='left',
            valign='middle'
        )
        self.program_info.add_widget(self.step_label)
        
        # Presión actual
        self.program_info.add_widget(Label(
            text=get_translation("current_pressure", "Current pressure:"),
            halign='right',
            valign='middle'
        ))
        
        self.pressure_label = Label(
            text="0.0 bar",
            halign='left',
            valign='middle'
        )
        self.program_info.add_widget(self.pressure_label)
        
        # Añadir el panel de información
        self.execution_panel.add_widget(self.program_info)
        
        # Botones de control
        control_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        self.start_button = Button(
            text=get_translation("start_execution", "Start"),
            size_hint_x=0.25
        )
        self.start_button.bind(on_press=self.start_execution)
        
        self.pause_button = Button(
            text=get_translation("pause_execution", "Pause"),
            size_hint_x=0.25,
            disabled=True
        )
        self.pause_button.bind(on_press=self.pause_execution)
        
        self.stop_button = Button(
            text=get_translation("stop_execution", "Stop"),
            size_hint_x=0.25,
            disabled=True
        )
        self.stop_button.bind(on_press=self.stop_execution)
        
        self.back_button = Button(
            text=get_translation("back_button", "Back"),
            size_hint_x=0.25
        )
        self.back_button.bind(on_press=self.back_action)
        
        control_layout.add_widget(self.start_button)
        control_layout.add_widget(self.pause_button)
        control_layout.add_widget(self.stop_button)
        control_layout.add_widget(self.back_button)
        
        self.execution_panel.add_widget(control_layout)
        
        # Panel de registro
        log_container = BoxLayout(
            orientation='vertical',
            size_hint_y=0.3,
            padding=[0, dp(15), 0, 0]
        )
        
        log_label = Label(
            text=get_translation("execution_log", "Execution Log"),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        log_container.add_widget(log_label)
        
        self.log_scroll = ScrollView(
            bar_width=dp(10),
            bar_color=[0.7, 0.7, 0.7, 0.9],
            bar_inactive_color=[0.5, 0.5, 0.5, 0.5],
            effect_cls='ScrollEffect'
        )
        
        self.log_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(2),
            size_hint_y=None
        )
        self.log_layout.bind(minimum_height=self.log_layout.setter('height'))
        
        self.log_scroll.add_widget(self.log_layout)
        log_container.add_widget(self.log_scroll)
        
        self.execution_panel.add_widget(log_container)
        
        # Inicialmente oculto
        self.execution_panel.opacity = 0
        self.execution_panel.disabled = True
        self.execution_panel.size_hint_y = 0
        
        main_layout.add_widget(self.execution_panel)
        
        # Mensajes de estado
        self.status_label = Label(
            text="",
            font_size='16sp',
            size_hint_y=None,
            height=dp(30),
            color=(1, 0, 0, 1)  # Color rojo para errores
        )
        main_layout.add_widget(self.status_label)
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        self.update_text()
        self.rebuild_program_list()
        self.hide_execution_panel()
        self.status_label.text = ""
    
    def on_leave(self):
        # Asegurarse de detener la ejecución al salir de la pantalla
        app = App.get_running_app()
        if app and hasattr(app, 'program_execution_service'):
            app.program_execution_service.stop_execution()
        
        # Detener el reloj de actualización
        if self.clock_event:
            self.clock_event.cancel()
    
    def update_text(self):
        """Actualiza los textos según el idioma actual"""
        if self.title_label:
            self.title_label.text = get_translation("execute_program_title", "Execute Program")
        
        if hasattr(self, 'program_info') and self.program_info:
            # Actualizar etiquetas en program_info
            for i, child in enumerate(self.program_info.children):
                if isinstance(child, Label):
                    if "Program name" in child.text:
                        child.text = get_translation("program_name", "Program name:")
                    elif "Progress" in child.text:
                        child.text = get_translation("progress", "Progress:")
                    elif "Elapsed time" in child.text:
                        child.text = get_translation("elapsed_time", "Elapsed time:")
                    elif "Remaining time" in child.text:
                        child.text = get_translation("remaining_time", "Remaining time:")
                    elif "Current step" in child.text:
                        child.text = get_translation("current_step", "Current step:")
                    elif "Current pressure" in child.text:
                        child.text = get_translation("current_pressure", "Current pressure:")
        
        if self.start_button:
            self.start_button.text = get_translation("start_execution", "Start")
        if self.pause_button:
            if self.pause_button.text == "Pause":
                self.pause_button.text = get_translation("pause_execution", "Pause")
            elif self.pause_button.text == "Resume":
                self.pause_button.text = get_translation("resume_execution", "Resume")
        if self.stop_button:
            self.stop_button.text = get_translation("stop_execution", "Stop")
        if self.back_button:
            self.back_button.text = get_translation("back_button", "Back")
    
    def rebuild_program_list(self):
        """Reconstruye la lista de programas disponibles"""
        self.program_selection_panel.clear_widgets()
        
        title_label = Label(
            text=get_translation("select_program", "Select a Program"),
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        self.program_selection_panel.add_widget(title_label)
        
        scroll = ScrollView(
            bar_width=dp(10),
            bar_color=[0.7, 0.7, 0.7, 0.9],
            effect_cls='ScrollEffect'
        )
        
        programs_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        programs_layout.bind(minimum_height=programs_layout.setter('height'))
        
        # Obtener programas
        app = App.get_running_app()
        if app and app.program_service:
            programs = app.program_service.get_all_programs(active_only=True)
            
            if not programs:
                no_programs_label = Label(
                    text=get_translation("no_programs_available", "No programs available"),
                    size_hint_y=None,
                    height=dp(40)
                )
                programs_layout.add_widget(no_programs_label)
            else:
                for program in programs:
                    program_button = Button(
                        text=program.name,
                        size_hint_y=None,
                        height=dp(50)
                    )
                    program_button.bind(on_press=lambda btn, p=program: self.select_program(p))
                    programs_layout.add_widget(program_button)
        
        scroll.add_widget(programs_layout)
        self.program_selection_panel.add_widget(scroll)
    
    def select_program(self, program):
        """Selecciona un programa para ejecutar"""
        self.selected_program = program
        self.show_execution_panel()
        
        # Cargar el programa en el servicio de ejecución
        app = App.get_running_app()
        if app and hasattr(app, 'program_execution_service'):
            success, message = app.program_execution_service.load_program(program.id)
            if success:
                self.program_name_label.text = program.name
                self.reset_execution_display()
            else:
                self.show_message(message, True)
    
    def show_execution_panel(self):
        """Muestra el panel de ejecución"""
        self.program_selection_panel.opacity = 0
        self.program_selection_panel.disabled = True
        self.program_selection_panel.size_hint_y = 0
        
        self.execution_panel.opacity = 1
        self.execution_panel.disabled = False
        self.execution_panel.size_hint_y = 0.7
        
        # Reiniciar los controles
        self.start_button.disabled = False
        self.pause_button.disabled = True
        self.stop_button.disabled = True
        self.pause_button.text = get_translation("pause_execution", "Pause")
    
    def hide_execution_panel(self):
        """Oculta el panel de ejecución"""
        self.program_selection_panel.opacity = 1
        self.program_selection_panel.disabled = False
        self.program_selection_panel.size_hint_y = 0.5
        
        self.execution_panel.opacity = 0
        self.execution_panel.disabled = True
        self.execution_panel.size_hint_y = 0
        
        # Detener actualización periódica
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None
            
        # Limpiar logs
        self.log_layout.clear_widgets()
    
    def reset_execution_display(self):
        """Reinicia los elementos de visualización de ejecución"""
        self.progress_bar.value = 0
        self.progress_text.text = "0%"
        self.elapsed_label.text = "00:00"
        self.remaining_label.text = "--:--"
        self.step_label.text = "--"
        self.pressure_label.text = "0.0 bar"
        self.log_layout.clear_widgets()
    
    def start_execution(self, instance):
        """Inicia la ejecución del programa"""
        app = App.get_running_app()
        if not app or not hasattr(app, 'program_execution_service'):
            self.show_message("service_not_available", True)
            return
            
        # Verificar si el programa está pausado para reanudar
        if app.program_execution_service.status.value == "paused":
            success, message = app.program_execution_service.resume_execution()
            if success:
                self.pause_button.text = get_translation("pause_execution", "Pause")
                self.start_button.disabled = True
                self.pause_button.disabled = False
                self.stop_button.disabled = False
                self.show_message(message, False)
            else:
                self.show_message(message, True)
            return
            
        # Iniciar nueva ejecución
        success, message = app.program_execution_service.start_execution(
            completion_callback=self.on_execution_completed,
            error_callback=self.on_execution_error,
            progress_callback=self.on_execution_progress
        )
        
        if success:
            self.start_button.disabled = True
            self.pause_button.disabled = False
            self.stop_button.disabled = False
            self.show_message(message, False)
            
            # Iniciar actualización periódica
            if self.clock_event:
                self.clock_event.cancel()
            self.clock_event = Clock.schedule_interval(self.update_execution_display, 0.5)
        else:
            self.show_message(message, True)
    
    def pause_execution(self, instance):
        """Pausa o reanuda la ejecución del programa"""
        app = App.get_running_app()
        if not app or not hasattr(app, 'program_execution_service'):
            self.show_message("service_not_available", True)
            return
            
        if app.program_execution_service.status.value == "paused":
            # Reanudar
            success, message = app.program_execution_service.resume_execution()
            if success:
                self.pause_button.text = get_translation("pause_execution", "Pause")
                self.show_message(message, False)
            else:
                self.show_message(message, True)
        else:
            # Pausar
            success, message = app.program_execution_service.pause_execution()
            if success:
                self.pause_button.text = get_translation("resume_execution", "Resume")
                self.show_message(message, False)
            else:
                self.show_message(message, True)
    
    def stop_execution(self, instance):
        """Detiene la ejecución del programa"""
        app = App.get_running_app()
        if not app or not hasattr(app, 'program_execution_service'):
            self.show_message("service_not_available", True)
            return
            
        success, message = app.program_execution_service.stop_execution()
        if success:
            self.start_button.disabled = False
            self.pause_button.disabled = True
            self.stop_button.disabled = True
            self.pause_button.text = get_translation("pause_execution", "Pause")
            self.show_message(message, False)
            
            # Detener actualización periódica
            if self.clock_event:
                self.clock_event.cancel()
                self.clock_event = None
        else:
            self.show_message(message, True)
    
    def back_action(self, instance):
        """Vuelve a la pantalla anterior"""
        # Asegurarse de detener cualquier ejecución
        app = App.get_running_app()
        if app and hasattr(app, 'program_execution_service'):
            app.program_execution_service.stop_execution()
            
        # Detener el reloj de actualización
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None
            
        # Volver al dashboard
        role = 'user'
        if app and app.current_user:
            role = app.current_user.role
            
        if role == 'admin':
            self.manager.current = 'admin_dashboard'
        else:
            self.manager.current = 'user_dashboard'
    
    def on_execution_completed(self):
        """Callback cuando la ejecución se completa"""
        self.show_message("execution_completed", False)
        
        # Restablecer botones
        self.start_button.disabled = False
        self.pause_button.disabled = True
        self.stop_button.disabled = True
        
        # Detener actualización periódica
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None
            
        # Actualizar una última vez
        Clock.schedule_once(self.update_execution_display, 0.1)
    
    def on_execution_error(self, error_message):
        """Callback cuando hay un error en la ejecución"""
        self.show_message(error_message, True)
        
        # Restablecer botones
        self.start_button.disabled = False
        self.pause_button.disabled = True
        self.stop_button.disabled = True
        
        # Detener actualización periódica
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None
    
    def on_execution_progress(self, event_type, step_info, *args):
        """Callback para actualizar el progreso de ejecución"""
        if event_type == "step_started" or event_type == "step_completed":
            self.add_log_entry(f"Paso {step_info['step_number']}: {step_info['pressure']} bar, {step_info['duration']} seg")
    
    def update_execution_display(self, dt=None):
        """Actualiza la información mostrada periódicamente"""
        app = App.get_running_app()
        if not app or not hasattr(app, 'program_execution_service'):
            return
            
        # Actualizar progreso
        progress, elapsed_seconds, remaining_seconds = app.program_execution_service.get_execution_progress()
        
        # Formatear tiempo transcurrido (MM:SS o HH:MM:SS)
        if elapsed_seconds < 3600:
            elapsed_formatted = f"{int(elapsed_seconds / 60):02d}:{int(elapsed_seconds % 60):02d}"
        else:
            hours = int(elapsed_seconds / 3600)
            minutes = int((elapsed_seconds % 3600) / 60)
            seconds = int(elapsed_seconds % 60)
            elapsed_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Formatear tiempo restante
        if remaining_seconds > 0:
            if remaining_seconds < 3600:
                remaining_formatted = f"{int(remaining_seconds / 60):02d}:{int(remaining_seconds % 60):02d}"
            else:
                hours = int(remaining_seconds / 3600)
                minutes = int((remaining_seconds % 3600) / 60)
                seconds = int(remaining_seconds % 60)
                remaining_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            remaining_formatted = "--:--"
        
        # Actualizar UI
        self.progress_bar.value = progress
        self.progress_text.text = f"{int(progress)}%"
        self.elapsed_label.text = elapsed_formatted
        self.remaining_label.text = remaining_formatted
        
        # Actualizar información de paso
        step_info = app.program_execution_service.get_current_execution_step()
        if step_info:
            self.step_label.text = f"{step_info['step_number']}/{len(app.program_execution_service.current_steps)}"
            self.pressure_label.text = f"{step_info['pressure']} bar"
        
        # Actualizar presión del hardware simulado
        if hasattr(app, 'hardware_simulator'):
            current_pressure = app.hardware_simulator.get_current_pressure()
            self.pressure_label.text = f"{current_pressure:.1f} bar"
    
    def add_log_entry(self, message):
        """Añade una entrada al registro de ejecución"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        entry_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(20)
        )
        
        time_label = Label(
            text=timestamp,
            size_hint_x=0.2,
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1)
        )
        
        message_label = Label(
            text=message,
            size_hint_x=0.8,
            font_size='12sp',
            halign='left'
        )
        message_label.bind(size=message_label.setter('text_size'))
        
        entry_layout.add_widget(time_label)
        entry_layout.add_widget(message_label)
        
        self.log_layout.add_widget(entry_layout)
        
        # Desplazarse hasta el final
        Clock.schedule_once(lambda dt: setattr(self.log_scroll, 'scroll_y', 0), 0.1)
    
    def show_message(self, message, is_error=True):
        """Muestra un mensaje de estado"""
        if self.status_label:
            self.status_label.text = get_translation(message, message)
            if is_error:
                self.status_label.color = (1, 0, 0, 1)  # Rojo para errores
            else:
                self.status_label.color = (0, 0, 1, 1)  # Azul para éxito