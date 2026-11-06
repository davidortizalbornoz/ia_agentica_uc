"""Núcleo de la Tarea 1: el system prompt, el loop agéntico y la salida estructurada.

Completa los TODO. La llamada al modelo ya está escrita; es el mismo patrón de `agente_manual` del Práctico 3.
`tests/test_loop.py` prueba el loop con un modelo falso (sin gastar llamadas ni necesitar key).
"""
import json
import time
from typing import Optional

from google.genai import types
from pydantic import BaseModel

import cliente
from cliente import costo_usd, log
from tools import REGISTRO, TOOLS

PAUSA = 1.0       # segundos entre vueltas del loop (límite por minuto del nivel gratuito)
MAX_ITER = 6      # tope de vueltas: cada vuelta es una llamada al modelo


# ---------------------------------------------------------------------------
# TODO 1 · System prompt (requisito 1)
# Debe definir: rol, a quién atiende, cómo usar la línea "[Consulta de: ...]" que antecede cada pregunta,
# reglas (no inventar datos, pedir aclaración si falta información, qué hacer ante errores de tools,
# privacidad según POL-07) y formato de respuesta.
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """TODO: escribe aquí el system prompt del asistente de Personas de Lumen Retail."""


# ---------------------------------------------------------------------------
# TODO 5 · Salida estructurada (requisito 4): ajusta los campos si lo necesitas
# ---------------------------------------------------------------------------
class ResumenConsulta(BaseModel):
    """Salida estructurada de cada consulta: lo que registraría el sistema de tickets de Personas."""
    tema: str                              # vacaciones | permisos | licencias | teletrabajo | jornada | beneficios | politicas | otro
    colaborador_id: Optional[str] = None   # a quién se refiere la consulta, si se identificó
    respuesta_breve: str                   # máximo 2 frases
    requiere_accion_humana: bool           # True si hay que derivar a Personas o a una jefatura
    motivo_derivacion: Optional[str] = None
    tools_usadas: list[str]


def _texto_usuario(pregunta: str, usuario: Optional[str]) -> str:
    """Antepone a la pregunta quién la hace, para que el modelo pueda resolver "mis vacaciones" y aplicar privacidad."""
    if not usuario:
        return pregunta
    res = REGISTRO["buscar_colaborador"](usuario)
    c = res.get("coincidencias", [{}])[0]
    etiqueta = f"{c.get('id', usuario)} {c.get('nombre', '')}, {c.get('cargo', '')}".strip(", ")
    return f"[Consulta de: {etiqueta}]\n{pregunta}"


def ejecutar(pregunta: str, usuario: Optional[str] = None, max_iter: int = MAX_ITER, verbose: bool = True) -> dict:
    """Corre el loop agéntico y devuelve un dict con respuesta, traza, uso y si se cortó por límite.

    Usa `_resultado(texto, traza, uso, cortado)` para construir lo que devuelves.
    `traza` es una lista de dicts {"paso", "tool", "args", "resultado"}: run_eval.py y los tests la leen.
    """
    contenido = [types.Content(role="user", parts=[types.Part(text=_texto_usuario(pregunta, usuario))])]
    traza, uso = [], []
    log.info("pregunta | usuario=%s | %s", usuario, pregunta)
    for paso in range(1, max_iter + 1):
        r = cliente.generar(contenido, system_instruction=SYSTEM_PROMPT, tools=TOOLS, temperature=0,
                            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))
        uso.append(r.usage_metadata)
        contenido.append(r.candidates[0].content)          # el turno del modelo (texto o pedido de tools)

        # TODO 2 · Si el modelo no pidió ninguna tool (r.function_calls vacío), es la respuesta final:
        #          return _resultado(r.text or "", traza, uso, cortado=False)

        # TODO 3 · Para cada `call` en r.function_calls:
        #          - ejecutar REGISTRO[call.name](**dict(call.args or {})) dentro de un try/except;
        #            si falla (o la tool no existe), el resultado debe ser {"error": "..."} (requisito 2: manejo de errores);
        #          - agregar a `traza` el dict {"paso", "tool", "args", "resultado"} y registrar en `log`;
        #          - construir types.Part.from_function_response(name=call.name, response={"resultado": resultado}).
        #          Luego agregar a `contenido` un types.Content(role="tool", parts=[...]) con todas las partes
        #          y dormir PAUSA segundos antes de la siguiente vuelta.
        raise NotImplementedError("TODO: completa el loop agéntico en agent.py")

    # TODO 4 · Se agotó max_iter sin respuesta final: devuelve una respuesta controlada (no un estado intermedio)
    #          con cortado=True. Piensa qué debería decirle el asistente al usuario en ese caso.
    log.warning("límite de iteraciones alcanzado")
    return _resultado("TODO: respuesta controlada cuando se agota el límite", traza, uso, cortado=True)


def _resultado(texto, traza, uso, cortado):
    entrada = sum((getattr(u, "prompt_token_count", 0) or 0) for u in uso)
    salida = sum((getattr(u, "candidates_token_count", 0) or 0) for u in uso)
    return {"respuesta": texto, "traza": traza, "tools_usadas": [t["tool"] for t in traza],
            "llamadas": len(uso), "tokens_entrada": entrada, "tokens_salida": salida,
            "costo_usd": round(costo_usd(entrada, salida), 6), "cortado": cortado}


def resumir(pregunta: str, resultado: dict) -> ResumenConsulta:
    """Pide al modelo un ResumenConsulta validado (salida estructurada, requisito 4).

    TODO 5 · Construye un prompt con la pregunta, la respuesta y las tools usadas, y llama a
    cliente.generar(prompt, system_instruction=..., temperature=0,
                    response_mime_type="application/json", response_schema=ResumenConsulta)
    Devuelve r.parsed (o ResumenConsulta.model_validate_json(r.text) si parsed viene vacío), como en el Práctico 2.
    """
    raise NotImplementedError("TODO: resumir")
