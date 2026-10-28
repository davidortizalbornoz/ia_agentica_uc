import importlib.util
import time
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

# El prompt v2, la pausa y los correos ya están en el script anterior.
_spec = importlib.util.spec_from_file_location(
    "versiones",
    Path(__file__).with_name("2_practico_3versionesde_systemprompt.py"),
)
if _spec is None or _spec.loader is None:
    raise SystemExit("No se encontró 2_practico_3versionesde_systemprompt.py")
_versiones = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_versiones)

generar = _versiones.generar
PROMPTS = _versiones.PROMPTS
PAUSA = _versiones.PAUSA
df = _versiones.df

class Clasificacion(BaseModel):
    categoria: Literal["facturacion", "tecnico", "reclamo", "otro"]
    urgencia: Literal["baja", "media", "alta"]
    resumen: str   # una frase

def generar_estructurado(contents, esquema, **config):
    """Pide al modelo una respuesta que cumpla el esquema Pydantic y devuelve el objeto validado."""
    r = generar(contents, response_mime_type="application/json", response_schema=esquema, **config)
    time.sleep(PAUSA)
    parsed = getattr(r, "parsed", None)
    if parsed is not None:
        return parsed
    texto = r.text
    if texto is None:
        raise SystemExit("La respuesta del modelo llegó sin texto.")
    return esquema.model_validate_json(texto)

def clasificar_estructurado(correo):
    return generar_estructurado(correo, Clasificacion, temperature=0,
        system_instruction=PROMPTS["v2_estructurado"] + "\nAdemás estima la urgencia y resume el correo en una frase.")

if __name__ == "__main__":
    for c in df["correo"][:3]:      # 3 llamadas individuales, una por correo
        print(clasificar_estructurado(c))

    cuarto = df["correo"].iloc[3]
    print()
    print("JSON DEL CUARTO CORREO")
    print(cuarto)
    print(clasificar_estructurado(cuarto).model_dump_json(indent=2, ensure_ascii=False))
