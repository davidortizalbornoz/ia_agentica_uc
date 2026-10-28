import sys
import textwrap
from pathlib import Path

import pandas as pd

_parte_guiada = Path(__file__).resolve().parents[1] / "parte_guiada"
sys.path.insert(0, str(_parte_guiada))

from common import MODEL as modelo, generar

prompt = "Solo me darás un breve consejo para incorporar hábitos de lectura a mi rutina diaria"
filas = []
for temp in [0.0, 0.7, 1.0]:
    respuesta = generar(prompt, temperature=temp, max_output_tokens=200)
    u = respuesta.usage_metadata
    texto = respuesta.text
    if u is None or texto is None:
        raise SystemExit("La respuesta del modelo llegó sin texto o sin datos de uso.")
    tokens_salida = (u.candidates_token_count or 0) + (u.thoughts_token_count or 0)
    filas.append({
        "temperature": temp,
        "respuesta": texto.strip(),
        "tokens_salida": tokens_salida,
    })

tabla = pd.DataFrame(filas)

def imprimir_tabla(df):
    ancho_respuesta = 68
    columnas = (
        ("temperature", 11),
        ("tokens_salida", 14),
        ("respuesta", ancho_respuesta),
    )
    linea = "+" + "+".join("-" * (ancho + 2) for _, ancho in columnas) + "+"

    def fila(valores):
        celdas = []
        for (nombre, ancho), valor in zip(columnas, valores):
            celdas.append(f" {str(valor):<{ancho}} ")
        return "|" + "|".join(celdas) + "|"

    print(linea)
    print(fila(nombre for nombre, _ in columnas))
    print(linea)
    for _, registro in df.iterrows():
        respuesta = textwrap.wrap(str(registro["respuesta"]), ancho_respuesta) or [""]
        for i, linea_respuesta in enumerate(respuesta):
            print(fila((
                f"{registro['temperature']:.1f}" if i == 0 else "",
                registro["tokens_salida"] if i == 0 else "",
                linea_respuesta,
            )))
        print(linea)

print(f"Modelo: {modelo}")
print(f"Prompt: {prompt}\n")
imprimir_tabla(tabla)
