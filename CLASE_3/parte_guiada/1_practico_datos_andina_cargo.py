import json
from pathlib import Path

# Datos de ejemplo de Andina Cargo: pedidos, stock y días de despacho.
PEDIDOS = [
  {"id": "P-1001", "cliente": "Ferretería Lagos", "ciudad": "Valparaíso", "estado": "en_transito", "items": [{"sku": "TAL-200", "cant": 10}], "fecha_despacho": "2026-10-15", "eta_dias": 2},
  {"id": "P-1002", "cliente": "Minimarket Sol", "ciudad": "Santiago", "estado": "entregado", "items": [{"sku": "CAJ-050", "cant": 200}], "fecha_despacho": "2026-10-10", "eta_dias": 0},
  {"id": "P-1003", "cliente": "Clínica Norte", "ciudad": "Antofagasta", "estado": "preparacion", "items": [{"sku": "GUA-010", "cant": 50}, {"sku": "TAL-200", "cant": 5}], "fecha_despacho": None, "eta_dias": 4},
  {"id": "P-1004", "cliente": "Ferretería Lagos", "ciudad": "Valparaíso", "estado": "retrasado", "items": [{"sku": "CAJ-050", "cant": 40}], "fecha_despacho": "2026-10-12", "eta_dias": 3},
  {"id": "P-1005", "cliente": "Agro Sur", "ciudad": "Temuco", "estado": "en_transito", "items": [{"sku": "PAL-001", "cant": 12}], "fecha_despacho": "2026-10-16", "eta_dias": 3},
]
STOCK = {"TAL-200": {"nombre": "Taladro 200W", "stock": 35, "bodega": "Santiago"},
         "CAJ-050": {"nombre": "Caja cartón 50x50", "stock": 0, "bodega": "Santiago"},
         "GUA-010": {"nombre": "Guantes nitrilo (caja 100)", "stock": 120, "bodega": "Antofagasta"},
         "PAL-001": {"nombre": "Pallet madera", "stock": 8, "bodega": "Temuco"}}
DIAS_DESPACHO_ESTIMADOS = {"Santiago": 1, "Valparaíso": 2, "Temuco": 3, "Antofagasta": 4, "Punta Arenas": 7}

if __name__ == "__main__":
    data = Path(__file__).resolve().parent / "data"
    data.mkdir(exist_ok=True)
    with (data / "pedidos.json").open("w", encoding="utf-8") as f:
        json.dump(PEDIDOS, f, ensure_ascii=False, indent=2)
    with (data / "stock.json").open("w", encoding="utf-8") as f:
        json.dump(STOCK, f, ensure_ascii=False, indent=2)
    with (data / "dias_despacho.json").open("w", encoding="utf-8") as f:
        json.dump(DIAS_DESPACHO_ESTIMADOS, f, ensure_ascii=False, indent=2)
    print(f"{len(PEDIDOS)} pedidos, {len(STOCK)} SKUs y {len(DIAS_DESPACHO_ESTIMADOS)} lugares de despacho guardados en {data}/")
