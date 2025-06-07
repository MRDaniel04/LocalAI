import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar variables de entorno (para obtener la API key)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: No se encontró la API Key de Gemini en el archivo .env.")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("Modelos disponibles que soportan 'generateContent':")
        print("-------------------------------------------------")
        found_models = False
        for m in genai.list_models():
            # Verificamos que el método 'generateContent' (usado por send_message) esté soportado
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
                found_models = True
        
        if not found_models:
            print("No se encontraron modelos que soporten 'generateContent'.")
            print("\nTodos los modelos listados por la API (sin filtrar por método):")
            print("-------------------------------------------------------------")
            for m_all in genai.list_models():
                print(f"- {m_all.name} (Soporta: {m_all.supported_generation_methods})")

    except Exception as e:
        print(f"Ocurrió un error al intentar listar los modelos: {e}")