# Chat Local con IA Gemini (Gepeto)

Este proyecto implementa una aplicación web de chat simple que te permite interactuar con la API de Gemini de Google de forma local. Las preguntas se realizan a través de una interfaz web y las respuestas de la IA se muestran en la misma página.

## Características

*   Interfaz de chat web minimalista y responsiva.
*   Comunicación con la API de Gemini para generación de respuestas.
*   Backend desarrollado en Python con Flask.
*   Frontend construido con HTML, CSS y JavaScript puro.
*   Gestión segura de la API Key mediante variables de entorno.
*   Posibilidad de crear un ejecutable para facilitar su uso (ver sección "Crear Ejecutable").


## Requisitos Previos

*   Python 3.7+ (se recomienda 3.9+ para compatibilidad con todas las dependencias)
*   Una API Key de Google Gemini (Puedes obtenerla desde [Google AI Studio](https://aistudio.google.com/))
*   Git (para clonar el repositorio)

## Configuración del Proyecto para Desarrollo

Sigue estos pasos si vas a ejecutar la aplicación directamente con `python app.py`.

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/MRDaniel04/LocalAI.git
    cd LocalAI 
    ```
    *(Nota: Asumo que el nombre de la carpeta raíz del proyecto es `LocalAI` según tu URL de GitHub. Si la carpeta interna principal se llama `gemini_local_chat`, ajusta el `cd`)*

4.  **Configura tu API Key para desarrollo:**
    *   En la **raíz del proyecto** (ej. `LocalAI/`), crea un archivo llamado `.env`.
    *   Añade tu API Key de Gemini al archivo `.env` de la siguiente manera:
        ```env
        GEMINI_API_KEY="TU_API_KEY_AQUI"
        ```

## Uso (Modo Desarrollo)

1.  **Ejecuta la aplicación Flask:**
    ```bash
    python app.py
    ```

2.  **Abre tu navegador web y ve a:**
    `http://127.0.0.1:5000/`
    (O `http://TU_IP_LOCAL:5000/` si quieres acceder desde otro dispositivo en tu red local).

3.  ¡Comienza a chatear con la IA!

## Pasos para ejecutar

1.  **Configura tu API Key para el Ejecutable:**
    *   **¡MUY IMPORTANTE!** Para que el ejecutable funcione, necesita su propio archivo `.env`.
    *   Copia el archivo `.env` que creaste en la raíz del proyecto (o crea uno nuevo con el mismo contenido: `GEMINI_API_KEY="TU_API_KEY_AQUI"`).
    *   Pega este archivo `.env` **en la misma carpeta donde se encuentra el archivo ejecutable** (ej. dentro de `dist/Gepeto/` si es una carpeta, o junto a `dist/Gepeto.exe` si es un solo archivo).

2.  **Ejecuta la aplicación:**
    Haz doble clic en el archivo ejecutable (ej. `Gepeto.exe`). La aplicación debería iniciarse y abrir tu navegador web predeterminado.

**Resumen de la Ubicación de el archivo `.env`:**

*   **Para el ejecutable:** El archivo `.env` debe estar **junto al archivo `.exe`** (ej. `LocalAI/dist/Gepeto/.env`).

## Estructura del Proyecto

LocalAI/
├── app.py # Script principal de Flask (backend)
├── .env # Archivo para API Key en DESARROLLO (¡IGNORADO POR GIT!)
├── ChatApp.spec # Archivo de configuración para PyInstaller (ejemplo)
├── .gitignore # Especifica archivos y directorios ignorados por Git
├── requirements.txt # Dependencias de Python
├── README.md # Este archivo
├── templates/ # Plantillas HTML
│ └── index.html # Página principal del chat
└── static/ # Archivos estáticos
├── css/
│ └── style.css # Estilos CSS
└── js/
└── script.js # Lógica JavaScript del frontend
dist/ # Carpeta creada por PyInstaller (después de construir)
└── Gepeto/ # Nombre de tu aplicación
├── Gepeto.exe # El ejecutable
└── .env # Archivo para API Key del EJECUTABLE
└── (otros archivos...)

## Tecnologías Utilizadas

*   **Backend:** Python, Flask, `google-generativeai`, `python-dotenv`, `markdown`
*   **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
*   **API:** Google Gemini API
*   **Empaquetado:** PyInstaller (opcional)

## Posibles Mejoras Futuras
*   [ ] Mejorar el manejo de errores y feedback al usuario en la interfaz.
*   [ ] Implementar persistencia del historial de chat.
*   [ ] Permitir configurar parámetros del modelo Gemini desde la interfaz.
*   [ ] Añadir soporte para streaming de respuestas.

## Contribuciones
Las contribuciones son bienvenidas. Por favor, abre un *issue* para discutir cambios importantes o envía un *pull request*.
