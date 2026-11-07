"""Tools del asistente de Personas de Lumen Retail.

Cada tool tiene dos partes:
  1. una función Python que consulta los JSON de `datos/` y devuelve un dict
     (o {"error": ...} si la consulta no se puede resolver);
  2. una `FunctionDeclaration`: el contrato que ve el modelo
     (nombre, descripción y parámetros en JSON Schema).

`REGISTRO` asocia el nombre de cada tool con su función.
`DECLARACIONES` y `TOOLS` son lo que recibe el modelo.
"""
import json
import math
import pathlib
import re
import unicodedata
from datetime import date, timedelta

from google.genai import types

DATOS = pathlib.Path(__file__).resolve().parent / "datos"
COLABORADORES = json.loads((DATOS / "colaboradores.json").read_text(encoding="utf-8"))
SOLICITUDES = json.loads((DATOS / "solicitudes.json").read_text(encoding="utf-8"))
POLITICAS = json.loads((DATOS / "politicas.json").read_text(encoding="utf-8"))
FERIADOS = {date.fromisoformat(f) for f in json.loads((DATOS / "feriados.json").read_text(encoding="utf-8"))["feriados"]}

TIPOS_SOLICITUD = (
    "vacaciones",
    "permiso_administrativo",
    "licencia_medica",
    "teletrabajo",
)
_TOKEN = re.compile(r"[a-z0-9]+")
_FECHA_ISO = re.compile(r"\d{4}-\d{2}-\d{2}")
_PESO_TITULO = 3
_PESO_TAG = 2
_PESO_TEXTO = 1


def _normalizar(s: str) -> str:
    """Minúsculas y sin tildes, para comparar nombres y palabras clave."""
    s = unicodedata.normalize("NFD", s or "").lower()
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _tokens(texto: str) -> list[str]:
    """Palabras alfanuméricas de un texto ya normalizado (sin tildes ni mayúsculas)."""
    return _TOKEN.findall(_normalizar(texto))


def _colaborador_por_id(colaborador_id: str) -> dict | None:
    """Devuelve el colaborador cuyo id coincide (sin distinguir mayúsculas) o None."""
    consulta = (colaborador_id or "").strip().lower()
    if not consulta:
        return None
    for colaborador in COLABORADORES:
        if colaborador["id"].lower() == consulta:
            return colaborador
    return None


def _error_id_colaborador(colaborador_id: str) -> dict:
    """Error cuando el id viene vacío o no está en colaboradores.json."""
    consulta = (colaborador_id or "").strip()
    if not consulta:
        return {"error": "Debes indicar el id del colaborador (formato C-001). Si solo tienes el nombre, usa buscar_colaborador primero."}
    return {"error": f"No existe un colaborador con id '{colaborador_id}'"}


def _campo_contiene(campo: str, palabra: str) -> bool:
    """True si algún token del campo es la palabra o empieza por ella (remoto/remotos)."""
    return any(token == palabra or token.startswith(palabra) for token in _tokens(campo))


def buscar_colaborador(nombre_o_id: str) -> dict:
    """Busca colaboradores por id exacto (C-001) o por coincidencia parcial de nombre.
    Devuelve {"coincidencias": [...]} (puede haber varias, p. ej. dos "Camila") o {"error": ...}."""
    q = _normalizar(nombre_o_id.strip())
    if not q:
        return {"error": "Debes indicar un nombre o un id"}
    por_id = [c for c in COLABORADORES if c["id"].lower() == q]
    if por_id:
        return {"coincidencias": por_id}
    por_nombre = [c for c in COLABORADORES if q in _normalizar(c["nombre"])]
    if not por_nombre:
        return {"error": f"No se encontró ningún colaborador que coincida con '{nombre_o_id}'"}
    return {"coincidencias": por_nombre}


DECL_BUSCAR_COLABORADOR = types.FunctionDeclaration(
    name="buscar_colaborador",
    description=("Busca colaboradores por id (formato C-001) o por nombre (parcial, sin distinguir tildes). "
                 "Devuelve una lista de coincidencias con id, nombre, cargo, área, jefatura_id, fecha_ingreso y modalidad. "
                 "Si hay más de una coincidencia, pregunta al usuario a cuál se refiere antes de seguir."),
    parameters_json_schema={
        "type": "object",
        "properties": {"nombre_o_id": {"type": "string", "description": "Id (C-001) o nombre o apellido del colaborador"}},
        "required": ["nombre_o_id"],
    },
)


def saldo_vacaciones(colaborador_id: str) -> dict:
    """Devuelve el saldo de vacaciones y la antigüedad de un colaborador.

    Lee `dias_vacaciones_disponibles` y `dias_vacaciones_tomados_2026` del
    registro en colaboradores.json. La antigüedad se mide a la fecha actual
    como años con un decimal: días de servicio / 365.25, redondeada a un
    decimal. Si el cociente exacto es menor que 1, el valor informado también
    queda bajo 1 (no se redondea a 1.0), la persona no tiene feriado legal y
    el resultado agrega una nota sobre el anticipo de vacaciones de POL-01.

    Args:
        colaborador_id: Id del colaborador, formato C-001. No acepta nombre.

    Returns:
        Dict con colaborador_id, nombre, dias_disponibles, dias_tomados_2026
        y antiguedad_anios. Incluye "nota" cuando la antigüedad es menor a un
        año. Si el id no existe o viene vacío, {"error": ...}.
    """
    colaborador = _colaborador_por_id(colaborador_id)
    if colaborador is None:
        return _error_id_colaborador(colaborador_id)

    ingreso = date.fromisoformat(colaborador["fecha_ingreso"])
    anios_exactos = (date.today() - ingreso).days / 365.25
    antiguedad_anios = round(anios_exactos, 1)
    if anios_exactos < 1 <= antiguedad_anios:
        antiguedad_anios = math.floor(anios_exactos * 10) / 10
    resultado = {
        "colaborador_id": colaborador["id"],
        "nombre": colaborador["nombre"],
        "dias_disponibles": colaborador["dias_vacaciones_disponibles"],
        "dias_tomados_2026": colaborador["dias_vacaciones_tomados_2026"],
        "antiguedad_anios": antiguedad_anios,
    }
    if anios_exactos < 1:
        resultado["nota"] = (
            "Menos de un año de antigüedad: no tiene saldo de vacaciones. "
            "Puede solicitar un anticipo de vacaciones con aprobación del área de Personas (POL-01)."
        )
    return resultado


DECL_SALDO_VACACIONES = types.FunctionDeclaration(
    name="saldo_vacaciones",
    description=(
        "Consulta el saldo individual de vacaciones de un colaborador ya identificado por su id (formato C-001). "
        "Úsala cuando pregunten cuántos días de vacaciones le quedan, cuántos días ha tomado durante 2026, "
        "o cuál es su antigüedad para saber si ya tiene derecho a feriado legal. "
        "El id es obligatorio: si la pregunta trae solo un nombre o un apellido, llama antes a buscar_colaborador. "
        "Si esa búsqueda devuelve más de una coincidencia (por ejemplo dos personas llamadas Camila), no elijas una: "
        "pide aclaración y no llames a esta tool hasta tener un único id. "
        "No la uses para el estado de un trámite (estado_solicitudes), ni para explicar la regla general de vacaciones, "
        "anticipación, fraccionamiento o vacaciones progresivas (buscar_politica con tema 'vacaciones'), "
        "ni para contar cuántos días hábiles hay entre dos fechas (dias_habiles_entre). "
        "Devuelve colaborador_id, nombre, dias_disponibles (saldo actual que se puede pedir), "
        "dias_tomados_2026 (días de vacaciones ya usados en el año 2026) y antiguedad_anios "
        "(años de servicio con un decimal, calculados a la fecha actual como días corridos / 365.25; "
        "si aún no cumple un año, antiguedad_anios es menor que 1). "
        "Si la antigüedad es menor a un año, el dict incluye además nota: esa persona no tiene saldo de feriado legal "
        "y solo puede pedir un anticipo con aprobación de Personas, según POL-01. "
        "Cita únicamente dias_disponibles; no recalcules el saldo ni sumes los días tomados. "
        "Si el id no existe, la respuesta es {\"error\": ...}: comunícalo y no inventes cifras."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "colaborador_id": {
                "type": "string",
                "description": (
                    "Id exacto del colaborador, formato C-001. No envíes el nombre ni el correo. "
                    "Si solo conoces el nombre, resuélvelo antes con buscar_colaborador y usa el id de la única coincidencia."
                ),
            },
        },
        "required": ["colaborador_id"],
    },
)


def estado_solicitudes(colaborador_id: str, tipo: str = "") -> dict:
    """Lista las solicitudes de un colaborador, con filtro opcional por tipo.

    Los tipos válidos son vacaciones, permiso_administrativo, licencia_medica
    y teletrabajo. Sin tipo, devuelve todas las solicitudes de esa persona.
    Cada elemento de la lista conserva los campos de solicitudes.json: id,
    colaborador_id, tipo, fecha_inicio, fecha_fin, dias, estado, aprobador_id
    y comentario.

    Args:
        colaborador_id: Id del colaborador, formato C-001.
        tipo: Filtro opcional. Vacío devuelve todas las solicitudes.

    Returns:
        Dict con colaborador_id, total y solicitudes. total es el largo de
        la lista y puede ser 0 si la persona existe pero no tiene trámites
        de ese tipo. Si el id no existe o el tipo no es uno de los cuatro
        válidos, {"error": ...}.
    """
    colaborador = _colaborador_por_id(colaborador_id)
    if colaborador is None:
        return _error_id_colaborador(colaborador_id)

    tipo_norm = _normalizar(tipo).strip().replace(" ", "_")
    if tipo_norm and tipo_norm not in TIPOS_SOLICITUD:
        tipos = ", ".join(TIPOS_SOLICITUD)
        return {"error": f"Tipo de solicitud desconocido: '{tipo}'. Usa uno de: {tipos}. Omite el tipo para ver todas."}

    solicitudes = [
        dict(solicitud)
        for solicitud in SOLICITUDES
        if solicitud["colaborador_id"] == colaborador["id"] and (not tipo_norm or solicitud["tipo"] == tipo_norm)
    ]
    return {
        "colaborador_id": colaborador["id"],
        "total": len(solicitudes),
        "solicitudes": solicitudes,
    }


DECL_ESTADO_SOLICITUDES = types.FunctionDeclaration(
    name="estado_solicitudes",
    description=(
        "Lista las solicitudes de ausencia o modalidad de un colaborador ya identificado por su id (formato C-001): "
        "vacaciones, permiso administrativo, licencia médica y teletrabajo, con su estado de aprobación. "
        "Úsala cuando pregunten en qué está un trámite, si está aprobado, pendiente, en revisión o rechazado, "
        "quién lo aprueba, qué fechas cubre, cuántos días pidió o cuál fue el comentario de la jefatura. "
        "Sirve también para revisar si ya existe una solicitud que se solape con fechas nuevas. "
        "Requiere el id: si solo hay un nombre, llama antes a buscar_colaborador y no continúes si hay varias coincidencias. "
        "El parámetro tipo es opcional. Omítelo, o envíalo vacío, para traer todas las solicitudes de esa persona. "
        "Si lo envías, debe ser exactamente uno de: vacaciones, permiso_administrativo, licencia_medica, teletrabajo. "
        "No la uses para el saldo disponible (saldo_vacaciones), ni para la regla de la política (buscar_politica), "
        "ni para calcular días hábiles de un rango (dias_habiles_entre). "
        "Devuelve colaborador_id, total (cantidad de solicitudes que cumplen el filtro; puede ser 0) y solicitudes, "
        "una lista de dicts con id (S-2026-000), colaborador_id, tipo, fecha_inicio, fecha_fin, dias, estado "
        "(aprobada, pendiente, en_revision o rechazada), aprobador_id y comentario. "
        "Responde solo con esos campos. Si estado es rechazada o en_revision, incluye el comentario: suele explicar el motivo. "
        "Una licencia médica es dato sensible (POL-07): entrega el periodo y el estado, nunca un diagnóstico; estos registros no traen diagnóstico. "
        "Si el id no existe o el tipo no es válido, la respuesta es {\"error\": ...}: explícalo y no inventes solicitudes."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "colaborador_id": {
                "type": "string",
                "description": (
                    "Id exacto del colaborador dueño de las solicitudes, formato C-001. "
                    "No envíes el nombre. Resuélvelo antes con buscar_colaborador si hace falta."
                ),
            },
            "tipo": {
                "type": "string",
                "description": (
                    "Filtro opcional por tipo de solicitud. Omítelo para devolver todas. "
                    "Valores admitidos: vacaciones, permiso_administrativo, licencia_medica, teletrabajo."
                ),
                "enum": list(TIPOS_SOLICITUD),
            },
        },
        "required": ["colaborador_id"],
    },
)


def buscar_politica(tema: str) -> dict:
    """Busca hasta dos políticas internas por palabras del tema.

    Considera solo palabras de más de 3 letras. Cada palabra suma 3 puntos si
    aparece en el título, 2 si aparece en los tags y 1 si aparece en el texto.
    Un token del campo cuenta cuando es igual a la palabra o empieza por ella
    (por ejemplo, remoto coincide con remotos). El resultado ordena por puntaje
    descendente y, ante empate, por id.

    Args:
        tema: Pregunta o palabras clave, por ejemplo "vacaciones" o
            "trabajar remoto desde la casa".

    Returns:
        {"politicas": [{"id", "titulo", "texto"}, ...]} con como máximo las
        dos políticas de mayor puntaje. Si el tema no aporta palabras útiles
        o ninguna política suma puntos, {"error": ...}.
    """
    palabras = [palabra for palabra in _tokens(tema) if len(palabra) > 3]
    if not palabras:
        return {"error": "Debes indicar un tema con al menos una palabra de más de 3 letras"}

    puntuadas: list[tuple[int, dict]] = []
    for politica in POLITICAS:
        tags = " ".join(politica["tags"])
        puntaje = 0
        for palabra in palabras:
            if _campo_contiene(politica["titulo"], palabra):
                puntaje += _PESO_TITULO
            if _campo_contiene(tags, palabra):
                puntaje += _PESO_TAG
            if _campo_contiene(politica["texto"], palabra):
                puntaje += _PESO_TEXTO
        if puntaje > 0:
            puntuadas.append((puntaje, politica))

    if not puntuadas:
        return {"error": f"No se encontró ninguna política que coincida con '{tema}'"}

    puntuadas.sort(key=lambda item: (-item[0], item[1]["id"]))
    return {
        "politicas": [
            {"id": politica["id"], "titulo": politica["titulo"], "texto": politica["texto"]}
            for _, politica in puntuadas[:2]
        ]
    }


DECL_BUSCAR_POLITICA = types.FunctionDeclaration(
    name="buscar_politica",
    description=(
        "Busca en el corpus de políticas internas de Lumen Retail (POL-01 a POL-07) las reglas que aplican a un tema. "
        "Úsala cuando la pregunta sea normativa y no un dato individual: cuántos días de vacaciones corresponden por año, "
        "con cuánta anticipación se piden, si se pueden fraccionar, qué es el anticipo o las vacaciones progresivas, "
        "cuántos permisos administrativos hay al año, cómo se informa una licencia médica, cuántos días de teletrabajo "
        "o remoto se pueden pedir, jornada, marcaje, horas extra, beneficios (aguinaldo, bono escolar, seguro, descuento) "
        "o a quién se le puede entregar información de otra persona (privacidad, POL-07). "
        "Pasa en tema la pregunta del usuario o sus palabras clave; no hace falta que sea el título exacto de la política. "
        "La búsqueda ignora mayúsculas y tildes, descarta palabras de 3 letras o menos y prioriza coincidencias en el título "
        "y en los tags por sobre el cuerpo del texto. "
        "No la uses para saldos (saldo_vacaciones), trámites concretos (estado_solicitudes) ni para contar días hábiles "
        "de un calendario (dias_habiles_entre). Si la pregunta mezcla regla y dato de una persona, llama esta tool y además la tool de datos. "
        "Devuelve {\"politicas\": [{\"id\", \"titulo\", \"texto\"}, ...]} con como máximo las dos políticas más relevantes, "
        "ordenadas de mayor a menor coincidencia. Responde citando el id (por ejemplo POL-01) y solo lo que diga el campo texto; "
        "no completes la regla con conocimiento externo ni con los tags, que no vienen en la respuesta. "
        "Si nada coincide, la respuesta es {\"error\": ...}: dilo y deriva al área de Personas (personas@lumenretail.example) "
        "en vez de inventar una política."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "tema": {
                "type": "string",
                "description": (
                    "Tema, pregunta o palabras clave de la regla a buscar. "
                    "Ejemplos: 'vacaciones', 'permiso administrativo', 'licencia médica', "
                    "'trabajar remoto desde la casa', 'jornada y horas extra', 'beneficios', 'privacidad de datos de un tercero'."
                ),
            },
        },
        "required": ["tema"],
    },
)


def _parse_fecha(valor: str) -> date:
    """Parsea una fecha AAAA-MM-DD. Lanza ValueError si el formato o el calendario no son válidos."""
    texto = (valor or "").strip()
    if not _FECHA_ISO.fullmatch(texto):
        raise ValueError(texto)
    return date.fromisoformat(texto)


def dias_habiles_entre(fecha_inicio: str, fecha_fin: str) -> dict:
    """Cuenta los días hábiles entre dos fechas, ambas inclusive.

    Un día hábil es lunes a viernes y no está en el set FERIADOS. Los feriados
    que caen sábado o domingo no se cuentan como hábiles ni se listan.
    feriados_en_rango solo incluye feriados que caen de lunes a viernes,
    en orden cronológico y formato AAAA-MM-DD.

    Args:
        fecha_inicio: Fecha inicial inclusive, formato AAAA-MM-DD.
        fecha_fin: Fecha final inclusive, formato AAAA-MM-DD. No puede ser
            anterior a fecha_inicio.

    Returns:
        Dict con fecha_inicio, fecha_fin, dias_habiles y feriados_en_rango.
        Si el formato no es AAAA-MM-DD o fecha_fin es anterior a fecha_inicio,
        {"error": ...}.
    """
    try:
        inicio = _parse_fecha(fecha_inicio)
        fin = _parse_fecha(fecha_fin)
    except ValueError:
        return {"error": "Las fechas deben tener formato AAAA-MM-DD, por ejemplo 2026-11-23"}
    if fin < inicio:
        return {"error": "fecha_fin no puede ser anterior a fecha_inicio"}

    dias_habiles = 0
    feriados_en_rango: list[str] = []
    actual = inicio
    while actual <= fin:
        es_dia_de_semana = actual.weekday() < 5
        if actual in FERIADOS and es_dia_de_semana:
            feriados_en_rango.append(actual.isoformat())
        if es_dia_de_semana and actual not in FERIADOS:
            dias_habiles += 1
        actual += timedelta(days=1)

    return {
        "fecha_inicio": inicio.isoformat(),
        "fecha_fin": fin.isoformat(),
        "dias_habiles": dias_habiles,
        "feriados_en_rango": feriados_en_rango,
    }


DECL_DIAS_HABILES = types.FunctionDeclaration(
    name="dias_habiles_entre",
    description=(
        "Cuenta los días hábiles entre dos fechas, ambas inclusive, usando el calendario del caso: "
        "lunes a viernes, restando los feriados de Chile cargados en feriados.json. "
        "Úsala cuando pregunten cuántos días hábiles hay en un periodo de vacaciones o permiso, "
        "si un rango alcanza el mínimo de 10 días hábiles, cuántos días hábiles de anticipación hay entre la fecha de hoy "
        "y el inicio de una solicitud, o qué feriados de día de semana "
        "caen dentro de esas fechas. "
        "No calcula saldos ni decide si una solicitud está aprobada: para eso están saldo_vacaciones y estado_solicitudes. "
        "Tampoco reemplaza a buscar_politica cuando la pregunta es cuál es la regla de anticipación. "
        "Ambas fechas son obligatorias y deben ir en formato AAAA-MM-DD (año-mes-día). "
        "No aceptes ni conviertas formatos como 27/11/2026 o 27-11-2026: si el usuario los escribe así, "
        "reformula a AAAA-MM-DD antes de llamar, o informa que el formato es inválido. "
        "fecha_fin debe ser igual o posterior a fecha_inicio. Un mismo día hábil y no feriado cuenta como 1. "
        "Devuelve fecha_inicio, fecha_fin, dias_habiles (entero) y feriados_en_rango: lista de fechas ISO de feriados "
        "que cayeron de lunes a viernes dentro del rango. Un feriado en sábado o domingo no entra en esa lista y tampoco suma como hábil. "
        "Si el formato es inválido o fecha_fin es anterior a fecha_inicio, la respuesta es {\"error\": ...}: "
        "explica el problema y pide las fechas de nuevo. No estimes el número de días por tu cuenta."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "fecha_inicio": {
                "type": "string",
                "description": "Fecha inicial inclusive, en formato AAAA-MM-DD. Ejemplo: 2026-11-23. No uses DD/MM/AAAA.",
            },
            "fecha_fin": {
                "type": "string",
                "description": "Fecha final inclusive, en formato AAAA-MM-DD. Debe ser igual o posterior a fecha_inicio. Ejemplo: 2026-11-27.",
            },
        },
        "required": ["fecha_inicio", "fecha_fin"],
    },
)


REGISTRO = {
    "buscar_colaborador": buscar_colaborador,
    "saldo_vacaciones": saldo_vacaciones,
    "estado_solicitudes": estado_solicitudes,
    "buscar_politica": buscar_politica,
    "dias_habiles_entre": dias_habiles_entre,
}
DECLARACIONES = [
    DECL_BUSCAR_COLABORADOR,
    DECL_SALDO_VACACIONES,
    DECL_ESTADO_SOLICITUDES,
    DECL_BUSCAR_POLITICA,
    DECL_DIAS_HABILES,
]
TOOLS = [types.Tool(function_declarations=DECLARACIONES)]
