# CELDA 16 — Código: Crear `README.md`
# Generamos el archivo `README.md` con la documentación del proyecto.

# ClaimAI Policy Analyzer

## Asistente IA para análisis preliminar de pólizas y siniestros

### Descripción del Proyecto
Este proyecto es una aplicación web desarrollada con Gradio que actúa como un asistente inteligente para el análisis de pólizas de seguros y la gestión preliminar de siniestros. Está diseñado para ayudar a ajustadores, abogados y técnicos del sector asegurador en la revisión de documentos (PDF, DOCX, TXT) y la generación de comunicaciones técnicas, utilizando el modelo de IA Gemini.

### Objetivo
El objetivo principal es proveer una herramienta eficiente para:
1.  Extraer y analizar información estructurada de pólizas de seguros.
2.  Comparar descripciones de siniestros con las coberturas y exclusiones de una póliza.
3.  Generar correos electrónicos formales con lenguaje técnico de seguros para diversas gestiones.

**ADVERTENCIA IMPORTANTE:** Esta herramienta es un asistente de IA y **no reemplaza** el análisis técnico, legal ni contractual de un profesional. Sus resultados son **preliminares** y requieren validación humana.

### Tecnologías Utilizadas
*   **Python:** Lenguaje de programación principal.
*   **Gradio:** Framework para la construcción de la interfaz de usuario web.
*   **Gemini API (google-generativeai):** Modelo de Inteligencia Artificial Generativa para análisis de texto.
*   **pypdf:** Biblioteca para la extracción de texto de archivos PDF.
*   **python-docx:** Biblioteca para la extracción de texto de archivos DOCX.
*   **python-dotenv:** Para la gestión de variables de entorno (uso local).
*   **HuggingFace Spaces:** Plataforma de deployment para la aplicación web.
*   **GitHub:** Repositorio de código fuente.

### Funcionalidades de la App
La aplicación cuenta con tres pestañas principales:

1.  **Análisis de Póliza:** Carga una póliza y la IA genera un informe estructurado con tipo de póliza, asegurado, vigencia, coberturas, exclusiones, deducibles, etc.
2.  **Análisis de Siniestro contra Póliza:** Carga una póliza y una descripción del siniestro. La IA compara ambos y ofrece un análisis preliminar de cobertura, riesgos y documentación pendiente.
3.  **Generador de Correo Formal:** Carga una póliza y una instrucción. La IA redacta un correo técnico de seguros (asunto, saludo, contexto, solicitud, cierre, firma).

### Instalación Local
1.  Clona el repositorio de GitHub:
    ```bash
    git clone https://github.com/[TU_USUARIO_DE_GITHUB]/[TU_REPOSITORIO].git
    cd [TU_REPOSITORIO]
    ```
2.  Crea un entorno virtual (opcional pero recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```
3.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Crea un archivo `.env` en la raíz del proyecto y añade tu API Key de Gemini:
    ```
    GEMINI_API_KEY="TU_API_KEY_DE_GEMINI"
    ```
    *(Obtén tu API Key en [Google AI Studio](https://aistudio.google.com/app/apikey))*.
    *(Recuerda añadir `python-dotenv` a tu `requirements.txt` para cargar este archivo).*

### Ejecución Local
Ejecuta el archivo `app.py`:
```bash
python app.py
```
La aplicación se iniciará en tu navegador en `http://127.0.0.1:7860` o una dirección similar.

### Deployment en HuggingFace Spaces
1.  Crea una cuenta en [HuggingFace](https://huggingface.co/).
2.  Ve a [Spaces](https://huggingface.co/spaces) y crea un "New Space".
3.  Elige "Gradio" como SDK y "Public" o "Private" según tu preferencia.
4.  Copia los archivos `app.py` y `requirements.txt` a tu nuevo Space.
5.  **Configura la `GEMINI_API_KEY` como un Secreto:**
    *   En tu Space, ve a la pestaña "Settings".
    *   Bajo "Repository secrets", añade un nuevo secreto con el nombre `GEMINI_API_KEY` y pega tu clave de API de Gemini como valor.
6.  El Space se desplegará automáticamente. Una vez listo, tu aplicación estará accesible en la URL proporcionada por HuggingFace.

### Configuración de GEMINI_API_KEY como Secreto en HuggingFace Spaces
Es crucial no exponer tu API Key directamente en el código de tu repositorio. En HuggingFace Spaces, esto se gestiona mediante secretos de repositorio:
1.  Navega a tu HuggingFace Space.
2.  Haz clic en la pestaña **"Settings"** (Configuración).
3.  Desplázate hasta la sección **"Repository secrets"** (Secretos del repositorio).
4.  Haz clic en **"Add a new secret"**.
5.  En el campo **"Name"**, introduce `GEMINI_API_KEY` (debe coincidir exactamente).
6.  En el campo **"Value"**, pega tu clave de API de Gemini.
7.  Haz clic en **"Add secret"**.
La aplicación desplegada podrá acceder a esta clave de forma segura a través de `os.getenv('GEMINI_API_KEY')`.

### Capturas de Pantalla Sugeridas para la Entrega
Para la entrega de tu proyecto, se recomienda incluir capturas de pantalla que demuestren la funcionalidad y el despliegue de tu aplicación. Aquí algunas sugerencias:
*   **Pantalla principal de la aplicación:** Un pantallazo general de la interfaz de Gradio.
*   **Carga de una póliza:** Una captura mostrando un archivo cargado en una de las pestañas.
*   **Resultado de "Análisis de Póliza":** Un pantallazo con el informe estructurado generado por la IA.
*   **Resultado de "Análisis de Siniestro":** Una captura mostrando el análisis comparativo del siniestro.
*   **Correo Generado:** Un pantallazo del correo formal técnico de seguros generado.
*   **Repositorio GitHub:** Una captura de la página principal de tu repositorio.
*   **HuggingFace Space funcionando:** Una captura de la aplicación desplegada en la URL pública de HuggingFace.

**¡Buena suerte con tu proyecto!**
