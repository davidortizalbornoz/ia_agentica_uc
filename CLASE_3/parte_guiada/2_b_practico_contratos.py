import importlib.util
from pathlib import Path

from google.genai import types

# buscar_pedido y consultar_stock viven en el script anterior.
_spec = importlib.util.spec_from_file_location(
    "practico_funciones",
    Path(__file__).with_name("2_a_practico_funciones_.py"),
)
if _spec is None or _spec.loader is None:
    raise SystemExit("No se encontró 2_a_practico_funciones_.py")
_funciones = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_funciones)
buscar_pedido = _funciones.buscar_pedido
consultar_stock = _funciones.consultar_stock

# --- 2) El "contrato" que ve el modelo: nombre, descripción y parámetros (JSON Schema). El modelo NUNCA ve el código. ---
DECL_BUSCAR_PEDIDO = types.FunctionDeclaration(
    name="buscar_pedido",
    description="Busca un pedido por su id (formato P-1234) y devuelve estado, cliente, ciudad, items, fecha de despacho y ETA en días.",
    parameters_json_schema={
        "type": "object",
        "properties": {"id_pedido": {"type": "string", "description": "Id del pedido, por ejemplo P-1001"}},
        "required": ["id_pedido"],
    },
)
DECL_CONSULTAR_STOCK = types.FunctionDeclaration(
    name="consultar_stock",
    description="Consulta las unidades disponibles de un producto por su SKU (formato ABC-123) y en qué bodega está.",
    parameters_json_schema={
        "type": "object",
        "properties": {"sku": {"type": "string", "description": "Código SKU, por ejemplo TAL-200"}},
        "required": ["sku"],
    },
)

TOOLS = [types.Tool(function_declarations=[DECL_BUSCAR_PEDIDO, DECL_CONSULTAR_STOCK])]
FUNCIONES = {"buscar_pedido": buscar_pedido, "consultar_stock": consultar_stock}   # nombre -> función real

if __name__ == "__main__":
    print("Tools declaradas:", list(FUNCIONES))
