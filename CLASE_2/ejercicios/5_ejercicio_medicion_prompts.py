import importlib.util
import sys
import time
from pathlib import Path

import pandas as pd
from pydantic import BaseModel

# generar vive en la parte guiada de la clase 1 y lee la API key desde el .env.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "CLASE_1" / "parte_guiada"))
from common import MODEL, generar

# Los tickets ya etiquetados están en el ejercicio 4 de esta clase.
_spec = importlib.util.spec_from_file_location(
    "casos_tickets_jira",
    Path(__file__).with_name("4_ejercicio_casos_tickets_jira.py"),
)
if _spec is None or _spec.loader is None:
    raise SystemExit("No se encontró 4_ejercicio_casos_tickets_jira.py")
_datos = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_datos)
df = _datos.df

# Las dos versiones comparten el texto. v3_con_ejemplos agrega reglas de ejemplo.
v2 = """Eres el clasificador de prioridades de la gerencia de recursos importantes y uso adecuado del tiempo.
Tarea: asignar solo una prioridad al ticket, estos están distribuidos por las siguientes categorías:
Categorías:
- desarrollo: cualquier evento relacionado al desarrollo y su ciclo de software.
- despliegue: cualquier evento relacionado las gestiones manuales y automáticas de despliegue de software en infraestructura cloud de la compañía.
- monitoreo: cualquier evento relacionado a los activos de software desplegados en ambientes productivos.
- otra: cualquier evento no relacionado a las categorias anteriores.
Prioridades:
- alta: cualquier evento que requiera suma importancia y afecte la continuidad operacional de la compañía.
- media: cualquier evento relacionado que no afecte la operación normal, ni cause daños operativos o comerciales.
- baja: cualquier evento que no sea importante y que puede solucionarse mas adelante en el corto plazo.
Responde SOLO con el nombre de la prioridad, en minúsculas, sin explicación."""

PROMPTS = {
    "v2_estructurado": v2,
    "v3_con_ejemplos": v2 + """

Ejemplos:
IF Ticket.idProject comienza con "Gerencia-P" -> priority = 'high'
IF Ticket.owner == "Ministro Quiroz" -> priority = 'low'
IF Ticket.assignedTo == "Ministro Eyzaguirre" -> priority = 'medium'
IF Ticket.details CONTAINS['css','estilo','margen','front','angular'] -> priority = 'medium'
IF Ticket.details CONTAINS['error','timeout','gateway','exception','stack trace'] -> priority = 'high'
IF Ticket.dateCreated > currentDate + 6 meses -> priority = 'high'""",
}

PAUSA = 2.0   # segundos entre llamadas, para respetar el límite por minuto del nivel gratuito

# La respuesta de cada llamada es una lista de {id, ticket, prioridad}, un elemento por ticket.
# prioridad es str: el modelo responde el nombre de una de las tres prioridades.
class Ticket(BaseModel):
    idTicket: str
    idProject: str
    owner: str
    assignedTo: str
    details: str
    dateCreated: str
    status: str

class Etiqueta(BaseModel):
    id: int
    ticket: Ticket
    prioridad: str

class Lote(BaseModel):
    resultados: list[Etiqueta]

def clasificar_lote(tickets, system_prompt):
    """Asigna la prioridad de todos los tickets en una sola llamada. Devuelve una prioridad por ticket, en el mismo orden."""
    lista = "\n".join(f"{i}. {c}" for i, c in enumerate(tickets))
    contenido = f"Asigna la prioridad de cada uno de los siguientes tickets, identificados por su número:\n\n{lista}"
    r = generar(contenido, system_instruction=system_prompt, temperature=0,
                response_mime_type="application/json", response_schema=Lote)
    time.sleep(PAUSA)
    lote = getattr(r, "parsed", None)
    if lote is None:
        texto = r.text
        if texto is None:
            raise SystemExit("La respuesta del modelo llegó sin texto.")
        lote = Lote.model_validate_json(texto)
    por_id = {e.id: e.prioridad.strip().lower().strip(".") for e in lote.resultados}
    return [por_id.get(i, "sin_respuesta") for i in range(len(tickets))]

CICLOS = 3          # aunque temperature=0, el modelo puede cambiar alguna prioridad; por eso repetimos
PREDICCIONES = {}   # nombre de la versión -> lista de predicciones de cada ciclo
CATEGORIAS = ("desarrollo", "despliegue", "monitoreo")

def medir(preds):
    """Aciertos de un ciclo: total y por categoría del ticket."""
    ok = pd.Series(preds) == df["prioridad"]
    medicion = {
        "aciertos": int(ok.sum()),
        "total": int(ok.shape[0]),
        "exactitud": float(ok.mean()),
    }
    for nombre in CATEGORIAS:
        parte = ok[df.categoria == nombre]
        medicion[f"{nombre}_ok"] = int(parte.sum())
        medicion[f"{nombre}_total"] = int(parte.shape[0])
    return medicion

def evaluar(system_prompt, nombre, ciclos=CICLOS):
    """Mide cuántos tickets coinciden con la prioridad esperada."""
    mediciones = []
    PREDICCIONES[nombre] = []
    for k in range(ciclos):
        print(f"Consultando {nombre}, ciclo {k + 1} de {ciclos}...")
        preds = clasificar_lote(list(df["contexto"]), system_prompt)
        PREDICCIONES[nombre].append(preds)
        mediciones.append(medir(preds))

    # El último ciclo queda en el dataframe para poder revisar ticket por ticket.
    df[nombre] = PREDICCIONES[nombre][-1]
    ultimo = mediciones[-1]
    exactitudes = [m["exactitud"] for m in mediciones]
    fila = {
        "version": nombre,
        "promedio": sum(exactitudes) / len(exactitudes),
        "minimo": min(exactitudes),
        "maximo": max(exactitudes),
        "ciclos": mediciones,
    }
    for categoria in CATEGORIAS:
        fila[f"{categoria}_ok"] = ultimo[f"{categoria}_ok"]
        fila[f"{categoria}_total"] = ultimo[f"{categoria}_total"]
    return fila

def imprimir_tabla(columnas, filas, izquierda=1):
    """Tabla de texto. `izquierda` indica cuántas columnas se alinean a la izquierda."""
    filas = list(filas)
    anchos = [len(columna) for columna in columnas]
    for fila in filas:
        for i, celda in enumerate(fila):
            anchos[i] = max(anchos[i], len(celda))

    def formatear(celdas):
        return "  ".join(
            celdas[i].ljust(anchos[i]) if i < izquierda else celdas[i].rjust(anchos[i])
            for i in range(len(celdas))
        )

    encabezado = formatear(columnas)
    print(encabezado)
    print("-" * len(encabezado))
    for fila in filas:
        print(formatear(fila))

def de(ok, total):
    return f"{ok} de {total}"

def porcentaje(valor):
    return f"{valor * 100:.1f}%"

def recortar(texto, largo=72):
    texto = str(texto)
    return texto if len(texto) <= largo else texto[: largo - 3] + "..."

def columnas_categoria(fila):
    return [de(fila[f"{nombre}_ok"], fila[f"{nombre}_total"]) for nombre in CATEGORIAS]

def imprimir_respuestas():
    """Prioridad que devolvió el modelo para cada ticket, en cada ciclo."""
    for nombre, ciclos in PREDICCIONES.items():
        print(f"RESPUESTA DEL MODELO · {nombre}")
        columnas = ["N", "Ticket", "Categoría", "Prioridad", *[f"Ciclo {n}" for n in range(1, len(ciclos) + 1)]]
        imprimir_tabla(
            columnas,
            [
                [
                    str(i + 1),
                    recortar(ticket),
                    str(df["categoria"].iloc[i]),
                    str(df["prioridad"].iloc[i]),
                    *[preds[i] if i < len(preds) else "sin_respuesta" for preds in ciclos],
                ]
                for i, ticket in enumerate(df["contexto"])
            ],
            izquierda=len(columnas),
        )
        print()

def imprimir_resultado(filas):
    """El modelo y sus respuestas, y después los ciclos, la comparación y las fórmulas."""
    print()
    print(f"MODELO: {MODEL}")
    print()
    imprimir_respuestas()
    print(f"CICLOS  ·  {len(df)} tickets, {CICLOS} ciclos por versión")
    imprimir_tabla(
        ["Versión", "Ciclo", "Aciertos", "Exactitud", "Desarrollo", "Despliegue", "Monitoreo"],
        [
            [
                fila["version"],
                str(numero),
                de(ciclo["aciertos"], ciclo["total"]),
                porcentaje(ciclo["exactitud"]),
                *columnas_categoria(ciclo),
            ]
            for fila in filas
            for numero, ciclo in enumerate(fila["ciclos"], start=1)
        ],
    )

    print()
    print("COMPARACIÓN DE SYSTEM PROMPTS")
    print("Un acierto es un ticket cuya prioridad coincide con la prioridad esperada.")
    imprimir_tabla(
        ["Versión", "Promedio", "Mínimo", "Máximo", "Desarrollo", "Despliegue", "Monitoreo"],
        [
            [
                fila["version"],
                porcentaje(fila["promedio"]),
                porcentaje(fila["minimo"]),
                porcentaje(fila["maximo"]),
                *columnas_categoria(fila),
            ]
            for fila in filas
        ],
    )

    print()
    print("FÓRMULAS")
    print("Promedio = suma de aciertos / (ciclos × tickets). Mínimo y máximo salen del peor y del mejor ciclo.")
    print("Desarrollo, despliegue y monitoreo de la comparación son los del último ciclo.")
    imprimir_tabla(
        ["Versión", "Aciertos de los ciclos", "Promedio", "Mínimo", "Máximo"],
        [
            [
                fila["version"],
                " + ".join(str(ciclo["aciertos"]) for ciclo in fila["ciclos"])
                + f" = {sum(ciclo['aciertos'] for ciclo in fila['ciclos'])}",
                (
                    f"{sum(ciclo['aciertos'] for ciclo in fila['ciclos'])} / "
                    f"({len(fila['ciclos'])} × {fila['ciclos'][0]['total']}) = {porcentaje(fila['promedio'])}"
                ),
                f"{min(ciclo['aciertos'] for ciclo in fila['ciclos'])} de {fila['ciclos'][0]['total']} = {porcentaje(fila['minimo'])}",
                f"{max(ciclo['aciertos'] for ciclo in fila['ciclos'])} de {fila['ciclos'][0]['total']} = {porcentaje(fila['maximo'])}",
            ]
            for fila in filas
        ],
    )

    imprimir_fallas()
    imprimir_inestables()

def imprimir_fallas():
    """Último ciclo: tickets en los que alguna versión no coincide con la prioridad esperada."""
    versiones = list(PROMPTS)
    distinto = df[versiones].ne(df["prioridad"], axis=0).any(axis=1)
    fallas = df.loc[distinto]
    print()
    print("DÓNDE FALLA")
    print("Último ciclo de v2_estructurado y v3_con_ejemplos.")
    if fallas.empty:
        print("Las dos versiones coincidieron con la prioridad esperada en todos los tickets.")
        return
    columnas = ["N", "Ticket", "Categoría", "Prioridad", *versiones]
    imprimir_tabla(
        columnas,
        [
            [
                str(int(i) + 1),
                recortar(fila["contexto"]),
                str(fila["categoria"]),
                str(fila["prioridad"]),
                *[str(fila[version]) for version in versiones],
            ]
            for i, fila in fallas.iterrows()
        ],
        izquierda=len(columnas),
    )

def imprimir_inestables():
    """Tickets cuya prioridad cambió entre ciclos de una misma versión."""
    versiones = list(PROMPTS)
    detalle = []
    conteo = []
    for nombre in versiones:
        ciclos = PREDICCIONES[nombre]
        inestables = []
        for i in range(len(df)):
            etiquetas = [ciclo[i] for ciclo in ciclos]
            if len(set(etiquetas)) > 1:
                inestables.append((i, etiquetas))
        conteo.append([nombre, str(len(inestables))])
        for i, etiquetas in inestables:
            detalle.append([
                nombre,
                str(i + 1),
                recortar(df["contexto"].iloc[i]),
                str(df["categoria"].iloc[i]),
                str(df["prioridad"].iloc[i]),
                *etiquetas,
            ])

    print()
    print("CASOS INESTABLES")
    print("La misma versión cambió la prioridad entre ciclos.")
    imprimir_tabla(["Versión", "Casos"], conteo)
    if not detalle:
        return
    print()
    columnas = ["Versión", "N", "Ticket", "Categoría", "Prioridad", *[f"Ciclo {n}" for n in range(1, CICLOS + 1)]]
    imprimir_tabla(columnas, detalle, izquierda=len(columnas))

if __name__ == "__main__":
    filas = [evaluar(prompt, nombre) for nombre, prompt in PROMPTS.items()]
    imprimir_resultado(filas)
