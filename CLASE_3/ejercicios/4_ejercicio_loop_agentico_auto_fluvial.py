import importlib.util
import sys
from pathlib import Path

from google.genai import types

# client y MODEL viven en la parte guiada de la clase 1 y leen la API key desde el .env.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "CLASE_1" / "parte_guiada"))
from common import MODEL, client, costo_usd

# Las búsquedas fluviales viven en 4_ejercicio_funciones.py.
# El SDK arma la declaración a partir del type hint y del docstring: no hace falta FunctionDeclaration.
_spec = importlib.util.spec_from_file_location(
    "ejercicio_funciones_fluviales",
    Path(__file__).with_name("4_ejercicio_funciones.py"),
)
_loader = _spec.loader if _spec is not None else None
if _spec is None or _loader is None:
    raise SystemExit("No se encontró 4_ejercicio_funciones.py")
_funciones = importlib.util.module_from_spec(_spec)
_loader.exec_module(_funciones)
buscar_rios_por_ciudad = _funciones.buscar_rios_por_ciudad
buscar_rios_por_nombre = _funciones.buscar_rios_por_nombre
buscar_ciudad_por_id = _funciones.buscar_ciudad_por_id
buscar_ciudad_por_region = _funciones.buscar_ciudad_por_region
buscar_ciudad_por_nombre = _funciones.buscar_ciudad_por_nombre
buscar_punto_por_id = _funciones.buscar_punto_por_id
buscar_punto_por_ciudad = _funciones.buscar_punto_por_ciudad

TOOLS = [
    buscar_rios_por_ciudad,
    buscar_rios_por_nombre,
    buscar_ciudad_por_id,
    buscar_ciudad_por_region,
    buscar_ciudad_por_nombre,
    buscar_punto_por_id,
    buscar_punto_por_ciudad,
]

INSTRUCCIONES = """Eres el asistente de una base de datos fluvial de Chile.
Respondes consultas sobre ríos, ciudades y puntos fluviales.

Reglas:
- Usa SIEMPRE las herramientas para obtener datos; nunca inventes ids, nombres ni milímetros.
- Si falta información para buscar, pídela antes de responder.
- Si una herramienta devuelve un error o una lista vacía, explícalo con claridad.
- Responde en español, en máximo 4 líneas, con tono profesional y directo.
"""

USO = []   # usage_metadata que devuelve cada send_message


def trazar(mensaje, verbose):
    """Escribe una línea de la traza. Con verbose=False el loop no imprime nada."""
    if verbose:
        print(mensaje)


def trazar_historial(historial, verbose):
    """Imprime la secuencia que armó el SDK: pregunta, pedido de tool, resultado y respuesta."""
    if not verbose:
        return
    for turno in historial or []:
        for parte in (turno.parts or []):
            if parte.function_call:
                argumentos = parte.function_call.args
                args = dict(argumentos) if argumentos is not None else {}
                print(f"[{turno.role}] pide {parte.function_call.name}({args})")
            elif parte.function_response:
                print(f"[{turno.role}] resultado -> {parte.function_response.response}")
            elif parte.text:
                print(f"[{turno.role}] {parte.text}")


def agente_automatico(pregunta, verbose=True, tools=None):
    """El SDK hace el loop: decide, ejecuta las funciones Python y repite hasta la respuesta final."""
    # None significa "usa las búsquedas fluviales". Pasarlas como funciones,
    # no como FunctionDeclaration: el SDK genera el contrato solo.
    if tools is None:
        tools = TOOLS

    trazar(f"Pregunta: {pregunta}", verbose)
    trazar(f"Tools: {[funcion.__name__ for funcion in tools]}", verbose)
    trazar("", verbose)

    # La conversación vive en el chat. generate_content con function calling
    # automático avisa que conviene esta API: el historial y las tools quedan acá.
    config_chat = types.GenerateContentConfig(
        system_instruction=INSTRUCCIONES,
        temperature=0,
        tools=tools,
    )
    chat = client.chats.create(model=MODEL, config=config_chat)
    respuesta = chat.send_message(pregunta)
    if respuesta.usage_metadata:
        USO.append(respuesta.usage_metadata)

    trazar(f"Respuesta: {respuesta.text}", verbose)
    trazar("", verbose)
    # Con chats.create esa secuencia está en el historial del chat.
    # send_message desactiva el loop interno de generate_content, así que
    # automatic_function_calling_history llega vacío.
    trazar("Historial automático:", verbose)
    trazar_historial(chat.get_history(), verbose)
    return respuesta.text


if __name__ == "__main__":
    #agente_automatico("¿Qué ríos hay en Temuco")
    #agente_automatico("¿Qué ríos hay en la región de la Araucanía?")
    #agente_automatico("¿Cuantos mm (milimetros) totales de agua caída se acumularían si llueve durante 5 días seguidos en la región de la Araucanía?")

    agente_automatico("Supongamos en que la región de la Araucanía llueve durante 5 días seguidos... ¿Que rios estarían estarían en riesgo de desborde (sobre 60 mm es considerado riesgoso)")
    # send_message informa el usage de la respuesta final. Las vueltas
    # intermedias las resuelve el SDK dentro de esa misma llamada.
    entrada = sum((u.prompt_token_count or 0) for u in USO)
    salida = sum((u.candidates_token_count or 0) for u in USO)
    print(f"{len(USO)} respuesta(s) de send_message | tokens entrada: {entrada} | salida: {salida} | costo ≈ US${costo_usd(entrada, salida):.5f}")
