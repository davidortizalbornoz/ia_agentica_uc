import os
import sys
import types
from pathlib import Path

# Sustituto local de Secrets de Colab: carga .env y expone google.colab.userdata.
# El fragmento de abajo queda igual que en el notebook.
_env_path = Path(__file__).resolve().parents[2] / ".env"
if _env_path.is_file():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _key, _value = _line.split("=", 1)
        os.environ.setdefault(_key.strip(), _value.strip().strip('"').strip("'"))

_userdata = types.ModuleType("google.colab.userdata")


class SecretNotFoundError(Exception):
    pass


class NotebookAccessError(Exception):
    pass


def get(name):
    value = os.environ.get(name)
    if not value:
        raise SecretNotFoundError(name)
    return value


_userdata.SecretNotFoundError = SecretNotFoundError
_userdata.NotebookAccessError = NotebookAccessError
_userdata.get = get

_colab = types.ModuleType("google.colab")
_colab.userdata = _userdata
sys.modules["google.colab"] = _colab
sys.modules["google.colab.userdata"] = _userdata

import os, time
from google.colab import userdata

# 1) Leer la key desde Secrets, con mensajes claros si algo falta
try:
    GEMINI_API_KEY = userdata.get("GEMINI_API_KEY")
except userdata.SecretNotFoundError:
    raise SystemExit("No existe un secreto llamado GEMINI_API_KEY. Créalo en el panel de Secrets (ícono de la llave) con ese nombre exacto.")
except userdata.NotebookAccessError:
    raise SystemExit("El secreto GEMINI_API_KEY existe pero no tiene 'Notebook access' activado para este notebook.")
assert GEMINI_API_KEY and len(GEMINI_API_KEY) > 20, \
    "El secreto GEMINI_API_KEY está vacío. Pega la key completa desde https://aistudio.google.com/apikey (botón 'Copiar clave')."
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

# 2) Elegir el modelo: buscamos uno que esté disponible en TU proyecto gratuito y que respete `temperature`
#    (los modelos Gemini 3.6+ y 4 la ignoran, por eso preferimos Flash-Lite 3.5 o 2.5)
from google import genai
client = genai.Client()
PREFERIDOS = ["gemini-3.5-flash-lite", "gemini-2.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-3.8-flash"]
disponibles = []
for m in client.models.list():
    acciones = getattr(m, "supported_actions", None) or []
    if not acciones or "generateContent" in acciones:
        disponibles.append(m.name.replace("models/", ""))
MODEL = next((p for p in PREFERIDOS if p in disponibles), None)
if MODEL is None:
    print("Ninguno de los modelos preferidos está disponible. Modelos de tu proyecto:", disponibles[:30])
    MODEL = next((d for d in disponibles if "flash" in d), disponibles[0])
print("Modelo elegido:", MODEL)

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

print("Listo. Modelo:", MODEL)
