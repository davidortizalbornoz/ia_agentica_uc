"""Ejecuta el set de casos contra el agente y guarda los resultados (evidencia para el informe).

Uso:
    python run_eval.py                       # corre casos/casos.json con el modelo real (requiere .env con GEMINI_API_KEY)
    python run_eval.py casos/mis_casos.json  # otro archivo de casos
    python run_eval.py --mock                # usa el modelo falso de tests/fake_modelo.py (sin red, sin key): para probar el flujo
    python run_eval.py --sin-resumen         # no pide la salida estructurada (útil mientras no implementas resumir())

Formato de cada caso (lista JSON):
    {"id": 1, "usuario": "C-001", "pregunta": "...", "tipo": "normal|encadenado|ambiguo|sin_datos|politica|error|privacidad",
     "esperado_contiene": ["texto1", "texto2"]}
`esperado_contiene` es una verificación de orientación (todos los textos deben aparecer en la respuesta, sin distinguir
mayúsculas). El análisis de verdad lo haces tú en el informe, leyendo la traza.
"""
import argparse
import datetime as dt
import json
import pathlib
import sys

parser = argparse.ArgumentParser()
parser.add_argument("casos", nargs="?", default="casos/casos.json")
parser.add_argument("--mock", action="store_true", help="usar el modelo falso (sin llamadas reales)")
parser.add_argument("--sin-resumen", action="store_true", help="no pedir la salida estructurada")
parser.add_argument("--max", type=int, default=None, help="correr solo los primeros N casos")
args = parser.parse_args()

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import cliente  # noqa: E402

if args.mock:
    from tests.fake_modelo import fake_generar
    cliente.generar = fake_generar
    print("[modo mock: modelo falso, sin llamadas reales]")

import agent  # noqa: E402  (después del parche, para que use cliente.generar parchado)

casos = json.loads(pathlib.Path(args.casos).read_text(encoding="utf-8"))
if args.max:
    casos = casos[: args.max]

pathlib.Path("resultados").mkdir(exist_ok=True)
salida = pathlib.Path("resultados") / f"eval_{dt.datetime.now():%Y%m%d_%H%M%S}{'_mock' if args.mock else ''}.jsonl"

filas = []
with salida.open("w", encoding="utf-8") as f:
    for c in casos:
        print(f"\n[{c['id']}] ({c.get('tipo', '?')}) usuario={c.get('usuario')} :: {c['pregunta']}")
        try:
            res = agent.ejecutar(c["pregunta"], usuario=c.get("usuario"), verbose=True)
        except NotImplementedError as e:
            print(f"  >> {e}")
            res = {"respuesta": f"NO IMPLEMENTADO: {e}", "traza": [], "tools_usadas": [], "llamadas": 0,
                   "tokens_entrada": 0, "tokens_salida": 0, "costo_usd": 0.0, "cortado": False}
        resumen = None
        if not args.sin_resumen and not res["respuesta"].startswith("NO IMPLEMENTADO"):
            try:
                resumen = agent.resumir(c["pregunta"], res).model_dump()
            except NotImplementedError:
                resumen = "NO IMPLEMENTADO"
            except Exception as e:  # noqa: BLE001
                resumen = f"ERROR: {type(e).__name__}: {e}"
        esperado = c.get("esperado_contiene", [])
        ok = all(s.lower() in res["respuesta"].lower() for s in esperado) if esperado else None
        print(f"  -> {res['respuesta']}")
        if resumen:
            print(f"  resumen: {resumen}")
        fila = {"id": c["id"], "tipo": c.get("tipo"), "usuario": c.get("usuario"), "pregunta": c["pregunta"],
                "respuesta": res["respuesta"], "tools_usadas": res["tools_usadas"], "traza": res["traza"],
                "llamadas": res["llamadas"], "tokens_entrada": res["tokens_entrada"], "tokens_salida": res["tokens_salida"],
                "costo_usd": res["costo_usd"], "cortado": res["cortado"], "esperado_contiene": esperado, "ok": ok,
                "resumen": resumen, "modelo": cliente.MODEL, "timestamp": dt.datetime.now().isoformat(timespec="seconds")}
        if "resuelve" in c:
            fila["resuelve"] = c["resuelve"]
        f.write(json.dumps(fila, ensure_ascii=False) + "\n")
        filas.append(fila)

mostrar_resuelve = any("resuelve" in r for r in filas)
resuelve_txt = [r.get("resuelve") or "-" for r in filas]
ancho_resuelve = max([len("resuelve"), *(len(t) for t in resuelve_txt)], default=len("resuelve")) if mostrar_resuelve else None
encabezado = f"{'id':>3} {'tipo':<12} {'ok':<5} {'pasos':>5} {'tokens':>7} {'US$':>9}  "
if mostrar_resuelve:
    encabezado += f"{'resuelve':<{ancho_resuelve}}  "
encabezado += "tools"
lineas = [encabezado]
for r, resuelve in zip(filas, resuelve_txt):
    ok = {True: "sí", False: "NO", None: "-"}[r["ok"]]
    tools = " > ".join(r["tools_usadas"]) or "-"
    linea = (f"{r['id']:>3} {str(r['tipo']):<12} {ok:<5} {r['llamadas']:>5} {r['tokens_entrada'] + r['tokens_salida']:>7} "
             f"{r['costo_usd']:>9.5f}  ")
    if mostrar_resuelve:
        linea += f"{resuelve:<{ancho_resuelve}}  "
    linea += tools
    lineas.append(linea)
ancho = max((len(linea) for linea in lineas), default=100) if mostrar_resuelve else 100
print("\n" + "=" * ancho)
for linea in lineas:
    print(linea)
total_ok = sum(1 for r in filas if r["ok"])
con_esperado = sum(1 for r in filas if r["ok"] is not None)
print("=" * ancho)
print(f"{len(filas)} casos | {total_ok}/{con_esperado} cumplen 'esperado_contiene' | "
      f"{sum(r['llamadas'] for r in filas)} llamadas | costo estimado US${sum(r['costo_usd'] for r in filas):.5f}")
print(f"Resultados guardados en {salida}")
