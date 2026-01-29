# Sistema de Baterías de Cuestionarios de Riesgo Psicosocial

Este sistema es una aplicación web diseñada para la aplicación, gestión y recolección de datos de las Baterías de Riesgo Psicosocial. Permite a los usuarios completar una serie de cuestionarios secuenciales, guardando su progreso y adaptando el flujo de preguntas según su perfil laboral.

## 🚀 Características Principales

*   **Flujo Secuencial Inteligente**: Guía al usuario a través de los cuestionarios en un orden predefinido (Datos Generales -> Estrés -> Extralaborales -> Intralaborales).
*   **Enrutamiento Condicional**: Determina automáticamente si el usuario debe responder la Forma A o la Forma B del cuestionario Intralaboral basándose en si tiene personas a cargo.
*   **Persistencia de Sesión**: Los usuarios pueden cerrar el navegador y retomar su encuesta ingresando su número de cédula.
*   **Almacenamiento Local**: Todos los datos se guardan en archivos JSON estructurados en el servidor, facilitando la exportación y backup sin necesidad de bases de datos complejas.
*   **Diseño Responsivo**: Interfaz moderna y amigable, optimizada para escritorio y dispositivos móviles.

## 🛠️ Arquitectura del Sistema

*   **Backend**: Python con FastAPI. Maneja la lógica de negocio, validación de datos, gestión de sesiones y servicio de archivos estáticos.
*   **Frontend**: HTML5, CSS3 y JavaScript (Vanilla). Se comunica con el backend mediante API REST.
*   **Base de Datos**: Sistema de archivos JSON (Flat-file database) ubicado en `backend/data/`.
*   **Puerto**: El sistema se ejecuta por defecto en el puerto **8000**.

## 📂 Estructura del Proyecto

```
/
├── backend/
│   ├── app.py                 # Aplicación principal FastAPI
│   ├── cleanup.py             # Script de limpieza y reseteo del sistema
│   ├── requirements.txt       # Dependencias de Python
│   ├── questionnaires/        # Definiciones de los cuestionarios (JSON)
│   └── data/                  # [GENERADO] Almacena respuestas y sesiones
└── frontend/
    ├── index.html             # Página de inicio
    ├── ficha-datos.html       # Formulario inicial de datos
    ├── encuesta.html          # Motor de renderizado de cuestionarios
    └── ...
```

## 🔧 Gestión del Despliegue (Servidor)

El sistema está configurado para ejecutarse como un servicio del sistema (systemd) en Linux, lo que garantiza que se inicie automáticamente y se mantenga en ejecución.

### Comandos de Control del Servicio

El nombre del servicio es `cuestionarios`.

*   **Verificar estado del servicio**:
    ```bash
    sudo systemctl status cuestionarios
    ```
    *Busca "Active: active (running)" para confirmar que está funcionando.*

*   **Reiniciar el servicio** (necesario después de cambios en el código):
    ```bash
    sudo systemctl restart cuestionarios
    ```

*   **Detener el servicio**:
    ```bash
    sudo systemctl stop cuestionarios
    ```

*   **Ver logs en tiempo real** (para depuración):
    ```bash
    sudo journalctl -u cuestionarios -f
    ```

### Puerto y Acceso

La aplicación escucha en el puerto **8000**. El servidor debe tener este puerto abierto o configurado a través de un proxy inverso (como Nginx) si se desea acceder por el puerto 80 estándar.

## 🧹 Mantenimiento y Limpieza

Para limpiar completamente el sistema (borrar respuestas de prueba y reiniciar sesiones) antes de una nueva campaña de recolección o entrega, se incluye un script de utilidad.

1.  Navegue a la carpeta raíz del proyecto.
2.  Ejecute el script de limpieza con Python:
    ```bash
    python backend/cleanup.py
    ```
3.  Escriba `DELETE` cuando el sistema lo solicite para confirmar.

**⚠️ ADVERTENCIA**: Esto eliminará PERMANENTEMENTE todos los archivos en `backend/data/` (respuestas y sesiones).

## 💻 Desarrollo Local

Para correr el proyecto en su máquina local:

1.  Instalar dependencias:
    ```bash
    pip install -r backend/requirements.txt
    ```
2.  Iniciar el servidor:
    ```bash
    python backend/app.py
    ```
3.  Acceder en el navegador: `http://localhost:8000`

---
*Desarrollado para la gestión eficiente de evaluaciones psicosociales.*
