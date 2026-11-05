import json
from datetime import datetime, timedelta
from pathlib import Path

# Mismo JSON que lee buscar_pedido en parte_guiada/2_a_practico_funciones_.py.
DATA = Path(__file__).resolve().parent.parent / "parte_guiada" / "data"


def fecha_estimada_entrega(id_pedido: str) -> dict:
    """Calcula la fecha estimada de entrega de un pedido específico.

    Lee ``pedidos.json``, el mismo archivo que usa ``buscar_pedido``. Si el
    pedido ya fue despachado, suma ``eta_dias`` (días corridos) a
    ``fecha_despacho`` y devuelve esa fecha en formato ``YYYY-MM-DD``. Si
    ``fecha_despacho`` es nula, el pedido todavía no salió de bodega: no hay
    fecha que calcular y la respuesta trae un mensaje que lo dice.

    Args:
        id_pedido: Identificador del pedido, por ejemplo ``"P-1001"``.
            Se normaliza a mayúsculas y sin espacios alrededor.

    Returns:
        Un diccionario. Con despacho registrado::

            {
                "id": "P-1001",
                "fecha_despacho": "2026-10-15",
                "eta_dias": 2,
                "fecha_estimada_entrega": "2026-10-17",
            }

        Si el pedido existe pero aún no fue despachado::

            {
                "id": "P-1003",
                "estado": "preparacion",
                "mensaje": "El pedido P-1003 aún no fue despachado ...",
            }

        Si el id no existe, falta ``eta_dias`` o no se puede leer el JSON,
        devuelve ``{"error": "..."}``.
    """
    try:
        with (DATA / "pedidos.json").open("r", encoding="utf-8") as f:
            pedidos_db = json.load(f)
    except Exception as e:
        return {"error": f"Error al leer la base de datos de pedidos: {str(e)}"}

    pedido = next((p for p in pedidos_db if p["id"] == id_pedido.upper().strip()), None)
    if pedido is None:
        return {"error": f"No existe el pedido {id_pedido}"}

    fecha_despacho = pedido.get("fecha_despacho")
    if not fecha_despacho:
        estado = pedido.get("estado", "sin estado")
        return {
            "id": pedido["id"],
            "estado": estado,
            "mensaje": (
                f"El pedido {pedido['id']} aún no fue despachado "
                f"(estado: {estado}). No hay fecha estimada de entrega."
            ),
        }

    eta_dias = pedido.get("eta_dias")
    if eta_dias is None:
        return {"error": f"El pedido {pedido['id']} no tiene eta_dias."}

    try:
        fecha = datetime.strptime(fecha_despacho, "%Y-%m-%d").date()
        eta = int(eta_dias)
    except (TypeError, ValueError) as e:
        return {"error": f"No se pudo calcular la entrega de {pedido['id']}: {e}"}

    estimada = fecha + timedelta(days=eta)
    return {
        "id": pedido["id"],
        "fecha_despacho": fecha_despacho,
        "eta_dias": eta,
        "fecha_estimada_entrega": estimada.isoformat(),
    }


if __name__ == "__main__":
    print("Fecha estimada de entrega para P-1001 (despachado)")
    print(fecha_estimada_entrega("P-1001"))
    print()

    print("Fecha estimada de entrega para P-1003 (aún no despachado)")
    print(fecha_estimada_entrega("P-1003"))
    print()

    print("Fecha estimada de entrega para P-9999 (no existe)")
    print(fecha_estimada_entrega("P-9999"))
    print()
