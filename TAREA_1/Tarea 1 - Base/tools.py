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


_CAMPOS_DIRECTORIO = ("id", "nombre", "cargo", "area", "jefatura_id")


def _ficha_directorio(colaborador: dict) -> dict:
    """Identificación pública: sin saldo, días tomados, correo, ingreso ni modalidad."""
    return {campo: colaborador[campo] for campo in _CAMPOS_DIRECTORIO}


def _reportes_directos(colaborador_id: str) -> list[dict]:
    """Personas cuyo jefatura_id es este colaborador. No incluye al resto del área."""
    consulta = (colaborador_id or "").strip().lower()
    if not consulta:
        return []
    return [c for c in COLABORADORES if (c.get("jefatura_id") or "").lower() == consulta]


def etiqueta_consultante(colaborador_id: str) -> dict:
    """Identifica al consultante: área, cargo y de quién es jefatura directa.

    Un equipo son las personas que comparten área. Esta tool no autoriza a ver a
    todo el equipo: solo lista a quienes tienen a este id en jefatura_id.
    No incluye saldo, días tomados, correo, fecha de ingreso ni modalidad.

    Args:
        colaborador_id: Id de quien pregunta, formato C-001. No acepta nombre.

    Returns:
        Dict con colaborador_id, nombre, cargo, area, es_jefatura_directa,
        reportes_directos (id, nombre, cargo, area, jefatura_id) y etiqueta,
        la línea que encabeza la consulta. Si el id no existe, {"error": ...}.
    """
    colaborador = _colaborador_por_id(colaborador_id)
    if colaborador is None:
        return _error_id_colaborador(colaborador_id)

    reportes = [_ficha_directorio(c) for c in _reportes_directos(colaborador["id"])]
    if reportes:
        equipo = ", ".join(f"{c['id']} {c['nombre']}" for c in reportes)
        alcance = f"jefatura directa de {equipo}"
    else:
        alcance = "sin personas a cargo"
    etiqueta = (
        f"{colaborador['id']} {colaborador['nombre']}, {colaborador['cargo']}, "
        f"área {colaborador['area']}, {alcance}"
    )
    return {
        "colaborador_id": colaborador["id"],
        "nombre": colaborador["nombre"],
        "cargo": colaborador["cargo"],
        "area": colaborador["area"],
        "es_jefatura_directa": bool(reportes),
        "reportes_directos": reportes,
        "etiqueta": etiqueta,
    }


DECL_ETIQUETA_CONSULTANTE = types.FunctionDeclaration(
    name="etiqueta_consultante",
    description=(
        "Identifica a quien hace la consulta y deja listo el contexto de POL-07 antes de pedir un dato individual. "
        "Úsala en los primeros pasos del loop cuando necesites confirmar el área del consultante o saber de quién es jefatura directa. "
        "El mensaje ya puede traer una línea '[Consulta de: ...]'; esta tool devuelve el mismo dato, estructurado, a partir del id. "
        "Recibe solo el id de quien pregunta (formato C-001), no el de la persona consultada y no un nombre. "
        "Un equipo son todos los colaboradores que comparten área. Esta tool no lista el área completa: "
        "reportes_directos son únicamente las personas cuyo campo jefatura_id es este consultante. "
        "Compartir área no convierte a alguien en jefatura de sus compañeros. "
        "Ejemplo: Felipe Araya (C-006, Operaciones) es jefatura directa de Rodrigo Fuentes (C-002) y no de Matías Soto, "
        "aunque Matías también esté en Operaciones, porque la jefatura_id de Matías es C-002. "
        "No la uses para saldos (saldo_vacaciones), trámites (estado_solicitudes) ni para decidir el acceso a un tercero "
        "(evaluar_acceso_pol07). Tampoco reemplaza a buscar_colaborador cuando el usuario da un nombre o hay homónimos. "
        "Devuelve colaborador_id, nombre, cargo, area, es_jefatura_directa (true si reportes_directos no está vacío), "
        "reportes_directos (lista de fichas con id, nombre, cargo, area y jefatura_id; puede venir vacía) y etiqueta, "
        "una frase con id, nombre, cargo, área y el alcance de jefatura. "
        "No trae dias_vacaciones, correo, fecha_ingreso ni modalidad. "
        "Si el id no existe o viene vacío, la respuesta es {\"error\": ...}: explícalo y no inventes el equipo."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "colaborador_id": {
                "type": "string",
                "description": (
                    "Id exacto de quien pregunta, formato C-001. "
                    "No envíes el nombre, el correo ni el id de la persona sobre la que se consulta."
                ),
            },
        },
        "required": ["colaborador_id"],
    },
)


def evaluar_acceso_pol07(consultante_id: str | None, objetivo_id: str) -> dict:
    """Decide si POL-07 permite entregar saldos, solicitudes o licencias del objetivo.

    Permitido solo en dos casos: el consultante es la misma persona, o su id es el
    jefatura_id del objetivo. Compartir área no autoriza. No se recorre la cadena
    de mando: la jefatura de la jefatura no ve el dato. Si el id objetivo no está
    en el directorio, permitido queda en true para que saldo_vacaciones o
    estado_solicitudes informen que ese id no existe, sin filtrar un dato real.

    Args:
        consultante_id: Id de quien pregunta, formato C-001. Vacío o desconocido niega el acceso.
        objetivo_id: Id de la persona cuyo saldo o trámite se quiere ver, formato C-001.

    Returns:
        Dict con politica "POL-07", permitido (bool) y motivo
        (propio_consultante, jefatura_directa, fuera_de_alcance, sin_consultante,
        consultante_desconocido u objetivo_no_resuelto). Si permitido es false,
        incluye error, listo para derivar a Personas. Si el objetivo existe,
        incluye objetivo_id canónico.
    """
    if not (consultante_id or "").strip():
        return {
            "permitido": False,
            "politica": "POL-07",
            "motivo": "sin_consultante",
            "error": (
                "POL-07: no hay un consultante identificado. "
                "No se entrega información individual. "
                "Deriva al área de Personas, personas@lumenretail.example."
            ),
        }

    consultante = _colaborador_por_id(consultante_id)
    if consultante is None:
        return {
            "permitido": False,
            "politica": "POL-07",
            "motivo": "consultante_desconocido",
            "error": (
                f"POL-07: no existe el consultante '{consultante_id}'. "
                "No se entrega información individual. "
                "Deriva al área de Personas, personas@lumenretail.example."
            ),
        }

    objetivo = _colaborador_por_id(objetivo_id)
    if objetivo is None:
        return {"permitido": True, "politica": "POL-07", "motivo": "objetivo_no_resuelto"}

    if consultante["id"].lower() == objetivo["id"].lower():
        return {
            "permitido": True,
            "politica": "POL-07",
            "motivo": "propio_consultante",
            "objetivo_id": objetivo["id"],
        }

    if (objetivo.get("jefatura_id") or "").lower() == consultante["id"].lower():
        return {
            "permitido": True,
            "politica": "POL-07",
            "motivo": "jefatura_directa",
            "objetivo_id": objetivo["id"],
        }

    misma_area = _normalizar(consultante["area"]) == _normalizar(objetivo["area"])
    if misma_area:
        jefatura = objetivo.get("jefatura_id") or "sin jefatura registrada"
        detalle = (
            f"POL-07: {consultante['nombre']} no es la jefatura directa de {objetivo['nombre']}. "
            f"Comparten el área {objetivo['area']}; ese dato solo puede verlo su jefatura directa "
            f"({jefatura}) o el propio colaborador. "
            "Deriva al área de Personas, personas@lumenretail.example."
        )
    else:
        detalle = (
            f"POL-07: {consultante['nombre']} ({consultante['area']}) no puede ver información individual de "
            f"{objetivo['nombre']} ({objetivo['area']}). No es su jefatura directa. "
            "Deriva al área de Personas, personas@lumenretail.example."
        )
    return {
        "permitido": False,
        "politica": "POL-07",
        "motivo": "fuera_de_alcance",
        "error": detalle,
        "objetivo_id": objetivo["id"],
    }


DECL_EVALUAR_ACCESO_POL07 = types.FunctionDeclaration(
    name="evaluar_acceso_pol07",
    description=(
        "Verifica POL-07 antes de entregar información individual: saldos, solicitudes y licencias. "
        "Llámalo en los primeros pasos del loop, después de tener un único id de la persona consultada "
        "y antes de saldo_vacaciones o estado_solicitudes. "
        "También llámalo cuando el dato sea del propio consultante: la verificación queda hecha y permitido vuelve true. "
        "consultante_id es quien pregunta (la línea '[Consulta de: C-00X ...]'). objetivo_id es la persona del dato. "
        "Los dos ids van en formato C-001. Si solo hay un nombre, resuélvelo antes con buscar_colaborador y no llames esta tool con homónimos. "
        "La regla es estricta. permitido es true solo si ambos ids son la misma persona (motivo propio_consultante) "
        "o si consultante_id es exactamente el jefatura_id del objetivo (motivo jefatura_directa). "
        "Un equipo son quienes comparten área, y eso no alcanza para ver el dato: un compañero de área no es la jefatura directa. "
        "No subas la cadena. La jefatura de la jefatura no tiene acceso. "
        "Felipe Araya (C-006) no ve a Matías Soto (C-004): comparten Operaciones, y la jefatura directa de Matías es Rodrigo Fuentes (C-002). "
        "Andrés Castillo (C-008, Dirección) ve a Felipe porque es su jefatura_id, y no ve a Rodrigo, que reporta a Felipe. "
        "No la uses para explicar el texto de la política (buscar_politica con tema 'privacidad'), ni para contar días hábiles, "
        "ni como reemplazo de saldo_vacaciones o estado_solicitudes: esta tool no trae cifras ni trámites. "
        "Devuelve politica 'POL-07', permitido (bool) y motivo. "
        "Si el objetivo existe, también objetivo_id. Si permitido es false, error explica el límite y pide derivar a "
        "personas@lumenretail.example: no llames después a saldo_vacaciones ni a estado_solicitudes, y no reintentes con otro id. "
        "motivo objetivo_no_resuelto significa que el id no está en el directorio: ahí sí puedes llamar a la tool de datos para que informe el id inválido. "
        "Si consultante_id viene vacío o no existe, permitido es false."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "consultante_id": {
                "type": "string",
                "description": (
                    "Id de quien pregunta, formato C-001, el de la línea '[Consulta de: ...]'. "
                    "No envíes el nombre ni el id de la persona consultada."
                ),
            },
            "objetivo_id": {
                "type": "string",
                "description": (
                    "Id de la persona cuyo saldo, solicitud o licencia se quiere ver, formato C-001. "
                    "Tiene que ser la única coincidencia ya resuelta. No envíes un nombre."
                ),
            },
        },
        "required": ["consultante_id", "objetivo_id"],
    },
)


def recortar_licencias_para_jefatura(resultado: dict) -> dict:
    """Deja una licencia médica en periodo y estado cuando la ve la jefatura directa.

    El resto de solicitudes (vacaciones, permiso, teletrabajo) se conserva completo.
    Si la consulta es del propio colaborador, no uses esta tool: él puede ver el
    comentario que devuelve estado_solicitudes.

    Args:
        resultado: Dict de estado_solicitudes, con colaborador_id, total y solicitudes.

    Returns:
        El mismo dict, con cada licencia_medica reducida a id, colaborador_id, tipo,
        fecha_inicio, fecha_fin, dias, estado y aprobador_id. Sin comentario ni diagnóstico.
        Si resultado no trae solicitudes, {"error": ...}.
    """
    if not isinstance(resultado, dict) or "solicitudes" not in resultado:
        return {
            "error": (
                "resultado debe ser el dict completo de estado_solicitudes, con la lista solicitudes. "
                "No envíes un saldo ni un texto suelto."
            )
        }

    solicitudes = []
    for solicitud in resultado.get("solicitudes") or []:
        if isinstance(solicitud, dict) and solicitud.get("tipo") == "licencia_medica":
            solicitudes.append({
                "id": solicitud.get("id"),
                "colaborador_id": solicitud.get("colaborador_id"),
                "tipo": "licencia_medica",
                "fecha_inicio": solicitud.get("fecha_inicio"),
                "fecha_fin": solicitud.get("fecha_fin"),
                "dias": solicitud.get("dias"),
                "estado": solicitud.get("estado"),
                "aprobador_id": solicitud.get("aprobador_id"),
            })
        else:
            solicitudes.append(solicitud)
    return {**resultado, "solicitudes": solicitudes}


DECL_RECORTAR_LICENCIAS = types.FunctionDeclaration(
    name="recortar_licencias_para_jefatura",
    description=(
        "Aplica la parte sensible de POL-07 a una licencia médica ya obtenida con estado_solicitudes. "
        "Úsala después de esa tool, y solo cuando evaluar_acceso_pol07 devolvió motivo jefatura_directa: "
        "quien pregunta no es el titular, es su jefatura directa. "
        "A esa jefatura se le informa el periodo de ausencia, el estado y el aprobador_id, nunca el diagnóstico ni el comentario. "
        "Pasa en resultado el dict completo que devolvió estado_solicitudes (colaborador_id, total y solicitudes), no un resumen escrito por ti. "
        "Cada item con tipo licencia_medica vuelve solo con id, colaborador_id, tipo, fecha_inicio, fecha_fin, dias, estado y aprobador_id. "
        "Vacaciones, permiso administrativo y teletrabajo se mantienen como llegaron, comentario incluido. "
        "No la llames cuando el consultante pide sus propias licencias: el titular puede ver lo que trajo estado_solicitudes. "
        "No la uses para decidir si hay acceso (evaluar_acceso_pol07), ni para buscar la solicitud (estado_solicitudes), "
        "ni para leer la regla general de licencias (buscar_politica). "
        "Si resultado no es ese dict o no trae la clave solicitudes, la respuesta es {\"error\": ...}: no inventes fechas ni estados. "
        "Cita únicamente los campos que vuelvan. Si no queda comentario, no lo reconstruyas."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "resultado": {
                "type": "object",
                "description": (
                    "Dict completo devuelto por estado_solicitudes. "
                    "Debe incluir colaborador_id, total y solicitudes. "
                    "Cada solicitud puede traer id, colaborador_id, tipo, fecha_inicio, fecha_fin, dias, estado, aprobador_id y comentario."
                ),
                "properties": {
                    "colaborador_id": {"type": "string"},
                    "total": {"type": "integer"},
                    "solicitudes": {"type": "array", "items": {"type": "object"}},
                },
                "required": ["solicitudes"],
            },
        },
        "required": ["resultado"],
    },
)


def buscar_colaborador(nombre_o_id: str) -> dict:
    """Busca colaboradores por id exacto (C-001) o por coincidencia parcial de nombre.

    Si nombre_o_id es "*", devuelve el directorio completo.
    Cada coincidencia trae solo id, nombre, cargo, área y jefatura_id.
    No incluye saldo, días tomados, correo, fecha de ingreso ni modalidad.
    Devuelve {"coincidencias": [...]} (puede haber varias, p. ej. dos "Camila") o {"error": ...}.
    """
    consulta = nombre_o_id.strip()
    if consulta == "*":
        return {"coincidencias": [_ficha_directorio(c) for c in COLABORADORES]}
    q = _normalizar(consulta)
    if not q:
        return {"error": "Debes indicar un nombre o un id"}
    por_id = [c for c in COLABORADORES if c["id"].lower() == q]
    if por_id:
        return {"coincidencias": [_ficha_directorio(c) for c in por_id]}
    por_nombre = [c for c in COLABORADORES if q in _normalizar(c["nombre"])]
    if not por_nombre:
        return {"error": f"No se encontró ningún colaborador que coincida con '{nombre_o_id}'"}
    return {"coincidencias": [_ficha_directorio(c) for c in por_nombre]}


DECL_BUSCAR_COLABORADOR = types.FunctionDeclaration(
    name="buscar_colaborador",
    description=("Busca colaboradores por id (formato C-001) o por nombre (parcial, sin distinguir tildes). "
                 "Si nombre_o_id es '*', devuelve el directorio completo. "
                 "Cada coincidencia trae solo id, nombre, cargo, área y jefatura_id. "
                 "No incluye saldo de vacaciones, días tomados, correo, fecha de ingreso ni modalidad: "
                 "esos datos individuales no salen de esta tool (POL-07). "
                 "Si hay más de una coincidencia, pregunta al usuario a cuál se refiere antes de seguir, "
                 "indicando nombre, cargo y área, sin saldos ni solicitudes."),
    parameters_json_schema={
        "type": "object",
        "properties": {"nombre_o_id": {"type": "string", "description": "Id (C-001), nombre o apellido del colaborador, o '*' para listar a todos"}},
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
        "POL-07 se aplica antes de devolverte el saldo: solo el propio colaborador o la persona indicada en su jefatura_id. "
        "Compartir área no autoriza. No se recorre la cadena de mando: la jefatura de esa jefatura no tiene acceso. "
        "Si la respuesta es un error que cita POL-07, no inventes cifras y deriva a personas@lumenretail.example. "
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
        "POL-07 se aplica antes de devolverte las solicitudes: solo el propio colaborador o la persona indicada en su jefatura_id. "
        "Compartir área no autoriza. No se recorre la cadena de mando: la jefatura de esa jefatura no tiene acceso. "
        "Si la respuesta es un error que cita POL-07, no inventes trámites y deriva a personas@lumenretail.example. "
        "El parámetro tipo es opcional. Omítelo, o envíalo vacío, para traer todas las solicitudes de esa persona. "
        "Si lo envías, debe ser exactamente uno de: vacaciones, permiso_administrativo, licencia_medica, teletrabajo. "
        "No la uses para el saldo disponible (saldo_vacaciones), ni para la regla de la política (buscar_politica), "
        "ni para calcular días hábiles de un rango (dias_habiles_entre). "
        "Devuelve colaborador_id, total (cantidad de solicitudes que cumplen el filtro; puede ser 0) y solicitudes, "
        "una lista de dicts con id (S-2026-000), colaborador_id, tipo, fecha_inicio, fecha_fin, dias, estado "
        "(aprobada, pendiente, en_revision o rechazada), aprobador_id y comentario. "
        "Responde solo con esos campos. Si estado es rechazada o en_revision, incluye el comentario: suele explicar el motivo. "
        "Una licencia médica es dato sensible (POL-07): si quien consulta es la jefatura directa, la respuesta de esa solicitud trae periodo, estado y aprobador_id, sin comentario ni diagnóstico. "
        "Al propio colaborador puedes citar lo que venga en la solicitud. "
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

    Una sola palabra que aparece únicamente en el cuerpo del texto (1 punto)
    no alcanza para devolver la política. Hace falta un acierto en el título,
    en los tags, o más de una palabra en el cuerpo. Así, "acoso laboral" no
    devuelve la de licencias médicas: "acoso" no aparece y "laboral" solo
    coincide con "laborales" en el texto.

    Args:
        tema: Pregunta o palabras clave, por ejemplo "vacaciones" o
            "trabajar remoto desde la casa".

    Returns:
        {"politicas": [{"id", "titulo", "texto"}, ...]} con como máximo las
        dos políticas de mayor puntaje. Si el tema no aporta palabras útiles,
        ninguna política suma puntos, o el único acierto es una palabra del
        cuerpo, {"error": ...}.
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
        # Un único acierto en el cuerpo (1 punto) no identifica la norma.
        # Con dos palabras, la que no aparece deja el puntaje en 1 y se descarta.
        if puntaje > _PESO_TEXTO:
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
        "Una sola palabra hallada únicamente en el cuerpo del texto no cuenta como coincidencia. "
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


_EXIGENCIAS_FECHA = (
    "Exigencias obligatorias de entrada: fecha_inicio y fecha_fin son ambas obligatorias. "
    "Cada una debe ser una fecha real de calendario, en texto, con formato AAAA-MM-DD "
    "(año de 4 dígitos, guion, mes de 2 dígitos, guion, día de 2 dígitos). "
    "Ejemplo válido: 2026-11-23. "
    "No se aceptan DD/MM/AAAA, DD-MM-AAAA, AAAAMMDD ni cadenas de dígitos. "
    "fecha_fin debe ser igual o posterior a fecha_inicio. "
    "Si un argumento no cumple ese formato, esta tool no interpreta el texto, no lo completa "
    "y no asume ningún rango de fechas."
)


def _validar_fecha(campo: str, valor) -> tuple[date | None, str | None]:
    """Exige AAAA-MM-DD exacto. No convierte ni completa otros formatos."""
    if not isinstance(valor, str) or not valor.strip():
        return None, (
            f"'{campo}' es obligatorio y debe ser un texto en formato AAAA-MM-DD. "
            f"Se recibió {valor!r}."
        )
    texto = valor.strip()
    if not _FECHA_ISO.fullmatch(texto):
        return None, (
            f"'{campo}' no tiene formato AAAA-MM-DD. Se recibió '{texto}'. "
            "No se interpreta ni se completa como fecha."
        )
    try:
        return date.fromisoformat(texto), None
    except ValueError:
        return None, (
            f"'{campo}' tiene la forma AAAA-MM-DD pero no es una fecha de calendario. "
            f"Se recibió '{texto}'."
        )


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
        Si algún argumento no es una fecha AAAA-MM-DD válida, {"error": ...}
        con la explicación y las exigencias de formato, sin calcular un rango.
        Si fecha_fin es anterior a fecha_inicio, {"error": ...}.
    """
    inicio, error_inicio = _validar_fecha("fecha_inicio", fecha_inicio)
    fin, error_fin = _validar_fecha("fecha_fin", fecha_fin)
    if error_inicio or error_fin:
        detalle = " ".join(mensaje for mensaje in (error_inicio, error_fin) if mensaje)
        return {"error": f"{detalle} {_EXIGENCIAS_FECHA}"}
    if fin < inicio:
        return {
            "error": (
                "fecha_fin no puede ser anterior a fecha_inicio. "
                f"Se recibió fecha_inicio='{inicio.isoformat()}' y fecha_fin='{fin.isoformat()}'. "
                f"{_EXIGENCIAS_FECHA}"
            )
        }

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
        "Si quien pregunta escribió una fecha literal que no está ya en AAAA-MM-DD "
        "(27/11/2026, 27-11-2026, 20261123 o una cadena de dígitos), pásala tal cual en el argumento. "
        "No la conviertas, no la completes y no inventes fecha_inicio ni fecha_fin. "
        "Solo puedes traducir a AAAA-MM-DD las expresiones relativas ya definidas: mañana, pasado mañana, "
        "en N días, esta semana y la próxima semana. "
        "fecha_fin debe ser igual o posterior a fecha_inicio. Un mismo día hábil y no feriado cuenta como 1. "
        "Devuelve fecha_inicio, fecha_fin, dias_habiles (entero) y feriados_en_rango: lista de fechas ISO de feriados "
        "que cayeron de lunes a viernes dentro del rango. Un feriado en sábado o domingo no entra en esa lista y tampoco suma como hábil. "
        "Si el formato es inválido, no calcula ningún rango y responde {\"error\": ...} con la explicación "
        "y las exigencias obligatorias de entrada. En ese caso transmite ese error y pide las fechas de nuevo. "
        "No reintentes con un rango supuesto ni estimes el número de días por tu cuenta."
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
    "etiqueta_consultante": etiqueta_consultante,
    "evaluar_acceso_pol07": evaluar_acceso_pol07,
    "buscar_colaborador": buscar_colaborador,
    "saldo_vacaciones": saldo_vacaciones,
    "estado_solicitudes": estado_solicitudes,
    "recortar_licencias_para_jefatura": recortar_licencias_para_jefatura,
    "buscar_politica": buscar_politica,
    "dias_habiles_entre": dias_habiles_entre,
}
DECLARACIONES = [
    DECL_ETIQUETA_CONSULTANTE,
    DECL_EVALUAR_ACCESO_POL07,
    DECL_BUSCAR_COLABORADOR,
    DECL_SALDO_VACACIONES,
    DECL_ESTADO_SOLICITUDES,
    DECL_RECORTAR_LICENCIAS,
    DECL_BUSCAR_POLITICA,
    DECL_DIAS_HABILES,
]
TOOLS = [types.Tool(function_declarations=DECLARACIONES)]
