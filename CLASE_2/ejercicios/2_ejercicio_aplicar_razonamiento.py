import importlib.util
import sys
import time
from pathlib import Path

import pandas as pd
from google.genai import types
from pydantic import BaseModel

# generar vive en la parte guiada de la clase 1 y lee la API key desde el .env.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "CLASE_1" / "parte_guiada"))
from common import MODEL, costo_usd, generar

# Los 31 correos ya etiquetados están en la parte guiada de esta clase.
_spec = importlib.util.spec_from_file_location(
    "elproblema_ylosdatos",
    Path(__file__).resolve().parents[1] / "parte_guiada" / "1_practico_elproblema_ylosdatos.py",
)
if _spec is None or _spec.loader is None:
    raise SystemExit("No se encontró 1_practico_elproblema_ylosdatos.py")
_datos = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_datos)
df = _datos.df

# Las dos versiones usan el mismo texto. v2_razonamiento además pide razonamiento al modelo.
v2 = """Eres el clasificador de correos de Andina Cargo (logística).
Tarea: asignar UNA categoría al correo del cliente.
Categorías:
- facturacion: facturas, pagos, notas de crédito, datos tributarios.
- tecnico: errores de la plataforma web, app o API, accesos y contraseñas.
- reclamo: quejas por daños, retrasos, mal servicio o entregas no realizadas.
- otro: consultas comerciales, cotizaciones, horarios, cobertura.
Responde SOLO con el nombre de la categoría, en minúsculas, sin explicación."""

PROMPTS = {
    "v2_estructurado": v2,
    "v2_razonamiento": v2,
}

RAZONAMIENTO = {
    "v2_razonamiento": types.ThinkingConfig(
        thinking_level=types.ThinkingLevel.HIGH,
        include_thoughts=True,
    ),
}

PAUSA = 2.0   # segundos entre llamadas, para respetar el límite por minuto del nivel gratuito

# La respuesta de cada llamada es una lista de {id, categoria}, un elemento por correo.
# categoria es str: el modelo responde el nombre de una de las cuatro categorías.
class Etiqueta(BaseModel):
    id: int
    categoria: str

class Lote(BaseModel):
    resultados: list[Etiqueta]

def clasificar_lote(correos, system_prompt, thinking_config=None):
    """Clasifica todos los correos en una sola llamada. Devuelve una categoría por correo, en el mismo orden."""
    lista = "\n".join(f"{i}. {c}" for i, c in enumerate(correos))
    contenido = f"Clasifica cada uno de los siguientes correos, identificados por su número:\n\n{lista}"
    config = {}
    if thinking_config is not None:
        config["thinking_config"] = thinking_config
    r = generar(contenido, system_instruction=system_prompt, temperature=0,
                response_mime_type="application/json", response_schema=Lote, **config)
    time.sleep(PAUSA)
    lote = getattr(r, "parsed", None)
    if lote is None:
        texto = r.text
        if texto is None:
            raise SystemExit("La respuesta del modelo llegó sin texto.")
        lote = Lote.model_validate_json(texto)
    por_id = {e.id: e.categoria.strip().lower().strip(".") for e in lote.resultados}
    uso = r.usage_metadata
    if uso is None:
        raise SystemExit("La respuesta del modelo llegó sin datos de uso.")
    entrada = uso.prompt_token_count or 0
    salida = (uso.candidates_token_count or 0) + (uso.thoughts_token_count or 0)
    return [por_id.get(i, "sin_respuesta") for i in range(len(correos))], {
        "entrada": entrada,
        "salida": salida,
        "costo": costo_usd(entrada, salida),
    }

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
        preds, uso = clasificar_lote(
            list(df["correo"]),
            system_prompt,
            thinking_config=RAZONAMIENTO.get(nombre),
        )
        PREDICCIONES[nombre].append(preds)
        medicion = medir(preds)
        medicion.update(uso)
        mediciones.append(medicion)

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
    imprimir_costo(filas)

def imprimir_fallas():
    """Último ciclo: correos en los que alguna versión no coincide con la clasificación."""
    versiones = list(PROMPTS)
    distinto = df[versiones].ne(df["clasificacion"], axis=0).any(axis=1)
    fallas = df.loc[distinto]
    print()
    print("DÓNDE FALLA")
    print("Último ciclo de v2_estructurado y v2_razonamiento.")
    if fallas.empty:
        print("Las dos versiones coincidieron con la clasificación en todos los correos.")
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
    """Correos cuya categoría cambió entre ciclos de una misma versión."""
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
                recortar(df["correo"].iloc[i]),
                str(df["clasificacion"].iloc[i]),
                str(df["dificultad"].iloc[i]),
                *etiquetas,
            ])

    print()
    print("CASOS INESTABLES")
    print("La misma versión cambió la categoría entre ciclos.")
    imprimir_tabla(["Versión", "Casos"], conteo)
    if not detalle:
        return
    print()
    columnas = ["Versión", "N", "Correo", "Clasificación", "Dificultad", *[f"Ciclo {n}" for n in range(1, CICLOS + 1)]]
    imprimir_tabla(columnas, detalle, izquierda=len(columnas))

def imprimir_costo(filas):
    """Tokens de salida y costo estimado de cada ciclo, con un total por prompt."""
    print()
    print("TOKENS Y COSTO")
    print("Tokens de salida = respuesta + razonamiento.")
    print("El costo estimado incluye el prompt y la salida, a precio del nivel de pago.")
    print("El total suma los ciclos de cada prompt.")
    filas_tabla = []
    for fila in filas:
        total_entrada = 0
        total_salida = 0
        total_costo = 0.0
        for numero, ciclo in enumerate(fila["ciclos"], start=1):
            filas_tabla.append([
                fila["version"],
                str(numero),
                str(ciclo["entrada"]),
                str(ciclo["salida"]),
                f"US${ciclo['costo']:.6f}",
            ])
            total_entrada += ciclo["entrada"]
            total_salida += ciclo["salida"]
            total_costo += ciclo["costo"]
        filas_tabla.append([
            fila["version"],
            "Total",
            str(total_entrada),
            str(total_salida),
            f"US${total_costo:.6f}",
        ])
    imprimir_tabla(
        ["Versión", "Ciclo", "Tokens del prompt", "Tokens de salida", "Costo estimado"],
        filas_tabla,
    )

if __name__ == "__main__":
    filas = [evaluar(prompt, nombre) for nombre, prompt in PROMPTS.items()]
    imprimir_resultado(filas)
