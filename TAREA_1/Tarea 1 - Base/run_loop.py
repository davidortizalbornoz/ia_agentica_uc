"""Corre una consulta de ejemplo contra el agente.

No es un test: llama a agent.ejecutar con el modelo real y muestra la respuesta.
"""
import json
import os
import pathlib
import sys

_DIR = pathlib.Path(__file__).resolve().parent
os.chdir(_DIR)
sys.path.insert(0, str(_DIR))

import agent

pregunta = "¿Cuántos días de vacaciones le quedan a Rodrigo Fuentes?"
r = agent.ejecutar(
    pregunta,
    usuario="C-006",
    verbose=True,
)
resumen = agent.resumir(pregunta, r)


print(r["respuesta"])
print()
print(resumen.model_dump_json(indent=2, ensure_ascii=False))
print()
"""
print(json.dumps(
    {
        "tools_usadas": r["tools_usadas"],
        "llamadas": r["llamadas"],
        "tokens_entrada": r["tokens_entrada"],
        "tokens_salida": r["tokens_salida"],
        "costo_usd": r["costo_usd"],
        "cortado": r["cortado"],
    },
    ensure_ascii=False,
    indent=2,
))
"""