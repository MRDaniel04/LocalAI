import os
import sys # Necesario para PyInstaller
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import markdown # Para convertir Markdown a HTML si Gemini responde en Markdown
import webbrowser # Para abrir el navegador
from threading import Timer # Para abrir el navegador después de que el servidor inicie
from werkzeug.utils import secure_filename # Para nombres de archivo seguros
# import tempfile # Opcional, si decides guardar archivos temporalmente en disco

# --- Determinar la ruta base para PyInstaller ---
# Esto es crucial para que PyInstaller encuentre las carpetas static y templates
# cuando se ejecuta desde el archivo empaquetado.
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

template_folder = os.path.join(base_dir, 'templates')
static_folder = os.path.join(base_dir, 'static')

# Cargar variables de entorno desde .env
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    dotenv_path = os.path.join(os.path.dirname(sys.executable), '.env')
else:
    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
else:
    print(f"ADVERTENCIA: No se encontró el archivo .env en {dotenv_path}. La API Key debe estar configurada de otra manera (ej. variables de entorno del sistema).")

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

# Configuración de la API Key de Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
initial_config_ok = True

if not GEMINI_API_KEY:
    print("ERROR CRÍTICO: No se encontró la API Key de Gemini...")
    initial_config_ok = False

if initial_config_ok:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"ERROR CRÍTICO: Falló la configuración de la API de Gemini: {e}")
        initial_config_ok = False

# Configuración del modelo
generation_config = {
  "temperature": 0.7,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = None
chat_session = None

if initial_config_ok:
    try:
        # Asegúrate de que este modelo ("gemini-1.5-flash-latest") soporte el tipo de entrada que le darás
        # (texto, o texto + imágenes si implementas multimodalidad)
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)
        chat_session = model.start_chat(history=[])
    except Exception as e:
        print(f"ERROR CRÍTICO: Error al inicializar el modelo Gemini: {e}")
        model = None
        chat_session = None
        initial_config_ok = False
else:
    print("INFO: Saltando la inicialización del modelo Gemini debido a un error previo en la configuración de la API Key.")

# --- Configuración para subida de archivos ---
# UPLOAD_FOLDER = 'uploads_temp' # Opcional: si quieres guardar archivos en disco
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {'txt', 'md', 'py', 'js', 'html', 'css', 'json', 'csv', 'png', 'jpg', 'jpeg', 'gif', 'pdf'} # Amplía según necesites

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# --- Fin de configuración para subida de archivos ---

@app.route('/')
def index():
    """Sirve la página principal."""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_gemini():
    if not initial_config_ok or not model or not chat_session: # Verificación de estado de la app
        error_msg = "El modelo Gemini no está inicializado correctamente. "
        if not initial_config_ok:
            error_msg += "Hubo un problema con la configuración de la API Key o del modelo al inicio. Revisa la consola."
        return jsonify({"error": error_msg}), 500

    # Obtener datos del formulario (multipart/form-data)
    user_question = request.form.get('question', '') # Pregunta de texto
    file_storage = request.files.get('file')      # Archivo adjunto (objeto FileStorage de Flask)

    file_content_for_prompt = ""
    file_description_for_prompt = "" # Para describir el archivo al modelo

    if file_storage: # Si se subió un archivo
        if file_storage.filename == '':
            # Esto no debería pasar si el JS valida, pero por si acaso
            print("Advertencia: Se recibió una solicitud de archivo sin nombre de archivo.")
        elif allowed_file(file_storage.filename):
            filename = secure_filename(file_storage.filename)
            file_description_for_prompt = f"Se ha adjuntado un archivo llamado '{filename}'."
            
            # Procesar el contenido del archivo
            # Por ahora, nos enfocaremos en leer archivos de texto.
            # Para otros tipos (imágenes, PDF), se necesitaría lógica más compleja.
            file_extension = filename.rsplit('.', 1)[1].lower()

            if file_extension == 'txt' or file_extension == 'md': # Archivos de texto plano o Markdown
                try:
                    # Leer el contenido del archivo en memoria
                    file_bytes = file_storage.read()
                    file_content_for_prompt = file_bytes.decode('utf-8')
                    # Limitar la cantidad de texto para no exceder límites del prompt
                    max_file_chars = 5000 # Ajusta este límite
                    if len(file_content_for_prompt) > max_file_chars:
                        file_content_for_prompt = file_content_for_prompt[:max_file_chars] + "\n[...contenido truncado...]"
                    file_description_for_prompt += " Su contenido (o parte de él) es:"
                except Exception as e:
                    print(f"Error al leer el archivo de texto '{filename}': {e}")
                    file_content_for_prompt = f"[Error al leer el contenido del archivo '{filename}']"
            
            elif file_extension in {'png', 'jpg', 'jpeg', 'gif'}:
                # Aquí es donde manejarías archivos de imagen para un modelo multimodal.
                # El modelo "gemini-1.5-flash-latest" PUEDE tener capacidades multimodales.
                # Necesitarías preparar los datos de la imagen (bytes y mimetype)
                # y pasarlos a model.generate_content() en una estructura de "parts".
                # Por ahora, solo informamos que es una imagen.
                file_description_for_prompt += " Es un archivo de imagen."
                # file_content_for_prompt = {"type": "image", "data": file_storage.read(), "mime_type": file_storage.mimetype} # Ejemplo conceptual
                # Esta línea anterior es solo un placeholder, la implementación real depende del SDK.
                # Por ahora, no pasaremos el contenido binario directamente al prompt de texto.
                file_content_for_prompt = "[Contenido de imagen no procesado para el prompt de texto actual. El modelo podría necesitar una entrada multimodal.]"

            elif file_extension == 'pdf':
                # Para PDFs, necesitarías una librería como PyPDF2 o pdfminer.six
                # from PyPDF2 import PdfReader
                # try:
                #     reader = PdfReader(file_storage) # file_storage es un stream
                #     text = ""
                #     for page in reader.pages:
                #         text += page.extract_text() + "\n"
                #     file_content_for_prompt = text[:max_file_chars] # ... truncar
                #     file_description_for_prompt += " Su contenido extraído (o parte de él) es:"
                # except Exception as e:
                #     print(f"Error extrayendo texto de PDF '{filename}': {e}")
                #     file_content_for_prompt = f"[Error al procesar el archivo PDF '{filename}']"
                file_description_for_prompt += " Es un archivo PDF."
                file_content_for_prompt = "[Extracción de texto de PDF no implementada en este ejemplo.]"

            else: # Otros tipos de archivo permitidos pero no procesados específicamente
                file_description_for_prompt += f" Es un archivo de tipo '{file_extension}'."
                file_content_for_prompt = "[Tipo de archivo no procesado para extracción de contenido directo.]"
        else:
            return jsonify({"error": "Tipo de archivo no permitido."}), 400

    # Construir el prompt final para Gemini
    # Si se usa un modelo puramente de texto con chat_session.send_message:
    prompt_parts = []
    if user_question:
        prompt_parts.append(user_question)
    if file_description_for_prompt:
        prompt_parts.append(f"\n\n{file_description_for_prompt}")
    if file_content_for_prompt and isinstance(file_content_for_prompt, str): # Solo si es texto extraído
        prompt_parts.append(f"\n{file_content_for_prompt}")
    
    final_prompt_text = "\n".join(prompt_parts).strip()

    if not final_prompt_text: # Si no hay pregunta ni archivo procesable
        return jsonify({"error": "No hay contenido para enviar a la IA (ni pregunta ni archivo procesable)."}), 400

    try:
        # Para modelos de texto y chat_session:
        response = chat_session.send_message(final_prompt_text)
        
        # Si estuvieras usando un modelo multimodal con model.generate_content()
        # y `file_content_for_prompt` fuera un diccionario con datos de imagen:
        #
        # gemini_api_parts = []
        # if user_question:
        #     gemini_api_parts.append(user_question)
        # if isinstance(file_content_for_prompt, dict) and file_content_for_prompt.get("type") == "image":
        #     # El SDK de Gemini espera algo como:
        #     # from google.generativeai.types import HarmCategory, HarmBlockThreshold, Part
        #     # image_part = Part.from_data(data=file_content_for_prompt["data"], mime_type=file_content_for_prompt["mime_type"])
        #     # gemini_api_parts.append(image_part)
        #     # response = model.generate_content(gemini_api_parts, stream=False) # o True para streaming
        #     pass # Esta lógica debe ser implementada cuidadosamente según el SDK
        # else: # Fallback a chat_session si no es una imagen procesada para multimodal
        #     response = chat_session.send_message(final_prompt_text)

        html_response = markdown.markdown(response.text)
        return jsonify({"answer": html_response})

    except Exception as e:
        print(f"Error al comunicarse con Gemini: {e}")
        error_message = str(e)
        if hasattr(e, 'message'):
            error_message = e.message
        if "response.prompt_feedback" in str(e).lower() or "response.candidates[0].finish_reason" in str(e).lower():
            error_message = "La pregunta o la respuesta fue bloqueada por las políticas de seguridad."
        return jsonify({"error": f"Error al procesar la pregunta con Gemini: {error_message}"}), 500

def open_browser():
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
        print("ERROR: La aplicación no pudo iniciar correctamente...")
        # ... (mensajes de error como los tenías)
        print("--------------------------------------------------------------------")
        if not (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')):
            input("Presiona Enter para salir...")
        sys.exit(1)
    
    Timer(1.5, open_browser).start()
    print("INFO: Iniciando servidor Flask...")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)