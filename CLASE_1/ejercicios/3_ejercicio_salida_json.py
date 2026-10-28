import json
import sys
from pathlib import Path

_parte_guiada = Path(__file__).resolve().parents[1] / "parte_guiada"
sys.path.insert(0, str(_parte_guiada))

from common import MODEL, generar

frases = ["Necesito 40 cajas de cartón para Valparaíso",
          "Mándame guantes a Antofagasta",
          "Incorporar un par de promotores de preservativos en la ciudad de Santiago"]

instruccion = (
    "Extrae de la frase del usuario solo estos campos: producto, cantidad y ciudad. "
    "Responde únicamente con un objeto JSON con esas tres claves. "
    "Si la frase no permite determinar un campo, su valor es null. "
    "No inventes datos. cantidad es un número entero o null."
)

def extraer(frase):
    respuesta = generar(
        frase,
        model=MODEL,
        system_instruction=instruccion,
        temperature=0.0,
        max_output_tokens=200,
        response_mime_type="application/json",
    )
    texto = respuesta.text
    if texto is None:
        raise SystemExit(f"La respuesta para {frase!r} llegó sin texto.")
    datos = json.loads(texto)
    if not isinstance(datos, dict):
        raise SystemExit(f"La respuesta no es un objeto JSON: {texto}")
    for clave in ("producto", "cantidad", "ciudad"):
        if clave not in datos or datos[clave] in ("", "null"):
            datos[clave] = None
    return {clave: datos[clave] for clave in ("producto", "cantidad", "ciudad")}

print("\nEJERCICIO 3. SALIDA EN JSON")
print("______________________________________________\n")
print("Modelo:", MODEL)
print()

for frase in frases:
    datos = extraer(frase)
    print("Frase:", frase)
    print(json.dumps(datos, ensure_ascii=False, indent=2))
    print()
