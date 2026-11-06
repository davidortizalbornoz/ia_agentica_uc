# Tarea 1 · Asistente de Personas de Lumen Retail

Código base de la Tarea 1 del curso INF3880 – Inteligencia Artificial Agéntica (UC, 2026-2).
El enunciado completo, los requisitos y la rúbrica están en `Tarea 1 - Enunciado.md`.

## Instalación (5 minutos)

Requiere Python 3.11 o superior.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate      macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Crea tu archivo `.env` a partir del ejemplo y pega tu key **gratuita** de Google AI Studio
(la misma que usas en los prácticos; si no la tienes, créala en https://aistudio.google.com/apikey):

```bash
cp .env.example .env
```

> La key va solo en `.env`, que está en `.gitignore`. **Nunca** la escribas en el código, en el informe ni en el .zip.
> Recuerda que en el nivel gratuito Google puede usar los prompts para mejorar sus productos: no uses datos reales de personas.

## Estructura

```
Tarea 1/
├── cliente.py          # cliente Gemini, modelo con respaldo, reintentos, logging  → NO se modifica
├── tools.py            # tools: 1 implementada (buscar_colaborador) + 4 por implementar (mínimo 3)  → TODO
├── agent.py            # system prompt, loop agéntico y salida estructurada                        → TODO
├── run_eval.py         # corre casos/casos.json y guarda resultados/*.jsonl (evidencia)            → se usa tal cual
├── casos/casos.json    # 3 casos de ejemplo; debes llegar a 10                                     → TODO
├── datos/              # colaboradores, solicitudes, políticas y feriados (simulados)
├── tests/              # pytest: tools (sin red) y loop (con modelo falso)
├── informe_plantilla.md
└── .env.example
```

## Cómo trabajar

1. **Corre los tests** para ver el estado inicial (solo pasan los de la tool de ejemplo):
   ```bash
   pytest -q
   ```
2. **Implementa las tools** en `tools.py` (función + `FunctionDeclaration`) y agrégalas a `REGISTRO` y `DECLARACIONES`.
   Los tests de `tests/test_tools.py` te dicen si cada una se comporta como se espera.
3. **Completa el loop** en `agent.py` (TODO 2, 3 y 4) y pruébalo sin gastar llamadas:
   ```bash
   pytest -q tests/test_loop.py
   python run_eval.py --mock --sin-resumen
   ```
   El modo `--mock` usa un modelo falso con reglas fijas: verifica que tu loop ejecuta tools y termina, no la calidad de las respuestas.
4. **Escribe el system prompt** (TODO 1) y prueba con el modelo real:
   ```bash
   python run_eval.py --sin-resumen
   ```
5. **Implementa `resumir`** (TODO 5) y corre la evaluación completa. Cada corrida queda en `resultados/eval_<fecha>.jsonl` y
   los pasos del agente en `logs/agente.log`: esa es tu evidencia de ejecución.
6. **Completa `casos/casos.json`** hasta 10 casos (ver tipos en el enunciado) y analiza las fallas en el informe.

## Si algo falla

- `Falta GEMINI_API_KEY`: revisa que `.env` exista en esta carpeta y que la key esté completa.
- Error 429: límite por minuto del nivel gratuito; `cliente.generar` espera 20 s y reintenta. Si persiste, sube `PAUSA` en `agent.py` (por ejemplo a 3 segundos).
- Error 500/503: saturación del servidor; `cliente.generar` reintenta y cambia de modelo. Si todos fallan, espera unos minutos.
- `parameters_json_schema` no existe: actualiza el SDK (`pip install -U google-genai`).
