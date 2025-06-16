# Proyecto: Sistema de Control Electrónico en Raspberry Pi

**Fecha y Hora de este Estado:** 2025-06-15 20:35:49 UTC
**Último Usuario en Interacción:** totama76

## Funcionalidades Operativas:

1.  **Estructura del Proyecto:**
    *   Arquitectura de 3 capas (Presentación, Lógica, Acceso a Datos) parcialmente implementada.
    *   Organización en directorios para cada capa y componentes.

2.  **Configuración Centralizada:**
    *   Archivo `config.ini` para gestionar:
        *   Idioma por defecto y ruta del logotipo.
        *   Nombre de la base de datos y credenciales del administrador por defecto.
        *   Unidades de medida (presión, tiempo).
        *   Valores por defecto para la creación de "programas".
        *   Colores para las alarmas visuales.
        *   Parámetros estéticos básicos.

3.  **Internacionalización (i18n):**
    *   Soporte para Inglés (en), Español (es) y Francés (fr).
    *   Archivos de traducción en formato JSON (`locales/*.json`).
    *   Módulo `Translator` (`app/i18n/translations.py`) para cargar y gestionar las traducciones.

4.  **Modelos de Datos:**
    *   Clases `User` y `Program` definidas en `app/data_access/models.py`.

5.  **Acceso a Datos (`DatabaseManager`):**
    *   Gestor para la base de datos SQLite (`app/data_access/database_manager.py`).
    *   Creación automática de tablas (`users`, `programs`).
    *   Funciones CRUD para usuarios (hashing de contraseñas simple - **mejora pendiente**).
    *   Funciones CRUD para programas.
    *   Creación automática de un usuario administrador por defecto.

6.  **Lógica de Negocio:**
    *   **Servicio de Usuario (`UserService`):** Registro, login, gestión básica de perfiles.
    *   **Servicio de Programa (`ProgramService`):** CRUD de programas, uso de valores por defecto.

7.  **Interfaz de Usuario (UI) - Kivy:**
    *   **Pantalla de Login (`LoginScreen`):**
        *   Implementada en `app/presentation/ui_manager.py` y `app/presentation/electronic_control.kv`.
        *   Campos de usuario/contraseña, botón de login, etiqueta de estado.
        *   Funcionalidad de login interactúa con `UserService`.
        *   Selector de Idioma funcional.
    *   **Pantallas de Dashboard (`AdminDashboardScreen`, `UserDashboardScreen`):**
        *   Implementadas como clases en `ui_manager.py` y definidas en `electronic_control.kv`.
        *   Heredan de una `BaseDashboardScreen` para compartir estructura y botón de logout.
        *   Muestran un mensaje de bienvenida personalizado.
        *   Botón de "Logout" funcional que devuelve al usuario a la pantalla de Login.
    *   **Navegación entre Pantallas:**
        *   Implementada la navegación desde `LoginScreen` a `AdminDashboardScreen` o `UserDashboardScreen` según el rol del usuario.
        *   Implementada la navegación desde los Dashboards de vuelta a `LoginScreen` mediante el botón "Logout".
    *   **Aplicación Kivy Principal (`ElectronicControlApp`):** Carga la UI, gestiona servicios, el usuario actual y la lógica de logout.

8.  **Flujo Principal de la Aplicación (`main.py`, `app/main_app.py`):** Inicializa y lanza la aplicación Kivy.

## Nuevas Funcionalidades y Correcciones Desde el Último Estado:

*   Creación de las clases `AdminDashboardScreen` y `UserDashboardScreen` en `ui_manager.py`.
*   Definición de una `BaseDashboardScreen` en `ui_manager.py` (y su correspondiente regla KV `<BaseDashboardScreen@Screen>`) para compartir la estructura y el botón de logout entre los dashboards.
*   Adición de las nuevas pantallas al `ScreenManager` en `electronic_control.kv`.
*   Implementación de la lógica de navegación en `LoginScreen.login()` para dirigir al usuario al dashboard apropiado.
*   Implementación de un método `logout()` en `ElectronicControlApp` y su vinculación al botón "Logout" en los dashboards.
*   Actualización de los archivos de traducción JSON con nuevas claves para "logout_button", "admin_dashboard", y "user_dashboard".
*   Mensaje de bienvenida personalizado en los dashboards que incluye el nombre de usuario.

## Requisitos Aplicados (Basado en "Biblia del Proyecto - Revisión 4"):

*   **1. Arquitectura y Tecnología:** Python, 3 capas (parcial), SQLite, Raspberry Pi (objetivo), Windows (desarrollo) - En progreso.
*   **2. Configuración:** `config.ini`, i18n, logo (parcial) - En progreso.
*   **3. UI/UX:** Pantalla táctil (Kivy), Login Screen, Selector Idioma, **Dashboards básicos (Admin/User), Navegación básica, Logout** - Implementado. *Pendiente:* Funcionalidad específica en dashboards, visualización datos, control ejecución.
*   **4. Seguridad:** Autenticación (backend y UI login implementado). Roles definidos y utilizados para navegación básica. *Pendiente:* UI por roles más detallada.
*   **5. Gestión de "Programas":** CRUD backend, parámetros, defaults. *Pendiente:* UI para CRUD programas.
*   **6. Ejecución de "Programas":** (Pendiente).

Este `README.md` refleja el estado actual del proyecto.