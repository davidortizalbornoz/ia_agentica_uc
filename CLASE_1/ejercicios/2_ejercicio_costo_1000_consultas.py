import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

_parte_guiada = Path(__file__).resolve().parents[1] / "parte_guiada"
sys.path.insert(0, str(_parte_guiada))

from common import MODEL, costo_usd, elegir_modelo, generar

consultas_dia = 1000
dias_mes = 30
TOKENS_SYSTEM_PROMPT = 2000
MODELO_2 = "gemini-3.8-flash"
elegir_modelo(MODELO_2)

def consultar(modelo):
    inicio = time.perf_counter()
    respuesta = generar(
        "¿Qué es un token?",
        model=modelo,
        system_instruction="Eres un tutor de un curso de IA agéntica. Respondes en español, en máximo 3 frases.",
        temperature=0.2,
        # Incluye los tokens de razonamiento. En gemini-3.8-flash un tope de 200
        # se agota pensando y la frase visible sale cortada.
        max_output_tokens=1024,
    )
    duracion_ms = (time.perf_counter() - inicio) * 1000
    u = respuesta.usage_metadata
    texto = respuesta.text
    if u is None or texto is None:
        raise SystemExit(f"La respuesta de {modelo} llegó sin texto o sin datos de uso.")
    salida = (u.candidates_token_count or 0) + (u.thoughts_token_count or 0)
    costo_consulta = costo_usd(u.prompt_token_count, salida, model=modelo)
    return {
        "modelo": modelo,
        "respuesta": texto.strip(),
        "duracion_ms": duracion_ms,
        "tokens_entrada": u.prompt_token_count,
        "tokens_salida": u.candidates_token_count,
        "tokens_razonamiento": u.thoughts_token_count or 0,
        "total": u.total_token_count,
        "costo_consulta": costo_consulta,
        "costo_diario": costo_consulta * consultas_dia,
        "costo_mensual": costo_consulta * consultas_dia * dias_mes,
    }

with ThreadPoolExecutor(max_workers=2) as executor:
    futuro_1 = executor.submit(consultar, MODEL)
    futuro_2 = executor.submit(consultar, MODELO_2)
    uno = futuro_1.result()
    dos = futuro_2.result()

print("\nEJERCICIO 2. COSTO DE 1.000 CONSULTAS")
print("______________________________________________\n")

for detalle in (uno, dos):
    print("Modelo:", detalle["modelo"])
    print("Respuesta:")
    print(detalle["respuesta"])
    print(f"tiempo de respuesta: {detalle['duracion_ms']:.0f} ms")
    print()

#DESDE AQUI COMIENZA LA TABLA COMPARATIVA DE MODELOS

def filas_comparacion(izq, der):
    return (
        ("tokens de entrada (prompt)", izq["tokens_entrada"], der["tokens_entrada"]),
        ("tokens de salida (respuesta)", izq["tokens_salida"], der["tokens_salida"]),
        ("tokens de razonamiento", izq["tokens_razonamiento"], der["tokens_razonamiento"]),
        ("total", izq["total"], der["total"]),
        ("costo una consulta", f"US${izq['costo_consulta']:.6f}", f"US${der['costo_consulta']:.6f}"),
        ("costo diario", f"US${izq['costo_diario']:.6f}", f"US${der['costo_diario']:.6f}"),
        ("costo mensual (30 días)", f"US${izq['costo_mensual']:.6f}", f"US${der['costo_mensual']:.6f}"),
    )

def imprimir_comparacion(titulo, filas, modelo_1, modelo_2):
    ancho_detalle = max(len("detalle"), *(len(nombre) for nombre, _, _ in filas))
    ancho_1 = max(len(modelo_1), *(len(str(valor)) for _, valor, _ in filas))
    ancho_2 = max(len(modelo_2), *(len(str(valor)) for _, _, valor in filas))
    linea = f"+{'-' * (ancho_detalle + 2)}+{'-' * (ancho_1 + 2)}+{'-' * (ancho_2 + 2)}+"

    def fila(detalle, col_1, col_2):
        return f"| {str(detalle):<{ancho_detalle}} | {str(col_1):<{ancho_1}} | {str(col_2):<{ancho_2}} |"

    print(titulo)
    print(linea)
    print(fila("detalle", modelo_1, modelo_2))
    print(linea)
    for nombre, valor_1, valor_2 in filas:
        print(fila(nombre, valor_1, valor_2))
    print(linea)
    print()

imprimir_comparacion(
    "TABLA COMPARATIVA DE MODELOS",
    filas_comparacion(uno, dos),
    uno["modelo"],
    dos["modelo"],
)

def con_system_prompt(detalle):
    """Recalcula la misma consulta con un system prompt fijo de 2000 tokens, sin llamar al modelo."""
    tokens_salida = detalle["tokens_salida"] or 0
    tokens_razonamiento = detalle["tokens_razonamiento"] or 0
    salida = tokens_salida + tokens_razonamiento
    costo_consulta = costo_usd(TOKENS_SYSTEM_PROMPT, salida, model=detalle["modelo"])
    return {
        "tokens_entrada": TOKENS_SYSTEM_PROMPT,
        "tokens_salida": tokens_salida,
        "tokens_razonamiento": tokens_razonamiento,
        "total": TOKENS_SYSTEM_PROMPT + tokens_salida + tokens_razonamiento,
        "costo_consulta": costo_consulta,
        "costo_diario": costo_consulta * consultas_dia,
        "costo_mensual": costo_consulta * consultas_dia * dias_mes,
    }

imprimir_comparacion(
    "TABLA COMPARATIVA: SYSTEM PROMPT DE 2000 TOKENS",
    filas_comparacion(con_system_prompt(uno), con_system_prompt(dos)),
    uno["modelo"],
    dos["modelo"],
)
