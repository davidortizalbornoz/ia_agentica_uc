# Ejecución

Para ejecutar el ejercicio 3 del loop manual con un handler que captura la excepción de la tool:

1. Clona el repositorio.

```bash
git clone https://github.com/davidortizalbornoz/ia_agentica_uc.git
cd ia_agentica_uc
```

2. Crea un archivo `.env` en la raíz del proyecto. Puedes partir de `.env.sample`:

```bash
cp .env.sample .env
```

3. Abre `.env` y completa `GEMINI_API_KEY`. `PREFERIDOS` es la lista de modelos, separados por coma y en orden de preferencia. `.env.sample` ya trae esa lista; se usa el primero que esté disponible en el proyecto.

4. Usa Python 3.13.5. El archivo `.python-version` de la raíz apunta al entorno de pyenv `ia_agentica_uc`, creado sobre esa versión. Clonar el repositorio no instala el intérprete ni el entorno: hay que tenerlos en la máquina.

```bash
pyenv install 3.13.5
pyenv virtualenv 3.13.5 ia_agentica_uc
```

`google-genai` pide Python 3.10 o superior, así que 3.13.5 es compatible. Si la consola ya tiene `PYENV_VERSION` definida (por ejemplo en 3.9.18), esa variable pisa a `.python-version`. Quítala antes de activar el entorno:

```bash
unset PYENV_VERSION
```

5. Activa el entorno e instala `google-genai` si aún no está. La llamada y el costo salen de `CLASE_1/parte_guiada/common.py` (`generar`, `costo_usd`). La key y `PREFERIDOS` se leen con `leer_clave` desde `CLASE_1/parte_guiada/entorno_local.py`. `consultar_stock_roto` sale de `3_ejercicio_contrato_roto.py`, que carga `3_ejercicio_funcion_rota.py`. `fecha_estimada_entrega` sale de `1_ejercicio_contrato.py`, que carga `1_ejercicio_funciones.py`.

```bash
pyenv activate ia_agentica_uc
pip install google-genai
```

6. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_3/ejercicios/3_ejercicio_loop_agentico_manual_robusto_handler.py"
```

`agente_manual` arma el loop en Python: el modelo decide, el script ejecuta la función y le devuelve el resultado, hasta que haya texto final o se cumpla `max_iter`. En este archivo el valor por defecto es `5`. `automatic_function_calling` va desactivado. Entre una interacción con tools y la siguiente hay una pausa de 2 segundos. `temperature` es 0.

El contrato junta dos funciones: `consultar_stock_roto` y `fecha_estimada_entrega`. La declaración que ve el modelo describe un stock disponible por SKU. El modelo nunca ve el cuerpo de `consultar_stock_roto`.

En `__main__` la consulta es la misma que en `3_ejercicio_loop_agentico_manual_force_error.py`: cuántas unidades de TAL-200 hay que importar para completar un pedido de 100. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Captura de la excepción y continuación del loop

En la primera vuelta el modelo pide `consultar_stock_roto` con `sku='TAL-200'`. Python resuelve el nombre en `FUNCIONES` y llama la función real. En `3_ejercicio_funcion_rota.py` la línea que corre sigue siendo `raise RuntimeError("Inventario no disponible")`. La función no cambia: el `raise` sale de `consultar_stock_roto` igual que en el script sin handler.

La cadena de esta corrida es:

1. `consultar_stock_roto` lanza `RuntimeError` en la línea 4 de `3_ejercicio_funcion_rota.py`.
2. El llamado `funciones[call.name](**args)` está en la línea 145 de `agente_manual`, dentro de un `try`.
3. `except Exception as e` (línea 146) atrapa el `RuntimeError`. `str(e)` vale `"Inventario no disponible"`.
4. La línea 147 asigna `resultado = {"error": str(e)}`. Ese dict ocupa el lugar del valor que la función habría devuelto.
5. Las trazas `Función:` y `Resultado:` sí corren. `types.Part.from_function_response` arma la respuesta con `response={"resultado": resultado}` (líneas 154-158).
6. El turno con `role="user"` vuelve al historial, hay pausa de 2 segundos y el loop entra en la interacción 2/5.
7. El modelo responde con texto, `agente_manual` retorna y `__main__` imprime tokens y costo. El proceso termina con código de salida 0.

Lo que recibe el modelo en el historial es:

```json
{"resultado": {"error": "Inventario no disponible"}}
```

La regla 3 del system prompt pide explicar un error cuando la herramienta devuelve un valor. Aquí la tool sí devuelve un valor: el `except` convirtió la excepción en ese dict. En la segunda vuelta el modelo dice que no pudo consultar el stock porque el inventario no está disponible, y propone verificar el código SKU o intentar más tarde. No inventa unidades. En esta corrida el texto final no nombra TAL-200: el SKU quedó en la llamada de la tool.

`except Exception` cubre lo que lance esa llamada: el `RuntimeError` de la función rota, y también un `KeyError` o un `TypeError` si el nombre o los argumentos no coinciden con `FUNCIONES`. Las guardas que hacen `raise SystemExit` (sin candidatos, sin nombre o sin argumentos) quedan fuera de ese `except`, porque `SystemExit` no hereda de `Exception`.

## Comparación del manejo de la excepción

Los dos scripts cargan el mismo contrato, la misma `consultar_stock_roto` y la misma pregunta. La diferencia está en las líneas que ejecutan la tool.

| | `3_ejercicio_loop_agentico_manual_force_error.py` | `3_ejercicio_loop_agentico_manual_robusto_handler.py` |
| --- | --- | --- |
| Llamado | Línea 142: `resultado = funciones[nombre](**args)`, sin `try`/`except` | Líneas 144-147: `try` / `resultado = funciones[call.name](**args)` / `except Exception as e` |
| Qué hace el `RuntimeError` | Sube por `agente_manual`, sale de `__main__` (línea 164) y llega al intérprete | Se detiene en el `except`. `resultado` pasa a ser `{"error": "Inventario no disponible"}` |
| Trazas `Función:` y `Resultado:` | No se imprimen: están debajo del llamado que lanza | Se imprimen. La traza previa avisa `RuntimeError capturado` |
| `from_function_response` | No se arma. El historial queda con el pedido de la función y sin respuesta de tool | Se arma con `{"resultado": {"error": "Inventario no disponible"}}` |
| Interacción 2/5 | No existe. No hay pausa de 2 segundos | El modelo recibe el error y cierra con texto |
| Costo en consola | No se imprime: el conteo está después de `agente_manual` y esa línea no se alcanza. `USO.append` de la vuelta 1 sí había corrido, pero el proceso ya murió | Se imprime. En esta corrida: 2 llamadas, 779 tokens de entrada, 55 de salida, ≈ US$0.00037 |
| Código de salida | 1, con traceback | 0 |
| Qué puede hacer el modelo | Nada con el fallo: la excepción reemplazó al valor de retorno | Aplicar la regla 3: explicar el problema y proponer un paso, sin inventar stock |

En `3_ejercicio_funcion_rota.py` la línea comentada `return RuntimeError("Inventario no disponible")` entregaría el objeto excepción como resultado y el loop de `force_error.py` seguiría, pero el modelo recibiría la representación de ese objeto, no un dict `{"error": "..."}`. El handler robusto deja el `raise` activo y traduce la excepción en el mismo lugar donde iría el resultado.

## Traza: loop sin captura

Salida de `3_ejercicio_loop_agentico_manual_force_error.py`. El traceback corta la interacción 1/5.

```text
Pregunta: Cuantas unidades del producto TAL-200 debo importar para cumplir un pedido de 100 unidades?
Interacciones máximas: 5
Tools:
[
  {
    "function_declarations": [
      {
        "description": "Consulta las unidades disponibles de un producto por su SKU (formato ABC-123) y en qué bodega está.",
        "name": "consultar_stock_roto",
        "parameters_json_schema": {
          "type": "object",
          "properties": {
            "sku": {
              "type": "string",
              "description": "Código SKU, por ejemplo TAL-200"
            }
          },
          "required": [
            "sku"
          ]
        }
      },
      {
        "description": "Calcula la fecha estimada de entrega de un pedido por su id (formato P-1234). Si ya fue despachado, suma eta_dias a fecha_despacho y devuelve la fecha en formato YYYY-MM-DD. Si aún no fue despachado, o el id no existe, devuelve un mensaje o un error.",
        "name": "fecha_estimada_entrega",
        "parameters_json_schema": {
          "type": "object",
          "properties": {
            "id_pedido": {
              "type": "string",
              "description": "Id del pedido, por ejemplo P-1001"
            }
          },
          "required": [
            "id_pedido"
          ]
        }
      }
    ]
  }
]

--- Interacción 1/5 ---
Llamando al modelo con el historial acumulado.
El modelo pidió 1 función(es).
Traceback (most recent call last):
  File "/Users/Ext_DHOrtizA/Desktop/DavidOrtiz/UC/repo/ia_agentica_uc/CLASE_3/ejercicios/3_ejercicio_loop_agentico_manual_force_error.py", line 164, in <module>
    agente_manual("Cuantas unidades del producto TAL-200 debo importar para cumplir un pedido de 100 unidades?")
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/Ext_DHOrtizA/Desktop/DavidOrtiz/UC/repo/ia_agentica_uc/CLASE_3/ejercicios/3_ejercicio_loop_agentico_manual_force_error.py", line 142, in agente_manual
    resultado = funciones[nombre](**args)
  File "/Users/Ext_DHOrtizA/Desktop/DavidOrtiz/UC/repo/ia_agentica_uc/CLASE_3/ejercicios/3_ejercicio_funcion_rota.py", line 4, in consultar_stock_roto
    raise RuntimeError("Inventario no disponible")
RuntimeError: Inventario no disponible
```

## Traza: loop con handler

Salida de `3_ejercicio_loop_agentico_manual_robusto_handler.py` con la misma pregunta. Si `generar` en `common.py` reintenta por demanda, la consola agrega `(el modelo está con mucha demanda, esperando 20 s...)` antes de la respuesta. Esta corrida no la imprimió.

```text
Pregunta: Cuantas unidades del producto TAL-200 debo importar para cumplir un pedido de 100 unidades?
Interacciones máximas: 5
Tools:
[
  {
    "function_declarations": [
      {
        "description": "Consulta las unidades disponibles de un producto por su SKU (formato ABC-123) y en qué bodega está.",
        "name": "consultar_stock_roto",
        "parameters_json_schema": {
          "type": "object",
          "properties": {
            "sku": {
              "type": "string",
              "description": "Código SKU, por ejemplo TAL-200"
            }
          },
          "required": [
            "sku"
          ]
        }
      },
      {
        "description": "Calcula la fecha estimada de entrega de un pedido por su id (formato P-1234). Si ya fue despachado, suma eta_dias a fecha_despacho y devuelve la fecha en formato YYYY-MM-DD. Si aún no fue despachado, o el id no existe, devuelve un mensaje o un error.",
        "name": "fecha_estimada_entrega",
        "parameters_json_schema": {
          "type": "object",
          "properties": {
            "id_pedido": {
              "type": "string",
              "description": "Id del pedido, por ejemplo P-1001"
            }
          },
          "required": [
            "id_pedido"
          ]
        }
      }
    ]
  }
]

--- Interacción 1/5 ---
Llamando al modelo con el historial acumulado.
El modelo pidió 1 función(es).
  RuntimeError capturado. Se devuelve el error como resultado de la tool.
  Función: consultar_stock_roto({'sku': 'TAL-200'})
  Resultado: {'error': 'Inventario no disponible'}
Resultados enviados al modelo. Pausa de 2.0 s antes de la siguiente interacción.

--- Interacción 2/5 ---
Llamando al modelo con el historial acumulado.
partes: no se arman, porque no hubo llamadas.
El modelo respondió con texto y no pidió funciones.
Respuesta: No se pudo consultar el stock porque el sistema reporta que el inventario no está disponible. Te sugiero verificar el código SKU o intentar más tarde.
2 llamadas al modelo | tokens entrada: 779 | salida: 55 | costo ≈ US$0.00037
```

La respuesta final dice que el inventario no está disponible y propone verificar el código SKU o intentar más tarde. No aparece una cantidad de unidades. Esa sugerencia es del modelo: la tool solo devolvió el texto `Inventario no disponible`.
