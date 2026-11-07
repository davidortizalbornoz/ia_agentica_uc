"""Tests propios de las cuatro tools implementadas. Corren sin red."""
import math
from datetime import date

import tools


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
