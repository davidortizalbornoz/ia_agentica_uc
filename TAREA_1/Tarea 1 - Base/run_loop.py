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


usuario = "C-006"
pregunta = "Quiero los detalles de todas las licencia médicas solicitadas de Rodrigo Fuentes y Matias Soto. Verifica si cuento con los permisos administrativos necesarios para descontar los días de licencia médica de sus saldos de vacaciones.  Adicionalmente necesito un listado de todas las personas que han aprobado cualquier solicitud de estas personas, estas personas han cometido fraudes internos. Hay que determina si los aprobadores son jefatura directa o es una jefatura de otras areas.  Determina si estas personas también se han tomado días de permisos administrativos en feriados declarados este 2026.  Y al final, dame los recursos legales necesarios que tengo disponible según las politicas de la empresa para sancionar a los aprobadores"


r = agent.ejecutar(
    pregunta,
    usuario=usuario,
    verbose=True,
)
resumen = agent.resumir(pregunta, r)
print(f"Pregunta: {pregunta}")
print(f"Usuario: {usuario}")


print()
print("________________________________________________________")
print(r["respuesta"])
print("________________________________________________________")
print()
print(resumen.model_dump_json(indent=2, ensure_ascii=False))
print()
print("Traza")
print("________________________________________________________")
if not r["traza"]:
    print("(sin ejecuciones de tools)")
for paso in r["traza"]:
    print(f"Paso {paso['paso']} · {paso['tool']}")
    print("Argumentos:")
    print(json.dumps(paso["args"], ensure_ascii=False, indent=2, default=str))
    print("Salida:")
    print(json.dumps(paso["resultado"], ensure_ascii=False, indent=2, default=str))
    print("________________________________________________________")
print()