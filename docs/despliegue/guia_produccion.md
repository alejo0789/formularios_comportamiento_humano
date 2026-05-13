# Guía de Despliegue en Windows Server

Sigue estos pasos para desplegar el Sistema de Cuestionarios en un entorno de Windows Server.

## 1. Requisitos del Sistema
- **Python 3.10+**: Descargar e instalar desde python.org. Asegúrate de marcar "Add Python to PATH".
- **Git**: Para clonar el repositorio (opcional).
- **Permisos de Administrador**: Necesarios para instalar servicios y configurar el servidor web.

## 2. Preparación del Proyecto
Crea una carpeta para el proyecto (ej: `C:\inetpub\wwwroot\formularios`) y copia los archivos allí.

## 3. Entorno Virtual y Dependencias (PowerShell)
Abre PowerShell como administrador y ejecuta:

```powershell
# Ir a la carpeta del proyecto
cd C:\inetpub\wwwroot\formularios

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Actualizar pip e instalar dependencias
python -m pip install --upgrade pip
pip install -r backend/requirements.txt

# Instalar Chromium para reportes PDF
playwright install chromium
```

## 4. Configuración del Entorno (.env)
Crea el archivo de configuración para el backend:

```powershell
copy backend\.env.example backend\.env
```
Edita `backend\.env` con el Bloc de notas o VS Code para ajustar los puertos y rutas.

## 5. Ejecutar como Servicio (NSSM)
Para que la aplicación corra en segundo plano y se inicie con el servidor, recomendamos usar **NSSM** (Non-Sucking Service Manager).

1. Descarga NSSM desde [nssm.cc](https://nssm.cc/download).
2. Abre una terminal de administrador y ejecuta:
   ```powershell
   .\nssm.exe install CuestionariosService
   ```
3. En la ventana que aparece, configura:
   - **Path**: `C:\inetpub\wwwroot\formularios\venv\Scripts\uvicorn.exe`
   - **Startup directory**: `C:\inetpub\wwwroot\formularios`
   - **Arguments**: `backend.app:app --host 0.0.0.0 --port 8034 --root-path /cuestionarios`
4. Haz clic en "Install service".
5. Inicia el servicio:
   ```powershell
   Start-Service CuestionariosService
   ```

## 6. Configuración del Servidor Web (IIS o Apache)

### Opción A: IIS (Recomendado en Windows)
1. Instala el módulo **Application Request Routing (ARR)** y **URL Rewrite**.
2. Configura un "Reverse Proxy" para que las peticiones a `http://tuservidor/cuestionarios` se redirijan a `http://localhost:8034/cuestionarios`.

### Opción B: Apache para Windows
Si usas el Apache incluido en XAMPP o similar, añade esto a `httpd.conf`:
```apache
<Location /cuestionarios>
    ProxyPass http://127.0.0.1:8034/cuestionarios
    ProxyPassReverse http://127.0.0.1:8034/cuestionarios
</Location>
```

---
## Comandos de Mantenimiento
- **Reiniciar servicio:** `Restart-Service CuestionariosService`
- **Verificar estado:** `Get-Service CuestionariosService`
- **Logs:** Revisa la pestaña "I/O" en NSSM para redirigir la salida a un archivo `.txt`.
