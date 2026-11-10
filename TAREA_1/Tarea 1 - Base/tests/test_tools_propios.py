"""Tests propios de las ocho tools declaradas. Corren sin red y sin key."""
import math
from datetime import date

import tools

_FICHA = {"id", "nombre", "cargo", "area", "jefatura_id"}
_TOOLS = (
    "etiqueta_consultante",
    "evaluar_acceso_pol07",
    "buscar_colaborador",
    "saldo_vacaciones",
    "estado_solicitudes",
    "recortar_licencias_para_jefatura",
    "buscar_politica",
    "dias_habiles_entre",
)


def test_saldo_vacaciones_devuelve_nombre_y_sin_nota_si_tiene_antiguedad():
    r = tools.saldo_vacaciones("c-001")
    assert r["colaborador_id"] == "C-001"
    assert r["nombre"] == "Camila Rojas"
    assert r["antiguedad_anios"] >= 5
    assert "nota" not in r


def test_saldo_vacaciones_antiguedad_usa_la_fecha_actual():
    r = tools.saldo_vacaciones("C-003")
    ingreso = date.fromisoformat("2025-11-02")
    exactos = (date.today() - ingreso).days / 365.25
    esperado = round(exactos, 1)
    if exactos < 1 <= esperado:
        esperado = math.floor(exactos * 10) / 10
    assert r["antiguedad_anios"] == esperado
    if exactos < 1:
        assert "anticipo" in r["nota"] and "POL-01" in r["nota"]
    else:
        assert "nota" not in r


def test_saldo_vacaciones_id_vacio():
    assert "error" in tools.saldo_vacaciones("  ")


def test_estado_solicitudes_sin_tramites_devuelve_lista_vacia():
    r = tools.estado_solicitudes("C-008")
    assert r["colaborador_id"] == "C-008"
    assert r["total"] == 0 and r["solicitudes"] == []


def test_estado_solicitudes_normaliza_tipo():
    r = tools.estado_solicitudes("C-003", tipo="Permiso administrativo")
    assert r["total"] == 1
    assert r["solicitudes"][0]["id"] == "S-2026-048"
    assert r["solicitudes"][0]["tipo"] == "permiso_administrativo"


def test_estado_solicitudes_tipo_desconocido():
    assert "error" in tools.estado_solicitudes("C-001", tipo="paracaidismo")


def test_buscar_politica_devuelve_como_maximo_dos_y_solo_id_titulo_texto():
    r = tools.buscar_politica("vacaciones")
    assert 1 <= len(r["politicas"]) <= 2
    assert set(r["politicas"][0]) == {"id", "titulo", "texto"}


def test_buscar_politica_tema_sin_palabras_utiles():
    assert "error" in tools.buscar_politica("el de la")


def test_dias_habiles_no_lista_feriado_de_fin_de_semana():
    r = tools.dias_habiles_entre("2026-09-14", "2026-09-20")
    assert r["feriados_en_rango"] == ["2026-09-18"]
    assert "2026-09-19" not in r["feriados_en_rango"]


def test_dias_habiles_mismo_dia_habil_cuenta_uno():
    r = tools.dias_habiles_entre("2026-11-23", "2026-11-23")
    assert r["dias_habiles"] == 1
    assert r["fecha_inicio"] == "2026-11-23" and r["fecha_fin"] == "2026-11-23"


def test_dias_habiles_fecha_inexistente():
    assert "error" in tools.dias_habiles_entre("2026-02-31", "2026-03-01")


def test_dias_habiles_fin_de_semana_cuenta_cero():
    r = tools.dias_habiles_entre("2026-09-19", "2026-09-20")
    assert r["dias_habiles"] == 0
    assert r["feriados_en_rango"] == []


def test_dias_habiles_rango_invertido_explica_el_formato():
    r = tools.dias_habiles_entre("2026-11-27", "2026-11-23")
    assert "anterior" in r["error"]
    assert "AAAA-MM-DD" in r["error"]


# ---------------- etiqueta_consultante ----------------
def test_etiqueta_jefatura_lista_solo_reportes_directos():
    r = tools.etiqueta_consultante("c-006")
    assert r["colaborador_id"] == "C-006"
    assert r["nombre"] == "Felipe Araya"
    assert r["area"] == "Operaciones"
    assert r["es_jefatura_directa"] is True
    assert [c["id"] for c in r["reportes_directos"]] == ["C-002"]
    assert "C-004" not in r["etiqueta"]
    assert all(set(ficha) == _FICHA for ficha in r["reportes_directos"])


def test_etiqueta_sin_personas_a_cargo():
    r = tools.etiqueta_consultante("C-001")
    assert r["es_jefatura_directa"] is False
    assert r["reportes_directos"] == []
    assert r["etiqueta"].startswith("C-001 Camila Rojas")
    assert "sin personas a cargo" in r["etiqueta"]


def test_etiqueta_id_vacio_o_inexistente():
    assert "formato C-001" in tools.etiqueta_consultante("  ")["error"]
    assert "C-999" in tools.etiqueta_consultante("C-999")["error"]


# ---------------- evaluar_acceso_pol07 ----------------
def test_acceso_propio_consultante():
    r = tools.evaluar_acceso_pol07("c-001", "C-001")
    assert r["permitido"] is True
    assert r["politica"] == "POL-07"
    assert r["motivo"] == "propio_consultante"
    assert r["objetivo_id"] == "C-001"
    assert "error" not in r


def test_acceso_jefatura_directa():
    r = tools.evaluar_acceso_pol07("C-005", "C-001")
    assert r["permitido"] is True
    assert r["motivo"] == "jefatura_directa"
    assert r["objetivo_id"] == "C-001"


def test_acceso_misma_area_no_autoriza():
    r = tools.evaluar_acceso_pol07("C-006", "C-004")
    assert r["permitido"] is False
    assert r["motivo"] == "fuera_de_alcance"
    assert "POL-07" in r["error"]
    assert "Operaciones" in r["error"]


def test_acceso_no_sube_la_cadena_de_mando():
    ajeno = tools.evaluar_acceso_pol07("C-008", "C-002")
    assert ajeno["permitido"] is False
    assert ajeno["motivo"] == "fuera_de_alcance"
    directo = tools.evaluar_acceso_pol07("C-008", "C-006")
    assert directo["permitido"] is True
    assert directo["motivo"] == "jefatura_directa"


def test_acceso_sin_consultante_o_desconocido():
    sin_consultante = tools.evaluar_acceso_pol07("  ", "C-001")
    assert sin_consultante["permitido"] is False
    assert sin_consultante["motivo"] == "sin_consultante"
    assert "POL-07" in sin_consultante["error"]
    desconocido = tools.evaluar_acceso_pol07(None, "C-001")
    assert desconocido["motivo"] == "sin_consultante"
    inexistente = tools.evaluar_acceso_pol07("C-999", "C-001")
    assert inexistente["permitido"] is False
    assert inexistente["motivo"] == "consultante_desconocido"


def test_acceso_objetivo_inexistente_deja_pasar_el_id():
    r = tools.evaluar_acceso_pol07("C-001", "C-999")
    assert r["permitido"] is True
    assert r["motivo"] == "objetivo_no_resuelto"
    assert "error" not in r


# ---------------- buscar_colaborador ----------------
def test_buscar_colaborador_por_id_solo_ficha_publica():
    ficha = tools.buscar_colaborador("c-002")["coincidencias"][0]
    assert ficha["nombre"] == "Rodrigo Fuentes"
    assert ficha["jefatura_id"] == "C-006"
    assert set(ficha) == _FICHA


def test_buscar_colaborador_directorio_completo():
    coincidencias = tools.buscar_colaborador("*")["coincidencias"]
    assert len(coincidencias) == len(tools.COLABORADORES) == 10
    assert all(set(ficha) == _FICHA for ficha in coincidencias)


def test_buscar_colaborador_camila_es_ambigua():
    ids = {c["id"] for c in tools.buscar_colaborador("camila")["coincidencias"]}
    assert ids == {"C-001", "C-009", "C-010"}


def test_buscar_colaborador_vacio_o_inexistente():
    assert "nombre o un id" in tools.buscar_colaborador("   ")["error"]
    assert "Zzzz" in tools.buscar_colaborador("Zzzz")["error"]


# ---------------- recortar_licencias_para_jefatura ----------------
def test_recortar_licencia_medica_quita_comentario():
    original = tools.estado_solicitudes("C-002")
    recortado = tools.recortar_licencias_para_jefatura(original)
    licencia = recortado["solicitudes"][0]
    assert recortado["colaborador_id"] == "C-002" and recortado["total"] == 1
    assert licencia["id"] == "S-2026-037"
    assert licencia["estado"] == "aprobada"
    assert licencia["aprobador_id"] == "C-006"
    assert set(licencia) == {
        "id", "colaborador_id", "tipo", "fecha_inicio", "fecha_fin", "dias", "estado", "aprobador_id",
    }
    assert "comentario" in original["solicitudes"][0]


def test_recortar_conserva_comentario_de_otros_tipos():
    original = tools.estado_solicitudes("C-004", tipo="vacaciones")
    recortado = tools.recortar_licencias_para_jefatura(original)
    assert recortado["solicitudes"][0]["tipo"] == "vacaciones"
    assert recortado["solicitudes"][0]["comentario"] == original["solicitudes"][0]["comentario"]


def test_recortar_lista_vacia_se_conserva():
    r = tools.recortar_licencias_para_jefatura(tools.estado_solicitudes("C-008"))
    assert r["total"] == 0 and r["solicitudes"] == []


def test_recortar_sin_clave_solicitudes():
    assert "solicitudes" in tools.recortar_licencias_para_jefatura({"colaborador_id": "C-001"})["error"]
    assert "error" in tools.recortar_licencias_para_jefatura("texto")


# ---------------- buscar_politica (umbral) ----------------
def test_buscar_politica_un_acierto_solo_en_el_cuerpo_no_alcanza():
    assert "error" in tools.buscar_politica("acoso laboral")


def test_buscar_politica_privacidad():
    r = tools.buscar_politica("privacidad")
    assert r["politicas"][0]["id"] == "POL-07"
    assert "jefatura directa" in r["politicas"][0]["texto"]


# ---------------- declaraciones ----------------
def test_cada_tool_declarada_esta_en_el_registro():
    nombres = [d.name for d in tools.DECLARACIONES]
    assert nombres == list(_TOOLS)
    assert set(nombres) == set(tools.REGISTRO)
    for declaracion in tools.DECLARACIONES:
        assert declaracion.description.strip()
        assert "TODO" not in declaracion.description
        esquema = declaracion.parameters_json_schema
        assert esquema["type"] == "object"
        assert esquema["required"]
