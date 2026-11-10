"""Tests de las tools (sin red, sin key). En el repo base pasan solo los de `buscar_colaborador`;
los demás fallan con NotImplementedError hasta que implementes cada tool."""
from datetime import date

import tools


# ---------------- buscar_colaborador (ejemplo implementado) ----------------
def test_buscar_por_id():
    r = tools.buscar_colaborador("c-001")
    assert r["coincidencias"][0]["nombre"] == "Camila Rojas"


def test_buscar_por_nombre_sin_tilde_devuelve_varias():
    r = tools.buscar_colaborador("camila")
    assert {c["id"] for c in r["coincidencias"]} == {"C-001", "C-009", "C-010"}
    assert tools.buscar_colaborador("Matias")["coincidencias"][0]["id"] == "C-004"


def test_buscar_inexistente():
    assert "error" in tools.buscar_colaborador("Zzzz")


# ---------------- saldo_vacaciones ----------------
def test_saldo_vacaciones_normal():
    r = tools.saldo_vacaciones("C-001")
    assert r["dias_disponibles"] == 9 and r["dias_tomados_2026"] == 6
    assert r["antiguedad_anios"] >= 5


def test_saldo_vacaciones_menos_de_un_anio_tiene_nota():
    r = tools.saldo_vacaciones("C-003")
    assert r["dias_disponibles"] == 0
    ingreso = date.fromisoformat("2025-11-02")
    if (date.today() - ingreso).days / 365.25 < 1:
        assert "nota" in r
    else:
        assert "nota" not in r


def test_saldo_vacaciones_inexistente():
    assert "error" in tools.saldo_vacaciones("C-999")


# ---------------- estado_solicitudes ----------------
def test_estado_solicitudes_todas():
    r = tools.estado_solicitudes("C-001")
    assert r["total"] == 2 and {s["id"] for s in r["solicitudes"]} == {"S-2026-041", "S-2026-042"}


def test_estado_solicitudes_filtra_por_tipo():
    r = tools.estado_solicitudes("C-001", tipo="vacaciones")
    assert r["total"] == 1 and r["solicitudes"][0]["estado"] == "aprobada"


def test_estado_solicitudes_inexistente():
    assert "error" in tools.estado_solicitudes("C-999")


# ---------------- buscar_politica ----------------
def test_buscar_politica_vacaciones_primero():
    r = tools.buscar_politica("vacaciones")
    assert r["politicas"][0]["id"] == "POL-01"


def test_buscar_politica_remoto_encuentra_teletrabajo():
    r = tools.buscar_politica("¿puedo trabajar remoto desde la casa?")
    assert "POL-04" in [p["id"] for p in r["politicas"]]


def test_buscar_politica_sin_resultados():
    assert "error" in tools.buscar_politica("paracaidismo")


# ---------------- dias_habiles_entre ----------------
def test_dias_habiles_semana_normal():
    assert tools.dias_habiles_entre("2026-11-23", "2026-11-27")["dias_habiles"] == 5


def test_dias_habiles_con_feriado():
    r = tools.dias_habiles_entre("2026-09-14", "2026-09-20")   # viernes 18/09 feriado, sábado 19/09 también
    assert r["dias_habiles"] == 4 and "2026-09-18" in r["feriados_en_rango"]


def test_dias_habiles_errores():
    assert "error" in tools.dias_habiles_entre("2026-11-27", "2026-11-23")
    assert "error" in tools.dias_habiles_entre("27/11/2026", "2026-11-28")


# ---------------- registro ----------------
def test_registro_y_declaraciones_consistentes():
    """Toda tool declarada debe estar implementada en REGISTRO y viceversa (si no, el agente se rompe)."""
    declaradas = {d.name for t in tools.TOOLS for d in t.function_declarations}
    assert declaradas == set(tools.REGISTRO)
    assert len(tools.REGISTRO) >= 4, "Debes implementar al menos 3 tools además de buscar_colaborador"
    for d in (d for t in tools.TOOLS for d in t.function_declarations):
        assert "TODO" not in d.description, f"La descripción de {d.name} sigue con TODO"
