import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import markdown # Para convertir Markdown a HTML si Gemini responde en Markdown

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)

# Configuración de la API Key de Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("No se encontró la API Key de Gemini. Asegúrate de que el archivo .env está configurado.")

genai.configure(api_key=GEMINI_API_KEY)

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
try:
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest", 
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)
    # Para chat, es mejor iniciar una sesión de chat
    chat_session = model.start_chat(history=[]) # Puedes inicializar con historial si quieres
except Exception as e:
    print(f"Error al inicializar el modelo Gemini: {e}")
    # Podrías querer manejar esto de forma más robusta,
    # por ejemplo, no iniciando la app o mostrando un error.
    model = None 
    chat_session = None


@app.route('/')
def index():
    """Sirve la página principal."""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_gemini():
    if not model or not chat_session:
        return jsonify({"error": "El modelo Gemini no está inicializado correctamente."}), 500

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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) # host='0.0.0.0' para acceder desde otros dispositivos en la red local