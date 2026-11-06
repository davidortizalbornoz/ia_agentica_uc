"""Modelo FALSO para probar el loop sin llamadas reales (ni key).

`fake_generar` imita lo que devuelve `cliente.generar`: un objeto con `.text`, `.function_calls`,
`.candidates[0].content`, `.usage_metadata` y `.parsed`. Decide con reglas simples:
- si la última parte del historial es del usuario y menciona a una persona, pide `buscar_colaborador`;
- si acaba de recibir el resultado de una tool, encadena otra (si está declarada) o responde con texto;
- si una tool devolvió {"error": ...}, lo explica y deriva a Personas.

No es un modelo de lenguaje: sirve para verificar que TU loop ejecuta tools, devuelve resultados y termina.
El comportamiento real del agente se evalúa con `run_eval.py` sin `--mock`.
"""
import json
import re
from types import SimpleNamespace

from google.genai import types

NOMBRES = ["camila", "rodrigo", "valentina", "matías", "matias", "daniela", "felipe", "josefa", "andrés", "andres",
           "rojas", "fuentes", "pérez", "perez", "soto", "herrera", "araya", "muñoz", "castillo", "vidal"]


def _respuesta(texto=None, llamadas=None, parsed=None):
    llamadas = llamadas or []
    partes = [types.Part(text=texto)] if texto else [types.Part(function_call=fc) for fc in llamadas]
    return SimpleNamespace(
        text=texto, function_calls=llamadas, parsed=parsed,
        candidates=[SimpleNamespace(content=types.Content(role="model", parts=partes))],
        usage_metadata=SimpleNamespace(prompt_token_count=100, candidates_token_count=20, total_token_count=120),
    )


def _declaradas(config):
    nombres = []
    for t in config.get("tools") or []:
        for d in getattr(t, "function_declarations", None) or []:
            nombres.append(d.name)
    return nombres


def _ya_llamada(contents, nombre):
    for c in contents:
        for p in c.parts or []:
            if p.function_call is not None and p.function_call.name == nombre:
                return True
    return False


def fake_generar(contents, **config):
    # --- salida estructurada (resumir): contents es un string y hay response_schema ---
    if isinstance(contents, str):
        esquema = config.get("response_schema")
        if esquema is not None:
            datos = {"tema": "vacaciones", "colaborador_id": None, "respuesta_breve": "Resumen simulado.",
                     "requiere_accion_humana": False, "motivo_derivacion": None, "tools_usadas": []}
            try:
                parsed = esquema.model_validate(datos)
            except Exception:  # noqa: BLE001  (el alumno cambió los campos: devolvemos JSON crudo)
                parsed = None
            return _respuesta(json.dumps(datos, ensure_ascii=False), parsed=parsed)
        return _respuesta("OK")

    declaradas = _declaradas(config)
    pregunta = (contents[0].parts[0].text or "")
    # la línea "[Consulta de: ...]" trae el nombre del consultante: no la usamos para detectar a terceros
    preg = (pregunta.split("\n", 1)[1] if pregunta.startswith("[Consulta de:") and "\n" in pregunta else pregunta).lower()
    ultimo = contents[-1]
    consultante = re.search(r"\[Consulta de: (C-\d{3})", pregunta)
    consultante = consultante.group(1) if consultante else None

    # --- turno del usuario: decidir la primera tool ---
    if ultimo.role != "tool":
        nombre = next((n for n in NOMBRES if n in preg), None)
        if nombre and "buscar_colaborador" in declaradas:
            return _respuesta(llamadas=[types.FunctionCall(name="buscar_colaborador", args={"nombre_o_id": nombre})])
        if consultante and ("me quedan" in preg or "mis " in preg or "mi " in preg):
            if "saldo_vacaciones" in declaradas and "vacacion" in preg:
                return _respuesta(llamadas=[types.FunctionCall(name="saldo_vacaciones", args={"colaborador_id": consultante})])
            if "estado_solicitudes" in declaradas and "solicitud" in preg:
                return _respuesta(llamadas=[types.FunctionCall(name="estado_solicitudes", args={"colaborador_id": consultante})])
            return _respuesta(llamadas=[types.FunctionCall(name="buscar_colaborador", args={"nombre_o_id": consultante})])
        if "buscar_politica" in declaradas and any(k in preg for k in ("política", "politica", "regla", "plazo", "anticipación")):
            return _respuesta(llamadas=[types.FunctionCall(name="buscar_politica", args={"tema": pregunta[-60:]})])
        return _respuesta("Necesito más información: ¿de qué colaborador o tema se trata?")

    # --- turno de tool: leer el resultado y decidir ---
    fr = ultimo.parts[0].function_response
    res = (fr.response or {}).get("resultado", fr.response)
    if isinstance(res, dict) and "error" in res:
        return _respuesta(f"No pude obtener el dato ({res['error']}). Te sugiero escribir a Personas (personas@lumenretail.example).")
    if fr.name == "buscar_colaborador":
        coincidencias = res.get("coincidencias", []) if isinstance(res, dict) else []
        if len(coincidencias) > 1:
            nombres = " o ".join(c["nombre"] for c in coincidencias)
            return _respuesta(f"Encontré más de una persona: ¿te refieres a {nombres}?")
        if coincidencias:
            c = coincidencias[0]
            if "solicitud" in preg and "estado_solicitudes" in declaradas and not _ya_llamada(contents, "estado_solicitudes"):
                return _respuesta(llamadas=[types.FunctionCall(name="estado_solicitudes", args={"colaborador_id": c["id"]})])
            if "vacacion" in preg and "saldo_vacaciones" in declaradas and not _ya_llamada(contents, "saldo_vacaciones"):
                return _respuesta(llamadas=[types.FunctionCall(name="saldo_vacaciones", args={"colaborador_id": c["id"]})])
            return _respuesta(f"Encontré a {c['nombre']} ({c['id']}), {c['cargo']} del área {c['area']}.")
    return _respuesta(f"Según el registro de Personas ({fr.name}): {json.dumps(res, ensure_ascii=False)[:200]}")
