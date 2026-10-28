import importlib.util
import sys
import time
from pathlib import Path

import pandas as pd
from pydantic import BaseModel

# generar vive en la parte guiada de la clase 1 y lee la API key desde el .env.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "CLASE_1" / "parte_guiada"))
from common import MODEL, generar

# Los 31 correos ya etiquetados están en el script anterior.
_spec = importlib.util.spec_from_file_location(
    "elproblema_ylosdatos",
    Path(__file__).with_name("1_practico_elproblema_ylosdatos.py"),
)
if _spec is None or _spec.loader is None:
    raise SystemExit("No se encontró 1_practico_elproblema_ylosdatos.py")
_datos = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_datos)
df = _datos.df

# Tres instrucciones para la misma tarea. Solo cambia el system prompt.
# v1 no dice las categorías. v2 las define. v3 repite v2 y agrega ejemplos.
v2 = """Eres el clasificador de correos de Andina Cargo (logística).
Tarea: asignar UNA categoría al correo del cliente.
Categorías:
- facturacion: facturas, pagos, notas de crédito, datos tributarios.
- tecnico: errores de la plataforma web, app o API, accesos y contraseñas.
- reclamo: quejas por daños, retrasos, mal servicio o entregas no realizadas.
- otro: consultas comerciales, cotizaciones, horarios, cobertura.
Responde SOLO con el nombre de la categoría, en minúsculas, sin explicación."""

PROMPTS = {
    "v1_vago": "Clasifica el correo.",
    "v2_estructurado": v2,
    "v3_con_ejemplos": v2 + """

Ejemplos:
Correo: "La boleta salió con un monto distinto al cotizado" -> facturacion
Correo: "La página de tracking no carga desde ayer" -> tecnico
Correo: "La carga llegó mojada" -> reclamo
Correo: "¿Hacen despachos los sábados?" -> otro""",
}

PAUSA = 2.0   # segundos entre llamadas, para respetar el límite por minuto del nivel gratuito

# La respuesta de cada llamada es una lista de {id, categoria}, un elemento por correo.
# categoria es str a propósito: queremos ver si un prompt vago inventa nombres.
class Etiqueta(BaseModel):
    id: int
    categoria: str

class Lote(BaseModel):
    resultados: list[Etiqueta]

def clasificar_lote(correos, system_prompt):
    """Clasifica todos los correos en una sola llamada. Devuelve una categoría por correo, en el mismo orden."""
    lista = "\n".join(f"{i}. {c}" for i, c in enumerate(correos))
    contenido = f"Clasifica cada uno de los siguientes correos, identificados por su número:\n\n{lista}"
    r = generar(contenido, system_instruction=system_prompt, temperature=0,
                response_mime_type="application/json", response_schema=Lote)
    time.sleep(PAUSA)
    lote = getattr(r, "parsed", None)
    if lote is None:
        texto = r.text
        if texto is None:
            raise SystemExit("La respuesta del modelo llegó sin texto.")
        lote = Lote.model_validate_json(texto)
    por_id = {e.id: e.categoria.strip().lower().strip(".") for e in lote.resultados}
    return [por_id.get(i, "sin_respuesta") for i in range(len(correos))]

CICLOS = 3          # aunque temperature=0, el modelo puede cambiar alguna etiqueta; por eso repetimos
PREDICCIONES = {}   # nombre de la versión -> lista de predicciones de cada ciclo

def medir(preds):
    """Aciertos de un ciclo: total, fáciles y difíciles."""
    ok = pd.Series(preds) == df["clasificacion"]
    faciles = ok[df.dificultad == "facil"]
    dificiles = ok[df.dificultad == "dificil"]
    return {
        "aciertos": int(ok.sum()),
        "total": int(ok.shape[0]),
        "exactitud": float(ok.mean()),
        "faciles_ok": int(faciles.sum()),
        "faciles_total": int(faciles.shape[0]),
        "dificiles_ok": int(dificiles.sum()),
        "dificiles_total": int(dificiles.shape[0]),
    }

def evaluar(system_prompt, nombre, ciclos=CICLOS):
    """Mide cuántos correos coinciden con la etiqueta esperada."""
    mediciones = []
    PREDICCIONES[nombre] = []
    for k in range(ciclos):
        print(f"Consultando {nombre}, ciclo {k + 1} de {ciclos}...")
        preds = clasificar_lote(list(df["correo"]), system_prompt)
        PREDICCIONES[nombre].append(preds)
        mediciones.append(medir(preds))

    # El último ciclo queda en el dataframe para poder revisar correo por correo.
    df[nombre] = PREDICCIONES[nombre][-1]
    ultimo = mediciones[-1]
    exactitudes = [m["exactitud"] for m in mediciones]
    return {
        "version": nombre,
        "promedio": sum(exactitudes) / len(exactitudes),
        "minimo": min(exactitudes),
        "maximo": max(exactitudes),
        "faciles_ok": ultimo["faciles_ok"],
        "faciles_total": ultimo["faciles_total"],
        "dificiles_ok": ultimo["dificiles_ok"],
        "dificiles_total": ultimo["dificiles_total"],
        "ciclos": mediciones,
    }

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

def recortar(texto, largo=48):
    texto = str(texto)
    return texto if len(texto) <= largo else texto[: largo - 3] + "..."

def imprimir_respuestas():
    """Categoría que devolvió el modelo para cada correo, en cada ciclo."""
    for nombre, ciclos in PREDICCIONES.items():
        print(f"RESPUESTA DEL MODELO · {nombre}")
        columnas = ["N", "Correo", "Clasificación", *[f"Ciclo {n}" for n in range(1, len(ciclos) + 1)]]
        imprimir_tabla(
            columnas,
            [
                [
                    str(i + 1),
                    recortar(correo),
                    str(df["clasificacion"].iloc[i]),
                    *[preds[i] if i < len(preds) else "sin_respuesta" for preds in ciclos],
                ]
                for i, correo in enumerate(df["correo"])
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
    print(f"CICLOS  ·  {len(df)} correos, {CICLOS} ciclos por versión")
    imprimir_tabla(
        ["Versión", "Ciclo", "Aciertos", "Exactitud", "Fáciles", "Difíciles"],
        [
            [
                fila["version"],
                str(numero),
                de(ciclo["aciertos"], ciclo["total"]),
                porcentaje(ciclo["exactitud"]),
                de(ciclo["faciles_ok"], ciclo["faciles_total"]),
                de(ciclo["dificiles_ok"], ciclo["dificiles_total"]),
            ]
            for fila in filas
            for numero, ciclo in enumerate(fila["ciclos"], start=1)
        ],
    )

    print()
    print("COMPARACIÓN DE SYSTEM PROMPTS")
    print("Un acierto es un correo cuya categoría coincide con la clasificación.")
    imprimir_tabla(
        ["Versión", "Promedio", "Mínimo", "Máximo", "Fáciles", "Difíciles"],
        [
            [
                fila["version"],
                porcentaje(fila["promedio"]),
                porcentaje(fila["minimo"]),
                porcentaje(fila["maximo"]),
                de(fila["faciles_ok"], fila["faciles_total"]),
                de(fila["dificiles_ok"], fila["dificiles_total"]),
            ]
            for fila in filas
        ],
    )

    print()
    print("FÓRMULAS")
    print("Promedio = suma de aciertos / (ciclos × correos). Mínimo y máximo salen del peor y del mejor ciclo.")
    print("Fáciles y difíciles de la comparación son los del último ciclo.")
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
    """Último ciclo: correos en los que v2 o v3 no coinciden con la clasificación.

    v1 queda fuera porque inventa los nombres de las categorías y fallaría en todos.
    """
    versiones = [nombre for nombre in PROMPTS if nombre != "v1_vago"]
    distinto = df[versiones].ne(df["clasificacion"], axis=0).any(axis=1)
    fallas = df.loc[distinto]
    print()
    print("DÓNDE FALLA")
    print("Último ciclo de v2 y v3. v1 no entra: inventa los nombres de las categorías.")
    if fallas.empty:
        print("v2 y v3 coincidieron con la clasificación en todos los correos.")
        return
    columnas = ["N", "Correo", "Clasificación", "Dificultad", *versiones]
    imprimir_tabla(
        columnas,
        [
            [
                str(int(i) + 1),
                recortar(fila["correo"]),
                str(fila["clasificacion"]),
                str(fila["dificultad"]),
                *[str(fila[version]) for version in versiones],
            ]
            for i, fila in fallas.iterrows()
        ],
        izquierda=len(columnas),
    )

def imprimir_inestables():
    """Correos cuya categoría cambió entre ciclos de la misma versión.

    v1 queda fuera, igual que en la tabla de fallas.
    """
    versiones = [nombre for nombre in PROMPTS if nombre != "v1_vago"]
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
                recortar(df["correo"].iloc[i]),
                str(df["clasificacion"].iloc[i]),
                str(df["dificultad"].iloc[i]),
                *etiquetas,
            ])

    print()
    print("CASOS INESTABLES")
    print("La misma versión cambió la categoría entre ciclos. v1 no entra.")
    imprimir_tabla(["Versión", "Casos"], conteo)
    if not detalle:
        return
    print()
    columnas = ["Versión", "N", "Correo", "Clasificación", "Dificultad", *[f"Ciclo {n}" for n in range(1, CICLOS + 1)]]
    imprimir_tabla(columnas, detalle, izquierda=len(columnas))

if __name__ == "__main__":
    filas = [evaluar(prompt, nombre) for nombre, prompt in PROMPTS.items()]
    imprimir_resultado(filas)
