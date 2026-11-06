"""Cliente de la API de Gemini para la Tarea 1. **No hay nada que completar en este archivo.**

Es la misma lógica que usaste en los prácticos 1 a 3, convertida en módulo:
- la key se lee de la variable de entorno GEMINI_API_KEY (archivo .env, que NO se entrega ni se sube a git);
- se elige automáticamente un modelo disponible en tu proyecto gratuito, con uno de respaldo;
- `generar()` reintenta ante 429 (límite de uso) y ante 500/503 (saturación), y cambia de modelo si hace falta;
- todo queda registrado en logs/agente.log (evidencia de ejecución para el informe).
"""
import logging
import os
import pathlib
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

pathlib.Path("logs").mkdir(exist_ok=True)
log = logging.getLogger("tarea1")
if not log.handlers:
    log.setLevel(logging.INFO)
    _fh = logging.FileHandler("logs/agente.log", encoding="utf-8")
    _fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    log.addHandler(_fh)

PREFERIDOS = ["gemini-3.5-flash-lite", "gemini-2.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-3.8-flash"]

# Precios de referencia del nivel DE PAGO, en USD por 1M tokens (https://ai.google.dev/gemini-api/docs/pricing).
# En el nivel gratuito no pagas; los usamos para estimar cuánto costaría tu agente en producción.
PRECIOS = {
    "gemini-3.5-flash-lite": {"input": 0.30, "output": 2.50},
    "gemini-3.8-flash":      {"input": 0.75, "output": 3.75},
    "gemini-3.1-flash-lite": {"input": 0.25, "output": 1.50},
    "gemini-2.5-flash":      {"input": 0.30, "output": 2.50},
    "gemini-2.5-flash-lite": {"input": 0.10, "output": 0.40},
}

_client = None
MODEL = None
RESPALDO = []


def obtener_cliente():
    """Crea el cliente la primera vez que se necesita (así los tests no requieren key)."""
    global _client, MODEL, RESPALDO
    if _client is not None:
        return _client
    key = os.environ.get("GEMINI_API_KEY", "")
    if len(key) < 20:
        raise SystemExit(
            "Falta GEMINI_API_KEY. Crea un archivo .env (copia .env.example) con tu key gratuita de "
            "https://aistudio.google.com/apikey . Nunca la escribas en el código ni la subas al repositorio."
        )
    _client = genai.Client(api_key=key)
    disponibles = []
    for m in _client.models.list():
        acciones = getattr(m, "supported_actions", None) or []
        if not acciones or "generateContent" in acciones:
            disponibles.append(m.name.replace("models/", ""))
    MODEL = next((p for p in PREFERIDOS if p in disponibles), None)
    if MODEL is None:
        MODEL = next((d for d in disponibles if "flash" in d), disponibles[0])
    RESPALDO = [p for p in PREFERIDOS if p in disponibles and p != MODEL]
    log.info("Modelo elegido: %s | respaldo: %s", MODEL, RESPALDO)
    return _client


def generar(contents, reintentos=3, **config):
    """Llama al modelo con manejo de los errores típicos del nivel gratuito.

    `config` acepta cualquier campo de GenerateContentConfig: system_instruction, temperature, tools,
    automatic_function_calling, response_mime_type, response_schema, ...
    """
    global MODEL
    client = obtener_cliente()
    for intento in range(reintentos + 1):
        try:
            r = client.models.generate_content(model=MODEL, contents=contents,
                                               config=types.GenerateContentConfig(**config))
            u = r.usage_metadata
            log.info("llamada ok | modelo=%s | tokens in=%s out=%s", MODEL,
                     getattr(u, "prompt_token_count", None), getattr(u, "candidates_token_count", None))
            return r
        except Exception as e:
            msg = str(e)
            if ("429" in msg or "RESOURCE_EXHAUSTED" in msg) and intento < reintentos:
                log.warning("429: límite de uso, esperando 20 s")
                print("  (límite de uso alcanzado, esperando 20 s...)")
                time.sleep(20)
            elif any(k in msg for k in ("500", "503", "INTERNAL", "UNAVAILABLE", "overloaded", "not available")):
                if intento < reintentos:
                    espera = 5 * 2 ** intento
                    log.warning("error transitorio del servidor, reintento en %s s: %s", espera, msg[:120])
                    print(f"  (error transitorio del servidor, reintentando en {espera} s...)")
                    time.sleep(espera)
                elif RESPALDO:
                    anterior, MODEL = MODEL, RESPALDO.pop(0)
                    log.warning("%s sigue fallando; cambio a %s", anterior, MODEL)
                    print(f"  ⚠️ {anterior} sigue fallando; cambiamos a {MODEL} y seguimos.")
                    return generar(contents, reintentos=reintentos, **config)
                else:
                    raise SystemExit("Gemini devolvió errores 500/503 en todos los modelos disponibles. "
                                     "Suele ser saturación temporal: espera unos minutos y vuelve a intentar.")
            elif "404" in msg or "NOT_FOUND" in msg:
                raise SystemExit(f"El modelo {MODEL} no está disponible en tu proyecto. Revisa PREFERIDOS en cliente.py.")
            elif "403" in msg or "401" in msg or "API_KEY_INVALID" in msg:
                raise SystemExit("La API key fue rechazada. Verifica que la copiaste completa desde "
                                 "https://aistudio.google.com/apikey y que no está restringida a otra API.")
            else:
                log.error("error no manejado: %s", msg[:300])
                raise


def costo_usd(input_tokens, output_tokens, model=None):
    """Costo estimado en USD si el modelo se pagara (nivel de pago)."""
    p = PRECIOS.get(model or MODEL, PRECIOS["gemini-3.5-flash-lite"])
    return ((input_tokens or 0) * p["input"] + (output_tokens or 0) * p["output"]) / 1_000_000
