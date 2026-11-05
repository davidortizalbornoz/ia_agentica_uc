import importlib.util
import json
import sys
import time
from pathlib import Path

from google.genai import types

# generar vive en la parte guiada de la clase 1 y lee la API key desde el .env.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "CLASE_1" / "parte_guiada"))
from common import costo_usd, generar

# FunctionDeclaration de buscar_pedido y consultar_stock.
_spec_guiada = importlib.util.spec_from_file_location(
    "practico_contratos",
    Path(__file__).resolve().parent.parent / "parte_guiada" / "2_b_practico_contratos.py",
)
_loader_guiada = _spec_guiada.loader if _spec_guiada is not None else None
if _spec_guiada is None or _loader_guiada is None:
    raise SystemExit("No se encontró 2_b_practico_contratos.py")
_contratos = importlib.util.module_from_spec(_spec_guiada)
_loader_guiada.exec_module(_contratos)

# FunctionDeclaration de fecha_estimada_entrega.
_spec_fecha = importlib.util.spec_from_file_location(
    "ejercicio_contrato",
    Path(__file__).with_name("1_ejercicio_contrato.py"),
)
_loader_fecha = _spec_fecha.loader if _spec_fecha is not None else None
if _spec_fecha is None or _loader_fecha is None:
    raise SystemExit("No se encontró 1_ejercicio_contrato.py")
_contrato_fecha = importlib.util.module_from_spec(_spec_fecha)
_loader_fecha.exec_module(_contrato_fecha)

# Las 3 funciones en un solo contrato: el modelo ve las declaraciones; Python ejecuta FUNCIONES.
TOOLS = [
    types.Tool(
        function_declarations=[
            _contratos.DECL_BUSCAR_PEDIDO,
            _contratos.DECL_CONSULTAR_STOCK,
            _contrato_fecha.DECL_FECHA_ESTIMADA_ENTREGA,
        ]
    )
]
FUNCIONES = {**_contratos.FUNCIONES, **_contrato_fecha.FUNCIONES}

PAUSA = 2.0   # segundos entre llamadas al modelo, para respetar el límite por minuto del nivel gratuito

INSTRUCCIONES = """Eres el asistente interno de Andina Cargo, una empresa de logística chilena.
Respondes consultas de ejecutivos de atención a clientes sobre pedidos, stock y tiempos de despacho.

Reglas:
- Usa SIEMPRE las herramientas para obtener datos; nunca inventes ids, estados ni cantidades.
- Si falta información (por ejemplo, el id del pedido), pídela antes de responder.
- Si una herramienta devuelve un error, explícalo con claridad y propone qué hacer.
- Responde en español, en máximo 4 líneas, con tono profesional y directo.
"""

USO = []   # acumulamos usage_metadata de cada llamada para medir cuánto cuesta un loop

def trazar(mensaje, verbose):
    """Escribe una línea de la traza. Con verbose=False el loop no imprime nada."""
    if verbose:
        print(mensaje)

def forma(objeto):
    """Dict legible de un objeto del SDK, sin campos vacíos ni bytes opacos."""
    if isinstance(objeto, list):
        return [forma(item) for item in objeto]
    if isinstance(objeto, bytes):
        return f"<bytes {len(objeto)}>"
    if hasattr(objeto, "model_dump"):
        return forma(objeto.model_dump(exclude_none=True))
    if isinstance(objeto, dict):
        return {clave: forma(valor) for clave, valor in objeto.items()}
    return objeto

def trazar_forma(titulo, objeto, verbose):
    """Imprime el contenido de un candidato, un turno, llamadas o partes."""
    if not verbose:
        return
    print(titulo)
    print(json.dumps(forma(objeto), ensure_ascii=False, indent=2, default=str))

def agente_manual(pregunta, max_iter=5, verbose=True, tools=None, funciones=None):
    """Loop agéntico mínimo: decidir -> actuar -> observar, hasta que haya respuesta final o se agote max_iter."""
    # None significa "usa el contrato unificado de las 3 funciones".
    if tools is None:
        tools = TOOLS
    if funciones is None:
        funciones = FUNCIONES

    trazar(f"Pregunta: {pregunta}", verbose)
    trazar(f"Interacciones máximas: {max_iter}", verbose)
    trazar_forma("Tools:", tools, verbose)
    trazar("", verbose)

    contenido = [
        types.Content(role="user", parts=[types.Part.from_text(text=pregunta)])
    ]
    for paso in range(1, max_iter + 1):
        trazar(f"--- Interacción {paso}/{max_iter} ---", verbose)
        trazar("Llamando al modelo con el historial acumulado.", verbose)

        respuesta = generar(
            contenido,
            system_instruction=INSTRUCCIONES,
            tools=tools,
            temperature=0,
            # El SDK no ejecuta las tools: las ejecutamos nosotros más abajo.
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        USO.append(respuesta.usage_metadata)

        # candidates y content vienen como opcionales en el SDK. En una respuesta
        # válida el primer candidato trae el turno: texto final o pedido de tool.
        candidatos = respuesta.candidates
        if not candidatos:
            raise SystemExit("El modelo no devolvió candidatos.")
        turno = candidatos[0].content
        if turno is None:
            raise SystemExit("El modelo no devolvió el turno de esta vuelta.")
        contenido.append(turno)

        # function_calls es None cuando el modelo ya respondió con texto.
        llamadas = respuesta.function_calls
        if not llamadas:
            trazar("partes: no se arman, porque no hubo llamadas.", verbose)
            trazar("El modelo respondió con texto y no pidió funciones.", verbose)
            trazar(f"Respuesta: {respuesta.text}", verbose)
            return respuesta.text

        # Puede pedir varias tools en la misma vuelta. Cada una se ejecuta acá,
        # en Python: el modelo solo envió el nombre y los argumentos.
        trazar(f"El modelo pidió {len(llamadas)} función(es).", verbose)
        partes = []
        for call in llamadas:
            nombre = call.name
            argumentos = call.args
            if nombre is None or argumentos is None:
                raise SystemExit("El modelo pidió una herramienta sin nombre o sin argumentos.")
            args = dict(argumentos)
            resultado = funciones[nombre](**args)
            trazar(f"  Función: {nombre}({args})", verbose)
            trazar(f"  Resultado: {resultado}", verbose)
            partes.append(
                types.Part.from_function_response(
                    name=nombre,
                    response={"resultado": resultado},
                )
            )
        # El resultado vuelve en un turno con role "user": así lo espera la API.
        contenido.append(types.Content(role="user", parts=partes))
        trazar(
            f"Resultados enviados al modelo. Pausa de {PAUSA} s antes de la siguiente interacción.",
            verbose,
        )
        trazar("", verbose)
        time.sleep(PAUSA)
    trazar(f"Límite de {max_iter} interacciones alcanzado, sin respuesta final.", verbose)
    return "Se alcanzó el límite de iteraciones sin respuesta final."

if __name__ == "__main__":
    agente_manual("Dame el día de la semana, de la fecha de entrega del pedido P-1001")

    # Cada vuelta reenvía todo el historial, así que el costo crece con los pasos.
    entrada = sum((u.prompt_token_count or 0) for u in USO)
    salida = sum((u.candidates_token_count or 0) for u in USO)
    print(f"{len(USO)} llamadas al modelo | tokens entrada: {entrada} | salida: {salida} | costo ≈ US${costo_usd(entrada, salida):.5f}")
