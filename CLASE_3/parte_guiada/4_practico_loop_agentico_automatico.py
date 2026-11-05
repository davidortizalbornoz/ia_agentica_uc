import importlib.util
import sys
from pathlib import Path

from google.genai import types

# client y MODEL viven en la parte guiada de la clase 1 y leen la API key desde el .env.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "CLASE_1" / "parte_guiada"))
from common import MODEL, client, costo_usd

# Las tres funciones viven en el script de la parte guiada 2.
# El SDK arma la declaración a partir del type hint y del docstring: no hace falta FunctionDeclaration.
_spec = importlib.util.spec_from_file_location(
    "practico_funciones",
    Path(__file__).with_name("2_a_practico_funciones_.py"),
)
_loader = _spec.loader if _spec is not None else None
if _spec is None or _loader is None:
    raise SystemExit("No se encontró 2_a_practico_funciones_.py")
_funciones = importlib.util.module_from_spec(_spec)
_loader.exec_module(_funciones)
buscar_pedido = _funciones.buscar_pedido
consultar_stock = _funciones.consultar_stock
estimar_despacho = _funciones.estimar_despacho

INSTRUCCIONES = """Eres el asistente interno de Andina Cargo, una empresa de logística chilena.
Respondes consultas de ejecutivos de atención a clientes sobre pedidos, stock y tiempos de despacho.

Reglas:
- Usa SIEMPRE las herramientas para obtener datos; nunca inventes ids, estados ni cantidades.
- Si falta información (por ejemplo, el id del pedido), pídela antes de responder.
- Si una herramienta devuelve un error, explícalo con claridad y propone qué hacer.
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
    # None significa "usa las tres funciones de 2_a". Pasarlas como funciones,
    # no como FunctionDeclaration: el SDK genera el contrato solo.
    if tools is None:
        tools = [buscar_pedido, consultar_stock, estimar_despacho]

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
    agente_automatico("¿Cuándo le llega a Clínica Norte su pedido P-1003?")

    # send_message informa el usage de la respuesta final. Las vueltas
    # intermedias las resuelve el SDK dentro de esa misma llamada.
    entrada = sum((u.prompt_token_count or 0) for u in USO)
    salida = sum((u.candidates_token_count or 0) for u in USO)
    print(f"{len(USO)} respuesta(s) de send_message | tokens entrada: {entrada} | salida: {salida} | costo ≈ US${costo_usd(entrada, salida):.5f}")
