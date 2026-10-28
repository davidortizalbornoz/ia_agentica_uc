import sys
from pathlib import Path

from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "CLASE_1" / "parte_guiada"))
from common import MODEL, generar

datos_faltantes = [
    "Despacha 40 unidades del SKU CAJ-40 a Valparaíso",
    "Necesito 15 del SKU GUA-02",
    "Envía el SKU PAL-200 a Antofagasta",
    "Mándame 8 cajas a Santiago",
    "El código de producto es TNT-15",
    "Quince brochas para la capital de Chile",
    "Hola, quisiera hacer un pedido",
]

instruccion = (
    "Extrae de la frase del usuario solo estos campos: sku, cantidad y ciudad. "
    "Responde únicamente con un objeto JSON que cumpla el esquema Pedido. "
    "Si la frase no permite determinar un campo, su valor es null. "
    "No inventes datos. cantidad es un número entero o null. sku y ciudad son texto o null."
)

class Pedido(BaseModel):
    sku: str | None = None
    cantidad: int | None = None
    ciudad: str | None = None

def extraer(frase):
    respuesta = generar(
        frase,
        model=MODEL,
        system_instruction=instruccion,
        temperature=0.0,
        max_output_tokens=200,
        response_mime_type="application/json",
        response_schema=Pedido,
    )
    pedido = getattr(respuesta, "parsed", None)
    if pedido is None:
        texto = respuesta.text
        if texto is None:
            raise SystemExit(f"La respuesta para {frase!r} llegó sin texto.")
        pedido = Pedido.model_validate_json(texto)
    return pedido

if __name__ == "__main__":
    print("\nEJERCICIO 3. EXTRACCIÓN ESTRUCTURADA DE PEDIDOS")
    print("______________________________________________\n")
    print("Modelo:", MODEL)
    print()

    for frase in datos_faltantes:
        pedido = extraer(frase)
        print("Frase:", frase)
        print(pedido.model_dump_json(indent=2, ensure_ascii=False))
        print()

print("________________ CONCLUSION ______________________\n")
print("Los dos recursos devuelven JSON. El de la clase 1 pide texto JSON y lo convierte en un diccionario. El de la clase 2, además, le entrega al modelo el esquema Pedido y comprueba que la respuesta cumpla ese esquema.\n")