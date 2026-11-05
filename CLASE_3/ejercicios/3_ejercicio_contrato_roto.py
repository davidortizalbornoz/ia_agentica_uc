import importlib.util
from pathlib import Path

from google.genai import types

# consultar_stock_roto vive en el ejercicio de la función rota.
_spec = importlib.util.spec_from_file_location(
    "ejercicio_funcion_rota",
    Path(__file__).with_name("3_ejercicio_funcion_rota.py"),
)
if _spec is None or _spec.loader is None:
    raise SystemExit("No se encontró 3_ejercicio_funcion_rota.py")
_funciones = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_funciones)
consultar_stock_roto = _funciones.consultar_stock_roto

# --- El "contrato" que ve el modelo: nombre, descripción y parámetros (JSON Schema). El modelo NUNCA ve el código. ---
DECL_CONSULTAR_STOCK_ROTO = types.FunctionDeclaration(
    name="consultar_stock_roto",
    description="Consulta las unidades disponibles de un producto por su SKU (formato ABC-123) y en qué bodega está.",
    parameters_json_schema={
        "type": "object",
        "properties": {"sku": {"type": "string", "description": "Código SKU, por ejemplo TAL-200"}},
        "required": ["sku"],
    },
)

TOOLS = [types.Tool(function_declarations=[DECL_CONSULTAR_STOCK_ROTO])]
FUNCIONES = {"consultar_stock_roto": consultar_stock_roto}  # nombre -> función real

if __name__ == "__main__":
    print("Tools declaradas:", list(FUNCIONES))
