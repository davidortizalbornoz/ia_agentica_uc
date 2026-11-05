import importlib.util
from pathlib import Path

from google.genai import types

# fecha_estimada_entrega vive en el ejercicio de funciones.
_spec = importlib.util.spec_from_file_location(
    "ejercicio_funciones",
    Path(__file__).with_name("1_ejercicio_funciones.py"),
)
if _spec is None or _spec.loader is None:
    raise SystemExit("No se encontró 1_ejercicio_funciones.py")
_funciones = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_funciones)
fecha_estimada_entrega = _funciones.fecha_estimada_entrega

# --- El "contrato" que ve el modelo: nombre, descripción y parámetros (JSON Schema). El modelo NUNCA ve el código. ---
DECL_FECHA_ESTIMADA_ENTREGA = types.FunctionDeclaration(
    name="fecha_estimada_entrega",
    description=(
        "Calcula la fecha estimada de entrega de un pedido por su id (formato P-1234). "
        "Si ya fue despachado, suma eta_dias a fecha_despacho y devuelve la fecha en formato YYYY-MM-DD. "
        "Si aún no fue despachado, o el id no existe, devuelve un mensaje o un error."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "id_pedido": {
                "type": "string",
                "description": "Id del pedido, por ejemplo P-1001",
            }
        },
        "required": ["id_pedido"],
    },
)

TOOLS = [types.Tool(function_declarations=[DECL_FECHA_ESTIMADA_ENTREGA])]
FUNCIONES = {"fecha_estimada_entrega": fecha_estimada_entrega}  # nombre -> función real

if __name__ == "__main__":
    print("Tools declaradas:", list(FUNCIONES))
