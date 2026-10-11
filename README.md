# Gestor de Tareas interactivo con Interfaz Gráfica

Una aplicación de escritorio desarrollada en **Python** utilizando **Tkinter** para la gestión visual de tareas pendientes. El sistema integra un motor de notificaciones en segundo plano, alertas de audio a través de **Pygame** y un sistema de hilos (*threading*) para evitar que la interfaz gráfica se congele al procesar eventos.

---

## 🔥 Características principales

- **Interfaz Limpia y Moderna:** Ventana no redimensionable construida con `tkinter.ttk` que incluye un componente `Treeview` optimizado para listar horas, tareas y estados.
- **Notificaciones Dinámicas:** Alertas visuales en pantalla acompañadas de reproducción de audio automatizada.
- **Arquitectura Multihilo (*Multithreading*):** Uso de `threading.Thread` y colas seguras (`queue.Queue`) para gestionar la síntesis de voz (*text-to-speech*) y alertas en segundo plano.
- **Persistencia de Datos:** Carga automática de configuraciones y textos personalizados desde archivos externos (`json` y `txt`).
- **Listo para Compilar:** Configurado con compatibilidad nativa (`sys._MEIPASS`) para compilarse fácilmente a un ejecutable (`.exe`) usando **PyInstaller**.

---

## 🛠️ Requisitos del sistema

Para ejecutar este proyecto de forma local, necesitas tener instalado **Python 3.x** y la siguiente biblioteca de terceros:

- **Pygame** (utilizado para el sistema de sonido y alertas)

Puedes instalar la dependencia ejecutando:
```bash
pip install pygame
```

---

## 📁 Estructura del repositorio

Para que el script se ejecute correctamente, asegúrate de mantener los siguientes recursos en la raíz de tu directorio (o configurar el empaquetador para incluirlos):

```text
├── app.py             # Código fuente principal de la aplicación
├── audio.wav          # Sonido de alerta para las notificaciones
├── icono.ico          # Icono personalizado de la barra de título
├── mensajes.json      # Base de datos de mensajes dinámicos en formato JSON
└── tareas.txt         # Registro de texto con las tareas programadas
```

---

## 🚀 Instrucciones de ejecución

1. Clona este repositorio en tu máquina local:
   ```bash
   git clone https://github.com
   ```
2. Asegúrate de colocar tus archivos de recursos (`audio.wav`, `icono.ico`, `mensajes.json`) en la misma carpeta.
3. Inicia la aplicación:
   ```bash
   python app.py
   ```

---

## ⚙️ Detalles técnicos del código

La clase principal `app` inicializa los siguientes componentes críticos:
- `pygame.mixer.Sound`: Controla y reproduce el sonido de alerta de forma asíncrona.
- `queue.Queue()` y `threading.Event()`: Coordinan los estados y la transferencia segura de datos entre el hilo principal de la interfaz visual (GUI) y los procesos de notificación en segundo plano.
- `tkinter.StringVar()`: Enlaza dinámicamente el texto de la "Próxima tarea" directamente en la pantalla del usuario en tiempo real.

---

## ✒️ Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para obtener más detalles.
