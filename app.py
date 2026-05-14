# CELDA 14 — Código: Crear `app.py` completo para deployment
# Este archivo `app.py` contendrá todo el código necesario para desplegar la aplicación en HuggingFace Spaces.
# Se utiliza `%%writefile` para crear el archivo en el sistema de archivos de Colab.

# Nota: En un entorno de producción como HuggingFace Spaces, la API Key se cargaría desde `os.environ`
# y no se usaría `google.colab.userdata` ni `getpass`.

# Importaciones deben estar al inicio del archivo app.py
# Definiciones de funciones y la interfaz Gradio deben seguir.

import os
import gradio as gr
import google.generativeai as genai
import pypdf
from docx import Document
from typing import Optional, Tuple
from pathlib import Path

# Para cargar variables de entorno en un entorno local
from dotenv import load_dotenv
load_dotenv()

# Manejo de la API Key para entornos de despliegue (HuggingFace Spaces)
# La variable de entorno GEMINI_API_KEY debe configurarse en los secretos del Space.
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("La variable de entorno 'GEMINI_API_KEY' no está configurada. Por favor, configúrala en los secretos de HuggingFace Spaces.")

genai.configure(api_key=GEMINI_API_KEY)

try:
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    gemini_model = None
    print(f"Error al inicializar el modelo Gemini: {e}")
    print("Asegúrate de que tu GEMINI_API_KEY es válida y tienes acceso al modelo.")

def extract_text_from_file(file_path: str) -> Tuple[Optional[str], str]:
    MAX_CHARS = 30000
    extracted_text = ""
    message = ""

    if not file_path:
        return None, "Error: No se ha cargado ningún archivo o el archivo no existe."

    file_obj = Path(file_path)
    file_extension = file_obj.suffix.lower()

    try:
        if file_extension == '.pdf':
            reader = pypdf.PdfReader(file_obj)
            for page in reader.pages:
                extracted_text += page.extract_text() or ""
        elif file_extension == '.docx':
            doc = Document(file_obj)
            for para in doc.paragraphs:
                extracted_text += para.text + "\n"
        elif file_extension == '.txt':
            with open(file_obj, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
        else:
            return None, f"Error: Formato de archivo no soportado: {file_extension}. Se esperan .pdf, .docx, .txt."

    except Exception as e:
        return None, f"Error inesperado al extraer texto: {str(e)}"

    if not extracted_text.strip():
        return None, "Error: No se pudo extraer texto del archivo o el archivo está vacío."

    if len(extracted_text) > MAX_CHARS:
        message = f"Advertencia: El texto de la póliza se ha recortado a los primeros {MAX_CHARS} caracteres debido a límites de procesamiento. El análisis será parcial." + "\n\n" + "---\n\n" + "Contenido parcial de la póliza:\n" + extracted_text[:MAX_CHARS] + "\n...\n(Texto recortado)"
        extracted_text = extracted_text[:MAX_CHARS]
    else:
        message = f"Texto de la póliza extraído con éxito ({len(extracted_text)} caracteres)."

    return extracted_text, message

def call_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY or not gemini_model:
        return "**Error:** La GEMINI_API_KEY no está configurada o el modelo Gemini no se pudo inicializar. Por favor, revisa la configuración del Space.\n\n"\
               "Asegúrate de haber configurado tu API Key en los secretos del Space de HuggingFace con el nombre `GEMINI_API_KEY`."

    try:
        generation_config = {
            "temperature": 0.2,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        response = gemini_model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        return response.text
    except Exception as e:
        return f"**Error al comunicarse con Gemini:** {str(e)}\n\n"\
               "Esto puede deberse a un problema de conexión, un prompt demasiado largo o un problema con la API Key. Por favor, inténtalo de nuevo."

def analyze_policy(file_path: str) -> str:
    if not file_path:
        return "Error: Por favor, carga un archivo de póliza."

    policy_text, message = extract_text_from_file(file_path)

    if policy_text is None:
        return message

    prompt = f"""Actúa como un experto ajustador de seguros con amplia experiencia en la lectura y análisis de pólizas complejas.\n\nAnaliza el siguiente texto de una póliza de seguros. Tu objetivo es extraer la información más relevante y presentarla de manera estructurada para una revisión preliminar. Utiliza un lenguaje técnico de seguros y, si la información no está explícitamente en el texto, indícalo claramente.\n\n--- Texto de la Póliza ---\n{policy_text}\n---\n
Por favor, genera un informe estructurado que incluya los siguientes puntos. Si algún punto no puede ser identificado con base ÚNICAMENTE en el texto proporcionado, indica 'No identificado' o 'Debe verificarse'.\n\n1.  **Tipo de Póliza Identificada:** [Ej: Póliza de Responsabilidad Civil, Póliza de Daños Materiales, Póliza de Vida, Póliza de Automóviles, Póliza Integral de Hogar, etc.]\n2.  **Nombre del Asegurado:** [Nombre o razón social del titular de la póliza]\n3.  **Vigencia de la Póliza:** [Fecha de inicio y fecha de fin, o 'No identificado']\n4.  **Ramos o Coberturas Principales:** [Lista de las coberturas fundamentales que ofrece la póliza, ej: Incendio, Robo, RC Explotación]\n5.  **Amparos Adicionales:** [Coberturas que complementan las principales, si se mencionan explícitamente]\n6.  **Bienes o Intereses Asegurados:** [Descripción de lo que está protegido por la póliza, ej: edificio, maquinaria, mercancías, vehículo]\n7.  **Sumas Aseguradas:** [Valores monetarios máximos de indemnización por cobertura, o 'No identificadas']\n8.  **Exclusiones Relevantes:** [Cláusulas que detallan situaciones o daños no cubiertos por la póliza. Enfócate en las más comunes o críticas]\n9.  **Deducibles:** [Cantidades o porcentajes que el asegurado debe asumir en caso de siniestro por cobertura, o 'No identificados']\n10. **Garantías o Condiciones Especiales:** [Requisitos o condiciones específicas que el asegurado debe cumplir para mantener la validez de la cobertura]\n11. **Obligaciones del Asegurado en Caso de Siniestro:** [Pasos o responsabilidades del asegurado cuando ocurre un evento cubierto]\n12. **Plazos Importantes de Aviso o Reclamación:** [Límites de tiempo para notificar un siniestro o presentar documentación]\n13. **Observaciones Importantes para el Ajustador:** [Cualquier punto crítico o ambiguo que requiera especial atención durante una liquidación]\n14. **Advertencia:** Este análisis es *preliminar* y se basa *únicamente* en el texto extraído. No constituye una decisión definitiva de cobertura y **debe ser revisado y validado por un ajustador o técnico especializado**."""

    response = call_gemini(prompt)
    return message + "\n\n" + response

def analyze_claim(file_path: str, claim_description: str) -> str:
    if not file_path:
        return "Error: Por favor, carga un archivo de póliza para analizar el siniestro."

    if not claim_description or not claim_description.strip():
        return "Error: Por favor, proporciona una descripción del siniestro."

    policy_text, message = extract_text_from_file(file_path)

    if policy_text is None:
        return message

    prompt = f"""Actúa como un experto ajustador de seguros con amplia experiencia en la lectura de pólizas y la evaluación de siniestros.\n\nSe te proporciona el texto de una póliza de seguros y la descripción de un siniestro. Tu tarea es realizar un análisis preliminar, comparando la descripción del siniestro con las condiciones de la póliza para determinar la posible cobertura. Utiliza un lenguaje técnico de seguros. Si la información no está explícitamente en el texto, indícalo claramente.\n\n--- Texto de la Póliza ---\n{policy_text}\n---\n
--- Descripción del Siniestro ---\n{claim_description}\n---\n
Por favor, genera un análisis estructurado que incluya los siguientes puntos. Si algún punto no puede ser identificado con base ÚNICAMENTE en la información proporcionada, indica 'No identificado' o 'Debe verificarse'.\n\n1.  **Resumen del Siniestro:** [Breve descripción de lo ocurrido, basándose en el input del usuario]\n2.  **Fecha del Evento (si se menciona):** [Fecha identificada en la descripción del siniestro o 'No especificada']\n3.  **Bien Afectado:** [Identificación del objeto, propiedad o persona afectada, según la descripción y la póliza]\n4.  **Causa Alegada del Daño:** [Motivo del siniestro según la descripción, ej: incendio, robo, choque]\n5.  **Cobertura Posiblemente Aplicable:** [Identifica qué cobertura(s) de la póliza podrían aplicar al siniestro. Usa frases como 'Posiblemente bajo la cobertura de...']\n6.  **Exclusiones que Deben Revisarse:** [Menciona cualquier exclusión relevante en la póliza que podría afectar la cobertura de este siniestro. Usa frases como 'Podría estar sujeto a la exclusión de...']\n7.  **Deducibles o Condiciones Relevantes:** [Identifica deducibles, coaseguros o condiciones específicas de la póliza que aplicarían en este caso. Ej: 'Aplica deducible de X', 'Sujeto a condición de seguridad Y']\n8.  **Garantías que Podrían Influir en la Cobertura:** [Cualquier garantía que el asegurado deba haber cumplido y que pueda afectar la viabilidad de la cobertura]\n9.  **Documentación Pendiente por Solicitar:** [Documentos adicionales que un ajustador necesitaría para procesar el siniestro. Ej: Informe policial, facturas, fotografías]\n10. **Preguntas Clave que Debería Hacer el Ajustador:** [Interrogantes fundamentales para el ajustador para clarificar el siniestro y la cobertura]\n11. **Riesgos de Cobertura:** [Enumera factores que podrían llevar a un rechazo total o parcial de la cobertura]\n12. **Conclusión Preliminar:** [Selecciona una de las siguientes opciones y justifica brevemente con la información disponible:\n    - **Posiblemente Amparado:** La descripción del siniestro parece encajar con una cobertura de la póliza y no hay exclusiones evidentes.\n    - **Condicionado a Mayor Documentación/Información:** La cobertura es probable pero se requiere más información o documentos para una decisión.\n    - **Riesgo de Exclusión:** Existe una o varias exclusiones que podrían aplicar y es necesario un análisis más profundo.\n    - **No Concluyente con la Información Disponible:** No hay suficiente información en la póliza o en la descripción del siniestro para emitir una conclusión preliminar.]\n13. **Advertencia:** Este análisis es *preliminar* y se basa *únicamente* en el texto de la póliza y la descripción del siniestro proporcionados. No constituye una decisión definitiva de cobertura y **debe ser revisado y validado por un ajustador o técnico especializado**."""

    response = call_gemini(prompt)
    return message + "\n\n" + response

def generate_email(file_path: str, instruction: str) -> str:
    if not file_path:
        return "Error: Por favor, carga un archivo de póliza para generar el correo."

    if not instruction or not instruction.strip():
        return "Error: Por favor, proporciona una instrucción para el correo (ej. 'Solicitar informe de causa')."

    policy_text, message = extract_text_from_file(file_path)

    if policy_text is None:
        return message

    prompt = f"""Actúa como un profesional experimentado en el sector de seguros, especialista en comunicación técnica y formal.\n\nTe proporciono el texto de una póliza de seguros y una instrucción para redactar un correo electrónico. Tu tarea es generar un correo formal en español, utilizando un lenguaje técnico de seguros, adecuado para ser enviado a una aseguradora, bróker o asegurado, según la naturaleza de la instrucción. El correo debe ser claro, conciso y profesional.\n\n--- Texto de la Póliza ---\n{policy_text}\n---\n
--- Instrucción para el Correo ---\n{instruction}\n---\n
Por favor, estructura el correo de la siguiente manera:\n\n1.  **Asunto Sugerido:** [Debe ser claro y conciso, reflejando el propósito del correo y mencionando la póliza si es pertinente.]\n2.  **Saludo Formal:** [Ej: Estimados señores/as, A quien corresponda, Estimado asegurado/a, etc.]\n3.  **Contexto Breve:** [Referencia a la póliza o al siniestro, si aplica, sin entrar en detalles excesivos.]\n4.  **Solicitud Principal/Propósito:** [El objetivo claro del correo, formulado de manera cortés y profesional.]\n5.  **Lista de Documentos o Aclaraciones Requeridas (si aplica):** [Si la instrucción implica solicitar algo, enumera los ítems de forma clara.]\n6.  **Cierre Profesional:** [Ej: Agradecemos de antemano su colaboración, Quedo a la espera de sus noticias, etc.]\n7.  **Firma Genérica:** [Ej: Atentamente, Departamento de Siniestros, Un cordial saludo, etc.]\n
Recuerda usar un tono objetivo y técnico, evitando afirmaciones absolutas. Si la instrucción es ambigua, haz una suposición razonable en el contexto de seguros."""

    response = call_gemini(prompt)
    return message + "\n\n" + response


with gr.Blocks(title="ClaimAI Policy Analyzer") as demo:
    gr.Markdown("# ClaimAI Policy Analyzer")
    gr.Markdown("## Asistente IA para análisis preliminar de pólizas y siniestros")
    gr.Markdown("Esta herramienta utiliza IA para ayudarte en el análisis de pólizas de seguros, comparación con siniestros y generación de comunicaciones. \n\n**IMPORTANTE:** Esta herramienta no reemplaza el análisis técnico, legal ni contractual de un ajustador de seguros. Sus resultados son **preliminares** y están sujetos a interpretación humana y a una revisión exhaustiva de la documentación contractual original.")

    with gr.Tabs():
        with gr.TabItem("Análisis de Póliza"):
            with gr.Row():
                policy_file_analyze = gr.File(label="Cargar Póliza (PDF, DOCX, TXT)", type="filepath")
            analyze_policy_btn = gr.Button("Analizar Póliza")
            policy_analysis_output = gr.Markdown(label="Informe de Análisis de Póliza")
            analyze_policy_btn.click(
                analyze_policy,
                inputs=[policy_file_analyze],
                outputs=[policy_analysis_output]
            )

        with gr.TabItem("Análisis de Siniestro contra Póliza"):
            with gr.Row():
                policy_file_claim = gr.File(label="Cargar Póliza (PDF, DOCX, TXT)", type="filepath")
            claim_description_input = gr.Textbox(label="Descripción del Siniestro", placeholder="Ej: Incendio en el almacén el 15/05/2024, afectando mercancías. Se estima pérdida de X.", lines=5)
            analyze_claim_btn = gr.Button("Analizar Siniestro")
            claim_analysis_output = gr.Markdown(label="Análisis de Siniestro")
            analyze_claim_btn.click(
                analyze_claim,
                inputs=[policy_file_claim, claim_description_input],
                outputs=[claim_analysis_output]
            )

        with gr.TabItem("Generador de Correo Formal"):
            with gr.Row():
                policy_file_email = gr.File(label="Cargar Póliza (PDF, DOCX, TXT)", type="filepath")
            email_instruction_input = gr.Textbox(label="Instrucción para el Correo", placeholder="Ej: Solicitar informe de causa del siniestro, o pedir documentos pendientes para el asegurado.", lines=3)
            generate_email_btn = gr.Button("Generar Correo")
            email_output = gr.Markdown(label="Correo Generado")
            generate_email_btn.click(
                generate_email,
                inputs=[policy_file_email, email_instruction_input],
                outputs=[email_output]
            )

if __name__ == "__main__":
    demo.launch()
