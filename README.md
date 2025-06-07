# Chat Local con IA Gemini

Este proyecto implementa una aplicación web de chat simple que te permite interactuar con la API de Gemini de Google de forma local. Las preguntas se realizan a través de una interfaz web y las respuestas de la IA se muestran en la misma página.

## Características

*   Interfaz de chat web minimalista y responsiva.
*   Comunicación con la API de Gemini para generación de respuestas.
*   Backend desarrollado en Python con Flask.
*   Frontend construido con HTML, CSS y JavaScript puro.
*   Gestión segura de la API Key mediante variables de entorno.


## Requisitos Previos

*   Python 3.7+
*   Una API Key de Google Gemini (Puedes obtenerla desde [Google AI Studio](https://aistudio.google.com/))
*   Git (opcional, para clonar el repositorio)

## Configuración del Proyecto

1.  **Clona el repositorio (o descarga los archivos):**
    ```bash
    git clone https://URL_DE_TU_REPOSITORIO_GIT.git
    cd gemini_local_chat
    ```
    (Reemplaza `URL_DE_TU_REPOSITORIO_GIT.git` con la URL real si lo subes a GitHub/GitLab, etc. Si no, simplemente navega a la carpeta del proyecto).

2.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configura tu API Key:**
    *   Crea un archivo llamado `.env` en la raíz del proyecto.
    *   Añade tu API Key de Gemini al archivo `.env` de la siguiente manera:
        ```env
        GEMINI_API_KEY="TU_API_KEY_AQUI"
        ```
    *   **Importante:** El archivo `.env` está incluido en `.gitignore` y no debe ser subido al repositorio.

## Uso

1.  **Asegúrate de que tu entorno virtual esté activado.**

2.  **Ejecuta la aplicación Flask:**
    ```bash
    python app.py
    ```

3.  **Abre tu navegador web y ve a:**
    `http://127.0.0.1:5000/`
    (O `http://TU_IP_LOCAL:5000/` si quieres acceder desde otro dispositivo en tu red local, ya que `app.py` está configurado con `host='0.0.0.0'`).

4.  ¡Comienza a chatear con la IA! Escribe tu pregunta en el cuadro de texto y presiona "Enviar" o la tecla Enter.
