import os
from flask import Flask, request, jsonify, abort
from datetime import datetime

app = Flask(__name__)

# CONFIGURACIÓN
# En producción, usa variables de entorno. Aquí definimos un default para pruebas.
# API Key que deberás poner en los Headers de ChatGPT (Authentication Type: API Key)
API_KEY = os.environ.get("API_KEY", "sk-proj-tu-clave-secreta-rama-judicial-2025")

def verify_auth():
    """Verifica que el Header Authorization contenga el Bearer Token correcto."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        abort(401, description="Falta el token de autorización o es inválido.")
    
    token = auth_header.split(" ")[1]
    if token != API_KEY:
        abort(403, description="Token no autorizado.")

def mock_data_rama_judicial(radicado):
    """
    Simulación de respuesta para probar la integración con ChatGPT
    mientras se decide entre Scraping o API de Terceros.
    """
    return {
        "radicado": radicado,
        "juzgado": "JUZGADO 005 LABORAL DE PEREIRA",
        "sujetos_procesales": "JUAN PEREZ vs. EMPRESA X S.A.S.",
        "ultima_actuacion": {
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "anotacion": "Auto que libra mandamiento de pago y decreta embargo",
            "link_documento": "https://procesos.ramajudicial.gov.co/documentos/ejemplo.pdf"
        },
        "estado_actual": "ACTIVO",
        "fuente": "Simulación (Mock Data) - Conecta un proveedor real para producción"
    }

def consultar_proveedor_externo(radicado):
    """
    PLACEHOLDER: Aquí iría la lógica real.
    
    Opción A (Scraping): Instanciar Selenium/Puppeteer, resolver Captcha, parsear HTML.
    Opción B (API Terceros): Requests.get('https://api.justiciaaldia.com/v1/proceso', params={...})
    """
    # Lógica condicional: Si tienes un proveedor, descomenta esto:
    # response = requests.get(f"PROVIDER_URL/{radicado}", headers={"ApiKey": "PROVIDER_KEY"})
    # return response.json()
    
    # Por defecto, devolvemos el mock para que la API funcione hoy mismo.
    return mock_data_rama_judicial(radicado)

@app.route('/api/consultar', methods=['GET'])
def consultar_proceso():
    # 1. Seguridad
    verify_auth()
    
    # 2. Obtener Input
    radicado = request.args.get('radicado')
    
    # 3. Validación Básica
    if not radicado:
        return jsonify({"error": "Falta el parámetro 'radicado'"}), 400
    
    if len(radicado) != 23:
        return jsonify({"error": "El radicado debe tener 23 dígitos exactos"}), 400

    try:
        # 4. Procesamiento (Llamada a lógica de negocio)
        data = consultar_proveedor_externo(radicado)
        
        # 5. Output Estándar
        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": "Error interno del servidor", "detalle": str(e)}), 500

if __name__ == '__main__':
    # Ejecutar en puerto 8080 (común para Cloud Run / App Platform)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
