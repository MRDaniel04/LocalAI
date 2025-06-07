import os
import sys # Necesario para PyInstaller
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import markdown # Para convertir Markdown a HTML si Gemini responde en Markdown
import webbrowser # Para abrir el navegador
from threading import Timer # Para abrir el navegador después de que el servidor inicie

# --- Determinar la ruta base para PyInstaller ---
# Esto es crucial para que PyInstaller encuentre las carpetas static y templates
# cuando se ejecuta desde el archivo empaquetado.
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Si la aplicación está "congelada" (empaquetada por PyInstaller)
    # sys._MEIPASS es la ruta temporal donde PyInstaller extrae los archivos
    base_dir = sys._MEIPASS
else:
    # Si se ejecuta como un script normal de Python
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Actualizar las rutas de las carpetas de plantillas y estáticas
template_folder = os.path.join(base_dir, 'templates')
static_folder = os.path.join(base_dir, 'static')

# Cargar variables de entorno desde .env
# Busca .env junto al script o, si está empaquetado, junto al ejecutable.
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Cuando está empaquetado, el "directorio del ejecutable" es donde está el .exe
    # y __file__ podría no ser lo que esperamos.
    # sys.executable es la ruta al .exe
    dotenv_path = os.path.join(os.path.dirname(sys.executable), '.env')
else:
    # En desarrollo, .env está junto a app.py
    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

# Solo intenta cargar si el archivo .env existe
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
else:
    print(f"ADVERTENCIA: No se encontró el archivo .env en {dotenv_path}. La API Key debe estar configurada de otra manera (ej. variables de entorno del sistema).")


# Inicializar Flask con las rutas correctas para plantillas y estáticos
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

# Configuración de la API Key de Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Variable global para indicar si la configuración inicial fue exitosa
initial_config_ok = True

if not GEMINI_API_KEY:
    print("ERROR CRÍTICO: No se encontró la API Key de Gemini. Asegúrate de que el archivo .env está configurado y contiene GEMINI_API_KEY, o que la variable de entorno está definida en el sistema.")
    initial_config_ok = False
    # No usamos raise ValueError aquí para permitir que la app intente iniciar y mostrar un error más amigable
    # o para que el usuario vea el mensaje en la consola si no es --windowed.

if initial_config_ok:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"ERROR CRÍTICO: Falló la configuración de la API de Gemini con la clave proporcionada: {e}")
        initial_config_ok = False

# Configuración del modelo
generation_config = {
  "temperature": 0.7, # Controla la creatividad. Más bajo = más determinista.
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048, # Máximo de tokens en la respuesta
}

safety_settings = [ # Ajusta según tus necesidades
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

# Modelo a elección (ListModels para elegir otros)
model = None
chat_session = None

if initial_config_ok:
    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest", # O el modelo que estés usando
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)
        # Para chat, es mejor iniciar una sesión de chat
        chat_session = model.start_chat(history=[]) # Puedes inicializar con historial si quieres
    except Exception as e:
        print(f"ERROR CRÍTICO: Error al inicializar el modelo Gemini: {e}")
        # Podrías querer manejar esto de forma más robusta,
        # por ejemplo, no iniciando la app o mostrando un error.
        model = None 
        chat_session = None
        initial_config_ok = False
else:
    # Si la configuración de la API Key ya falló, no intentamos inicializar el modelo.
    print("INFO: Saltando la inicialización del modelo Gemini debido a un error previo en la configuración de la API Key.")


@app.route('/')
def index():
    """Sirve la página principal."""
    if not initial_config_ok:
        # Podríamos mostrar una página de error aquí si la configuración falló gravemente
        # return "Error: La aplicación no pudo iniciarse correctamente debido a un problema de configuración. Por favor, revisa los logs o la consola.", 503
        # Por ahora, intentamos servir la página, pero el chat no funcionará.
        pass
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_gemini():
    if not initial_config_ok or not model or not chat_session:
        error_msg = "El modelo Gemini no está inicializado correctamente. "
        if not initial_config_ok:
            error_msg += "Hubo un problema con la configuración de la API Key o del modelo al inicio. Revisa la consola."
        return jsonify({"error": error_msg}), 500

    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "No se recibió ninguna pregunta."}), 400

    user_question = data['question']

    try:
        # Envía el mensaje al chat y obtén la respuesta
        # La API de chat mantiene el historial automáticamente si usas chat_session.send_message
        response = chat_session.send_message(user_question)
        
        # Gemini puede devolver texto en formato Markdown.
        # Convertirlo a HTML puede ser útil para una mejor visualización.
        # Si no quieres Markdown, puedes intentar obtener response.text directamente.
        # Asegúrate de instalar la librería: pip install Markdown
        html_response = markdown.markdown(response.text)
        return jsonify({"answer": html_response})

    except Exception as e:
        print(f"Error al comunicarse con Gemini: {e}")
        # Intenta obtener más detalles del error si es una APIError de Google
        error_message = str(e)
        if hasattr(e, 'message'): # Para algunos errores de la API de Google
            error_message = e.message
        
        # Si el error es por contenido bloqueado (safety settings)
        if "response.prompt_feedback" in str(e).lower() or "response.candidates[0].finish_reason" in str(e).lower():
             # Esto es un poco genérico, idealmente inspeccionarías response.prompt_feedback
             # o response.candidates[0].finish_reason si la API lo permite directamente en la excepción
            error_message = "La pregunta o la respuesta fue bloqueada por las políticas de seguridad."
            # Podrías querer acceder a response.prompt_feedback para más detalles si la estructura del error lo permite
            # Por ejemplo, si la excepción `e` tuviera un atributo `response_object` que contenga el `response` original.
            # if hasattr(e, 'response_object') and e.response_object.prompt_feedback:
            #    error_message += f" Razón: {e.response_object.prompt_feedback}"
        return jsonify({"error": f"Error al procesar la pregunta con Gemini: {error_message}"}), 500

def open_browser():
    """Abre el navegador web en la URL de la aplicación."""
    # Solo intenta abrir el navegador si la configuración inicial fue OK
    if initial_config_ok:
        try:
            webbrowser.open_new("http://127.0.0.1:5000/")
            print("INFO: Navegador abierto en http://127.0.0.1:5000/")
        except Exception as e:
            print(f"ADVERTENCIA: No se pudo abrir el navegador automáticamente: {e}")
    else:
        print("INFO: No se abrirá el navegador debido a errores de configuración inicial.")


if __name__ == '__main__':
    if not initial_config_ok:
        print("--------------------------------------------------------------------")
        print("ERROR: La aplicación no pudo iniciar cor3rectamente debido a errores de configuración.")
        print("Por favor, revisa los mensajes de error anteriores en esta consola.")
        print("Asegúrate de que el archivo .env existe junto al ejecutable (o en la carpeta del script si ejecutas con python app.py)")
        print("y que contiene una GEMINI_API_KEY válida.")
        print("--------------------------------------------------------------------")
        # Para ejecutables --windowed, el usuario no verá esto.
        # En un futuro, podrías escribir a un archivo de log o mostrar un popup.
        if not (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')): # Si no está empaquetado o es consola
            input("Presiona Enter para salir...")
        sys.exit(1) # Salir con código de error
    
    # Abrir el navegador un poco después de que el servidor haya tenido tiempo de arrancar
    # Solo si la configuración fue exitosa.
    Timer(1.5, open_browser).start() # Damos 1.5 segundos

    print("INFO: Iniciando servidor Flask...")
    # debug=False y use_reloader=False son importantes para producción/ejecutables
    # y para que PyInstaller funcione correctamente.
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)