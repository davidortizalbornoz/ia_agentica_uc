import os
import time

from google import genai
from google.genai import types

from entorno_local import leer_clave

# 1) Leer la key desde el .env de la raíz del repositorio
GEMINI_API_KEY = leer_clave("GEMINI_API_KEY")
assert len(GEMINI_API_KEY) > 20, \
    "GEMINI_API_KEY está incompleta. Pega la key completa desde https://aistudio.google.com/apikey (botón 'Copiar clave')."
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

# 2) Elegir el modelo: buscamos uno que esté disponible en TU proyecto gratuito y que respete `temperature`
#    (los modelos Gemini 3.6+ y 4 la ignoran, por eso preferimos Flash-Lite 3.5 o 2.5)
client = genai.Client()

def _corte_de_conexion(error):
    """No se pudo hablar con la API: conexión rechazada, cortada o agotada."""
    nombre = type(error).__name__
    mensaje = str(error)
    return (
        nombre in {
            "ReadError", "ConnectError", "RemoteProtocolError",
            "ConnectTimeout", "ReadTimeout", "WriteError", "NetworkError", "PoolTimeout",
        }
        or "Connection reset by peer" in mensaje
        or "Connection refused" in mensaje
        or "Errno 54" in mensaje
        or "Errno 61" in mensaje
        or "Server disconnected" in mensaje
    )


def _listar_modelos(reintentos=2):
    """Modelos del proyecto que aceptan generateContent."""
    for intento in range(reintentos + 1):
        try:
            disponibles = []
            for m in client.models.list():
                nombre = m.name or ""
                acciones = getattr(m, "supported_actions", None) or []
                if nombre and (not acciones or "generateContent" in acciones):
                    disponibles.append(nombre.replace("models/", ""))
            return disponibles
        except Exception as e:
            if _corte_de_conexion(e) and intento < reintentos:
                print("  (se cortó la conexión al listar modelos, esperando 20 s...)")
                time.sleep(20)
                continue
            if _corte_de_conexion(e):
                raise SystemExit(
                    "Se cortó la conexión al consultar los modelos disponibles. "
                    "Vuelve a ejecutar el script."
                ) from None
            raise SystemExit(
                f"No se pudo consultar los modelos disponibles: {type(e).__name__}: {e}"
            ) from None
    raise SystemExit("No se pudo consultar los modelos disponibles.")


def elegir_modelo(modelo_forzado=""):
    """Elige un modelo que acepte generateContent.

    Si `modelo_forzado` trae un nombre, se usa ese. Si viene vacío, se toma
    el primero de PREFERIDOS (en .env) que esté disponible en el proyecto.
    """
    disponibles = _listar_modelos()
    if not disponibles:
        raise SystemExit("No hay modelos con generateContent en tu proyecto.")

    if modelo_forzado.strip():
        modelo_forzado = modelo_forzado.strip()
        if modelo_forzado not in disponibles:
            raise SystemExit(
                f"El modelo {modelo_forzado} no está disponible en tu proyecto. "
                f"Modelos: {disponibles[:30]}"
            )
        return modelo_forzado

    preferidos = [
        nombre.strip().strip('"').strip("'")
        for nombre in leer_clave("PREFERIDOS").strip("[]").split(",")
    ]
    preferidos = [nombre for nombre in preferidos if nombre]
    elegido = next((p for p in preferidos if p in disponibles), None)
    if elegido is None:
        print("Ninguno de los modelos preferidos está disponible. Modelos de tu proyecto:", disponibles[:30])
        elegido = next((d for d in disponibles if "flash" in d), disponibles[0])
    return elegido

MODEL = elegir_modelo()

# Precios de referencia del nivel DE PAGO, en USD por 1M tokens (https://ai.google.dev/gemini-api/docs/pricing).
# En el nivel gratuito no pagas, pero calcularemos cuánto costaría para entender la economía de un LLM.
PRECIOS = {
    "gemini-3.5-flash-lite": {"input": 0.30, "output": 2.50},
    "gemini-3.8-flash":      {"input": 0.75, "output": 3.75},
    "gemini-3.1-flash-lite": {"input": 0.25, "output": 1.50},
    "gemini-2.5-flash":      {"input": 0.30, "output": 2.50},
    "gemini-2.5-flash-lite": {"input": 0.10, "output": 0.40},
}

def costo_usd(input_tokens, output_tokens, model=None):
    p = PRECIOS.get(model or MODEL, PRECIOS["gemini-3.5-flash-lite"])   # si el modelo no está en la tabla, usa un precio de referencia
    return ((input_tokens or 0) * p["input"] + (output_tokens or 0) * p["output"]) / 1_000_000

def generar(contents, reintentos=2, model=None, **config):
    """Llama al modelo; si el nivel gratuito devuelve 429, 503 o se corta la conexión, espera y reintenta.

    `model` fuerza un modelo para esta llamada. Si viene vacío, se usa MODEL.
    """
    modelo = model or MODEL
    for intento in range(reintentos + 1):
        try:
            return client.models.generate_content(model=modelo, contents=contents,
                                                  config=types.GenerateContentConfig(**config))
        except Exception as e:
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                if intento < reintentos:
                    print("  (límite de uso alcanzado, esperando 20 s...)")
                    time.sleep(20)
                    continue
                raise SystemExit(
                    "Se alcanzó el límite de uso del nivel gratuito (429). "
                    "Espera un momento y vuelve a ejecutar el script."
                ) from None
            if "503" in msg or "UNAVAILABLE" in msg:
                if intento < reintentos:
                    print("  (el modelo está con mucha demanda, esperando 20 s...)")
                    time.sleep(20)
                    continue
                raise SystemExit(
                    f"El modelo {modelo} sigue con mucha demanda (503). "
                    "Espera un momento y vuelve a ejecutar el script."
                ) from None
            if _corte_de_conexion(e):
                if intento < reintentos:
                    print(f"  (se cortó la conexión con {modelo}, esperando 20 s...)")
                    time.sleep(20)
                    continue
                raise SystemExit(
                    f"Se cortó la conexión al consultar {modelo}. "
                    "Vuelve a ejecutar el script."
                ) from None
            if "404" in msg or "NOT_FOUND" in msg:
                raise SystemExit(f"El modelo {modelo} no está disponible en tu proyecto. Cambia MODEL por otro de la lista de la celda anterior.") from None
            if "403" in msg or "401" in msg or "API_KEY_INVALID" in msg:
                raise SystemExit("La API key fue rechazada. Verifica que la copiaste completa desde https://aistudio.google.com/apikey y que no está restringida a otra API.") from None
            raise SystemExit(f"No se pudo consultar {modelo}: {type(e).__name__}: {msg}") from None
    raise SystemExit(f"No se pudo consultar {modelo}.")

def contar_tokens(texto):
    return client.models.count_tokens(model=MODEL, contents=texto).total_tokens
