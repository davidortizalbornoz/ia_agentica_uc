"""Tests del loop agéntico con el modelo falso (sin red, sin key).
Fallan con NotImplementedError hasta que completes `ejecutar` y `resumir` en agent.py."""
import pytest

import agent
import cliente
from tests.fake_modelo import fake_generar


@pytest.fixture(autouse=True)
def modelo_falso(monkeypatch):
    monkeypatch.setattr(cliente, "generar", fake_generar)
    monkeypatch.setattr(agent, "PAUSA", 0)


def test_loop_ejecuta_tool_y_termina():
    r = agent.ejecutar("¿Cuántos días de vacaciones le quedan a Rodrigo Fuentes?", usuario="C-006", verbose=False)
    assert "buscar_colaborador" in r["tools_usadas"]
    assert r["respuesta"] and not r["cortado"]
    assert r["llamadas"] >= 2
    assert r["traza"][0]["resultado"]["coincidencias"][0]["id"] == "C-002"


def test_loop_respeta_limite_de_iteraciones():
    r = agent.ejecutar("¿Cuántos días de vacaciones le quedan a Rodrigo Fuentes?", usuario="C-006", max_iter=1, verbose=False)
    assert r["cortado"] is True
    assert r["respuesta"] and "TODO" not in r["respuesta"], "la respuesta al cortarse debe ser controlada"
    assert r["llamadas"] == 1


def test_loop_convierte_error_de_tool_en_resultado(monkeypatch):
    def rota(nombre_o_id):
        raise RuntimeError("base de datos de Personas no disponible")
    monkeypatch.setitem(agent.REGISTRO, "buscar_colaborador", rota)
    r = agent.ejecutar("¿Cuántos días de vacaciones le quedan a Rodrigo Fuentes?", verbose=False)
    assert "error" in r["traza"][0]["resultado"]
    assert "no disponible" in r["respuesta"].lower() or "personas" in r["respuesta"].lower()


def test_resumir_devuelve_objeto_validado():
    res = {"respuesta": "Te quedan 9 días según el registro de Personas.", "tools_usadas": ["saldo_vacaciones"]}
    resumen = agent.resumir("¿Cuántos días de vacaciones me quedan?", res)
    assert isinstance(resumen, agent.ResumenConsulta)
    assert isinstance(resumen.requiere_accion_humana, bool)
