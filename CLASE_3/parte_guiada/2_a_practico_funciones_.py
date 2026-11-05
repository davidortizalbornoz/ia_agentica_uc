import json
import time
from pathlib import Path

from google.genai import types

# Los JSON los escribe 1_practico_datos_andina_cargo.py en esta misma carpeta.
DATA = Path(__file__).resolve().parent / "data"


# --- 1) Las funciones Python: código normal, sin nada de IA. Devuelven dict (o {"error": ...}) ---
def buscar_pedido(id_pedido: str) -> dict:
    """Devuelve el pedido con ese id: estado, cliente, ciudad, items, fecha de despacho y ETA en días."""
    try:
        with (DATA / "pedidos.json").open("r", encoding="utf-8") as f:
            pedidos_db = json.load(f)
    except Exception as e:
        return {"error": f"Error al leer la base de datos de pedidos: {str(e)}"}

    p = next((p for p in pedidos_db if p["id"] == id_pedido.upper().strip()), None)
    return p if p else {"error": f"No existe el pedido {id_pedido}"}

def consultar_stock(sku: str) -> dict:
    """Devuelve nombre, unidades disponibles y bodega de un SKU."""
    try:
        with (DATA / "stock.json").open("r", encoding="utf-8") as f:
            stock_db = json.load(f)
    except Exception as e:
        return {"error": f"Error al leer el inventario: {str(e)}"}

    s = stock_db.get(sku.upper().strip())
    return {"sku": sku.upper().strip(), **s} if s else {"error": f"SKU {sku} no encontrado"}

def estimar_despacho(ciudad: str) -> dict:
    """Días hábiles estimados de despacho a una ciudad chilena."""
    try:
        with (DATA / "dias_despacho.json").open("r", encoding="utf-8") as f:
            despachos_db = json.load(f)
    except Exception as e:
        return {"error": f"Error al leer la tabla de despachos: {str(e)}"}

    dias = despachos_db.get(ciudad.strip().title())
    if dias is None:
        return {"error": f"Sin cobertura registrada para {ciudad}", "ciudades_con_cobertura": list(despachos_db)}
    return {"ciudad": ciudad.strip().title(), "dias_habiles": dias}

if __name__ == "__main__":
    print("Buscar Pedido ID: P-1004")
    print(buscar_pedido("P-1004"))
    print()

    print("Consultar Stock para Producto SKU: CAJ-050")
    print(consultar_stock("CAJ-050"))
    print()

    print("Estimar Despacho para Temuco")
    print(estimar_despacho("Temuco"))
    print()
