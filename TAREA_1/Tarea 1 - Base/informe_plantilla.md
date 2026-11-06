# Tarea 1 · Informe

**Nombre:** …

**Modelo usado:** (lo imprime `cliente.py` en `logs/agente.log`)

Máximo 3 páginas. Sé concreto: una decisión bien justificada vale más que tres descritas.

## 1\. System prompt (requisito 1\)

- Versión final (puede ir como anexo) y **qué problema resolvió cada regla**: ¿qué hacía mal el agente antes de agregarla?  
- ¿Cómo resolviste la privacidad (POL-07) y las consultas ambiguas (dos "Camila")?

## 2\. Diseño de las tools (requisito 3\)

| Tool | Qué devuelve | Decisión de diseño que tomaste y por qué |
| :---- | :---- | :---- |
| … | … | … |

- ¿Tuviste que reescribir alguna descripción para que el modelo eligiera bien la tool? Muestra antes/después.  
- ¿Qué devuelven tus tools cuando fallan y cómo lo usa el agente?

## 3\. Loop agéntico y control (requisito 2\)

- Límite de iteraciones: qué valor usaste y qué responde el agente cuando se corta.  
- Manejo de errores de tools: muestra una traza (del `.jsonl` o del log) donde una tool falló.

## 4\. Salida estructurada (requisito 4\)

- Campos de `ResumenConsulta` y para qué los usaría el área de Personas. Un ejemplo real de salida.

## 5\. Evaluación (requisito 5\)

Tabla de los 10 casos (puedes pegarla desde el resumen que imprime `run_eval.py`):

| id | tipo | pregunta | tools usadas | pasos | ¿correcto? |
| :---- | :---- | :---- | :---- | :---- | :---- |

- **Al menos 2 fallas analizadas:** qué pasó, por qué (prompt, tool, modelo, datos) y qué cambiarías.  
- ¿Cuánto varían los resultados si corres los casos dos veces? (temperature=0 no garantiza determinismo).

## 6\. Costo

Tokens y costo estimado total de una corrida de los 10 casos (lo imprime `run_eval.py`). ¿Cuánto costaría al mes con 500 consultas diarias?

## 7\. Declaración de uso de IA

Qué herramientas de IA usaste, para qué partes, y qué partes escribiste y entiendes completamente.