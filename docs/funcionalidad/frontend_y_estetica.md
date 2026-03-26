# Arquitectura del Frontend y Estética

El frontend del proyecto de Análisis Psicosocial está diseñado para ser una aplicación web progresiva (PWA) de alta interactividad, optimizada para la recopilación de datos de los trabajadores.

## 1. Interfaz de Usuario Conversacional

El sistema utiliza una interfaz de tipo **Chat Conversacional**, permitiendo que el trabajador complete los cuestionarios de manera fluida y amigable.

### Características del Chat
- **Avatar Dinámico:** Representación visual de un bot para guiar al usuario.
- **Indicador de "Escribiendo":** Simula una conversación real para reducir el abandono.
- **Micro-animaciones:** Transiciones suaves entre preguntas y respuestas.
- **Opciones Interactivas:** Botones accionables con emojis que facilitan la selección rápida de respuestas (Siempre, Casi siempre, etc.).

## 2. Componentes Principales

La aplicación se organiza en una arquitectura modular de archivos HTML y CSS:

- **index.html:** El portal de acceso y dashboard de selección de cuestionarios.
- **app.js:** El motor principal que maneja los flujos de conversación, carga las preguntas desde la API y envía las respuestas.
- **reportes_modulares/:** Una carpeta dedicada a la construcción de los reportes PDF. Cada sección (`01_portada.html`, `04_perfil_poblacion.html`, etc.) es una plantilla independiente.
- **styles.css:** Contiene el diseño visual, utilizando variables CSS para una fácil personalización temática.

---

## 3. Guía Estética y Diseño Premium

El diseño sigue principios de **Acertemos Premium UI**, enfocándose en la legibilidad y la profesionalidad.

### Colores de Identidad
- **Azul Primario (#1a237e / #283593):** Usado para encabezados y acciones principales (inspirado en la seriedad del contexto legal).
- **Escala de Riesgo:**
    - `Muy Alto:` Morado (#8e44ad)
    - `Alto:` Rojo (#e74c3c)
    - `Medio:` Naranja (#f39c12)
    - `Bajo / Sin Riesgo:` Verde (#27ae60)

### Tipografía
Se utiliza la tipografía del sistema (Segoe UI, Arial) para garantizar tiempos de carga rápidos y una lectura clara en todos los dispositivos.

## 4. Estado de la Aplicación (`state`)

En `app.js`, el estado se maneja en un objeto central que rastrea:
- `questions`: Lista de preguntas cargadas.
- `currentQuestionIndex`: El progreso del usuario.
- `userResponses`: Mapa de ID de pregunta a valor de respuesta.
- `conversationPhase`: Fase actual (`welcome`, `info`, `questions`, `complete`).

---

## 5. Escalabilidad y Futuras Mejoras
- **Integración con WhatsApp:** El backend ya soporta lógica para recibir identificaciones y emitir links de cuestionarios.
- **Dashboard de Analistas:** Vista consolidada con gráficos dinámicos para la alta gerencia.
