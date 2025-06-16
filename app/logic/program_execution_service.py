import time
from threading import Thread, Event
import datetime
from enum import Enum

class ProgramExecutionStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    ABORTED = "aborted"

class ProgramExecutionService:
    def __init__(self, program_service, hardware_controller=None):
        self.program_service = program_service
        self.hardware_controller = hardware_controller  # Controlador de hardware
        self.current_program = None
        self.current_steps = []
        self.current_step_index = -1
        self.status = ProgramExecutionStatus.IDLE
        self.execution_thread = None
        self.stop_event = Event()
        self.pause_event = Event()
        self.execution_log = []
        self.execution_start_time = None
        self.current_step_start_time = None
        self.completion_callback = None
        self.error_callback = None
        self.progress_callback = None

    def load_program(self, program_id):
        """Carga un programa para su ejecución"""
        program, steps = self.program_service.get_program_by_id(program_id)
        if not program or not steps:
            return False, "program_not_found"
            
        self.current_program = program
        self.current_steps = steps
        self.current_step_index = -1
        self.status = ProgramExecutionStatus.IDLE
        self.execution_log = []
        return True, "program_loaded"

    def start_execution(self, completion_callback=None, error_callback=None, progress_callback=None):
        """Inicia la ejecución del programa cargado"""
        if self.status == ProgramExecutionStatus.RUNNING:
            return False, "program_already_running"
            
        if not self.current_program or not self.current_steps:
            return False, "no_program_loaded"
            
        # Reiniciar si el programa ya se completó o tuvo error
        if self.status in [ProgramExecutionStatus.COMPLETED, ProgramExecutionStatus.ERROR, ProgramExecutionStatus.ABORTED]:
            self.current_step_index = -1
            self.execution_log = []
            
        # Configurar callbacks
        self.completion_callback = completion_callback
        self.error_callback = error_callback
        self.progress_callback = progress_callback
            
        # Configurar eventos de control
        self.stop_event.clear()
        self.pause_event.clear()
        
        # Registrar tiempo de inicio
        self.execution_start_time = datetime.datetime.now()
        
        # Iniciar thread de ejecución
        self.status = ProgramExecutionStatus.RUNNING
        self.execution_thread = Thread(target=self._execution_thread_function)
        self.execution_thread.daemon = True
        self.execution_thread.start()
        
        return True, "execution_started"

    def pause_execution(self):
        """Pausa la ejecución del programa"""
        if self.status != ProgramExecutionStatus.RUNNING:
            return False, "program_not_running"
            
        self.pause_event.set()
        self.status = ProgramExecutionStatus.PAUSED
        self._log_event("Ejecución pausada")
        return True, "execution_paused"

    def resume_execution(self):
        """Reanuda la ejecución pausada"""
        if self.status != ProgramExecutionStatus.PAUSED:
            return False, "program_not_paused"
            
        self.pause_event.clear()
        self.status = ProgramExecutionStatus.RUNNING
        self._log_event("Ejecución reanudada")
        return True, "execution_resumed"

    def stop_execution(self):
        """Detiene la ejecución del programa"""
        if self.status not in [ProgramExecutionStatus.RUNNING, ProgramExecutionStatus.PAUSED]:
            return False, "program_not_running"
            
        self.stop_event.set()
        self.pause_event.clear()  # En caso de estar pausado
        
        # Esperar a que el hilo termine
        if self.execution_thread and self.execution_thread.is_alive():
            self.execution_thread.join(timeout=2.0)
            
        self.status = ProgramExecutionStatus.ABORTED
        self._log_event("Ejecución abortada por usuario")
        return True, "execution_stopped"

    def get_execution_progress(self):
        """Obtiene el progreso de ejecución actual"""
        if not self.current_steps:
            return 0, 0, 0
            
        total_steps = len(self.current_steps)
        current_step = self.current_step_index + 1  # +1 para mostrar desde 1 en vez de 0
        
        # Calcular tiempo restante estimado
        elapsed_seconds = 0
        remaining_seconds = 0
        
        if self.execution_start_time:
            elapsed_time = datetime.datetime.now() - self.execution_start_time
            elapsed_seconds = elapsed_time.total_seconds()
            
            if self.current_step_index >= 0 and self.status == ProgramExecutionStatus.RUNNING:
                # Calcular tiempo restante para el paso actual
                current_step_obj = self.current_steps[self.current_step_index]
                step_elapsed = 0
                
                if self.current_step_start_time:
                    step_elapsed = (datetime.datetime.now() - self.current_step_start_time).total_seconds()
                    
                step_remaining = max(0, current_step_obj.duration - step_elapsed)
                
                # Sumar el tiempo restante de pasos futuros
                future_steps_time = sum(step.duration for step in self.current_steps[self.current_step_index+1:])
                
                remaining_seconds = step_remaining + future_steps_time
        
        # Calcular porcentaje
        percentage = 0
        if total_steps > 0:
            if self.status == ProgramExecutionStatus.COMPLETED:
                percentage = 100
            elif self.current_step_index >= 0:
                # Calcular el porcentaje incluyendo el progreso dentro del paso actual
                steps_percentage = (self.current_step_index / total_steps) * 100
                
                if self.status == ProgramExecutionStatus.RUNNING and self.current_step_start_time:
                    current_step_obj = self.current_steps[self.current_step_index]
                    step_elapsed = (datetime.datetime.now() - self.current_step_start_time).total_seconds()
                    step_percentage = min(1.0, step_elapsed / max(1, current_step_obj.duration))
                    step_contribution = (step_percentage / total_steps) * 100
                    percentage = steps_percentage + step_contribution
                else:
                    percentage = steps_percentage
        
        return percentage, elapsed_seconds, remaining_seconds

    def get_current_execution_step(self):
        """Obtiene información sobre el paso actual en ejecución"""
        if self.current_step_index < 0 or self.current_step_index >= len(self.current_steps):
            return None
            
        step = self.current_steps[self.current_step_index]
        
        # Calcular tiempo transcurrido en este paso
        step_elapsed = 0
        if self.current_step_start_time:
            step_elapsed = (datetime.datetime.now() - self.current_step_start_time).total_seconds()
            
        return {
            'step_number': step.step_number,
            'pressure': step.pressure,
            'duration': step.duration,
            'elapsed': step_elapsed,
            'remaining': max(0, step.duration - step_elapsed)
        }

    def get_execution_log(self):
        """Obtiene el registro de ejecución"""
        return self.execution_log

    def _execution_thread_function(self):
        """Función principal del hilo de ejecución"""
        try:
            self._log_event(f"Iniciando ejecución del programa: {self.current_program.name}")
            
            # Iniciar desde el principio o continuar desde donde se quedó en caso de pausa
            start_index = 0 if self.current_step_index < 0 else self.current_step_index
            
            for i in range(start_index, len(self.current_steps)):
                # Verificar si se solicitó detener
                if self.stop_event.is_set():
                    return
                    
                self.current_step_index = i
                current_step = self.current_steps[i]
                
                self._log_event(f"Ejecutando paso {current_step.step_number}: {current_step.pressure} bar durante {current_step.duration} segundos")
                self.current_step_start_time = datetime.datetime.now()
                
                # Notificar inicio de paso si hay callback
                if self.progress_callback:
                    step_info = self.get_current_execution_step()
                    self.progress_callback("step_started", step_info)
                
                # Simular o ejecutar el control de hardware
                if self.hardware_controller:
                    try:
                        self.hardware_controller.set_pressure(current_step.pressure)
                    except Exception as e:
                        self._log_event(f"Error en hardware: {e}")
                        self._handle_error(f"hardware_error: {e}")
                        return
                
                # Esperar el tiempo de duración del paso
                step_end_time = self.current_step_start_time + datetime.timedelta(seconds=current_step.duration)
                
                while datetime.datetime.now() < step_end_time:
                    # Verificar si se solicitó detener
                    if self.stop_event.is_set():
                        return
                        
                    # Manejar pausa
                    if self.pause_event.is_set():
                        # Ajustar el tiempo final para compensar el tiempo de pausa
                        pause_start = datetime.datetime.now()
                        self._log_event(f"Paso {current_step.step_number} pausado")
                        
                        # Esperar hasta que se quite la pausa
                        while self.pause_event.is_set() and not self.stop_event.is_set():
                            time.sleep(0.1)
                            
                        if self.stop_event.is_set():
                            return
                            
                        # Calcular cuánto tiempo estuvo pausado y ajustar
                        pause_duration = datetime.datetime.now() - pause_start
                        step_end_time += pause_duration
                        self._log_event(f"Paso {current_step.step_number} reanudado después de {pause_duration.total_seconds():.1f} segundos")
                    
                    # Actualizar progreso cada 5 iteraciones
                    if self.progress_callback and i % 5 == 0:
                        step_info = self.get_current_execution_step()
                        progress, elapsed, remaining = self.get_execution_progress()
                        self.progress_callback("step_progress", step_info, progress, elapsed, remaining)
                        
                    time.sleep(0.1)
                
                self._log_event(f"Completado paso {current_step.step_number}")
                
                # Notificar fin de paso si hay callback
                if self.progress_callback:
                    step_info = self.get_current_execution_step()
                    self.progress_callback("step_completed", step_info)
            
            # Programa completado exitosamente
            self.status = ProgramExecutionStatus.COMPLETED
            self._log_event(f"Programa completado: {self.current_program.name}")
            
            # Llamar al callback de completado si existe
            if self.completion_callback:
                self.completion_callback()
                
        except Exception as e:
            self._handle_error(f"execution_error: {e}")
    
    def _handle_error(self, error_message):
        """Maneja errores durante la ejecución"""
        self.status = ProgramExecutionStatus.ERROR
        self._log_event(f"ERROR: {error_message}")
        
        # Detener hardware si está disponible
        if self.hardware_controller:
            try:
                self.hardware_controller.emergency_stop()
            except:
                pass
                
        # Llamar al callback de error si existe
        if self.error_callback:
            self.error_callback(error_message)
    
    def _log_event(self, message):
        """Registra un evento en el log de ejecución"""
        timestamp = datetime.datetime.now()
        log_entry = {
            'timestamp': timestamp,
            'message': message
        }
        self.execution_log.append(log_entry)
        print(f"[{timestamp.strftime('%H:%M:%S')}] {message}")