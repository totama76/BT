import random
import time
from threading import Thread, Event

class HardwareSimulator:
    """
    Simulador de hardware para probar la ejecución de programas
    sin necesidad de hardware real.
    """
    def __init__(self):
        self.current_pressure = 0.0
        self.target_pressure = 0.0
        self.is_running = False
        self.control_thread = None
        self.stop_event = Event()
        self.pressure_update_callback = None
        self.error_rate = 0.001  # Probabilidad de error aleatorio (0.1%)

    def start(self, pressure_update_callback=None):
        """Inicia el simulador"""
        if self.is_running:
            return False
            
        self.is_running = True
        self.pressure_update_callback = pressure_update_callback
        self.stop_event.clear()
        
        # Iniciar thread de control
        self.control_thread = Thread(target=self._control_loop)
        self.control_thread.daemon = True
        self.control_thread.start()
        
        return True

    def stop(self):
        """Detiene el simulador"""
        if not self.is_running:
            return False
            
        self.stop_event.set()
        
        # Esperar a que el hilo termine
        if self.control_thread and self.control_thread.is_alive():
            self.control_thread.join(timeout=2.0)
            
        self.is_running = False
        return True

    def set_pressure(self, pressure):
        """Establece la presión objetivo"""
        if pressure < 0:
            raise ValueError("La presión no puede ser negativa")
            
        self.target_pressure = float(pressure)
        return True

    def emergency_stop(self):
        """Detiene de emergencia el sistema"""
        self.target_pressure = 0.0
        print("¡PARADA DE EMERGENCIA ACTIVADA!")
        return True

    def get_current_pressure(self):
        """Obtiene la presión actual"""
        return self.current_pressure

    def _control_loop(self):
        """Bucle principal de control simulado"""
        adjustment_rate = 0.2  # Bar por segundo
        update_interval = 0.1  # Segundos
        
        while not self.stop_event.is_set():
            # Simular cambio gradual de presión
            if self.current_pressure < self.target_pressure:
                self.current_pressure = min(
                    self.target_pressure,
                    self.current_pressure + adjustment_rate * update_interval
                )
            elif self.current_pressure > self.target_pressure:
                self.current_pressure = max(
                    self.target_pressure,
                    self.current_pressure - adjustment_rate * update_interval
                )
                
            # Añadir pequeñas fluctuaciones para simular ruido
            noise = random.uniform(-0.05, 0.05)
            self.current_pressure = max(0, self.current_pressure + noise)
            
            # Simular fallos aleatorios
            if random.random() < self.error_rate:
                error_type = random.choice(["pressure_spike", "connection_lost"])
                
                if error_type == "pressure_spike":
                    # Simular un pico de presión
                    self.current_pressure += random.uniform(1.0, 3.0)
                    print("¡SIMULACIÓN: Error - Pico de presión!")
                    
                elif error_type == "connection_lost":
                    # Simular pérdida de conexión
                    print("¡SIMULACIÓN: Error - Pérdida de conexión con el hardware!")
                    raise ConnectionError("Simulación de pérdida de conexión con el hardware")
            
            # Notificar cambio de presión
            if self.pressure_update_callback:
                self.pressure_update_callback(self.current_pressure)
                
            time.sleep(update_interval)