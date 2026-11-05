# Ejecución

Para ejecutar el ejercicio 3 del loop manual con una tool que lanza una excepción:

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
python "CLASE_3/ejercicios/3_ejercicio_loop_agentico_manual_force_error.py"
```

`agente_manual` arma el loop en Python: el modelo decide, el script ejecuta la función y le devuelve el resultado, hasta que haya texto final o se cumpla `max_iter`. En este archivo el valor por defecto es `5`. `automatic_function_calling` va desactivado. Entre una interacción con tools y la siguiente hay una pausa de 2 segundos. `temperature` es 0.

El contrato junta dos funciones: `consultar_stock_roto` y `fecha_estimada_entrega`. La declaración que ve el modelo describe un stock disponible por SKU. El modelo nunca ve el cuerpo de `consultar_stock_roto`.

En `__main__` la consulta pide cuántas unidades de TAL-200 hay que importar para completar un pedido de 100. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Propagación de la excepción y quiebre del loop

En la primera vuelta el modelo pide `consultar_stock_roto` con `sku='TAL-200'`. Python resuelve el nombre en `FUNCIONES` y llama la función real. En `3_ejercicio_funcion_rota.py` la línea que corre es `raise RuntimeError("Inventario no disponible")`. `raise` sale de esa función y sube por cada caller que no la capture.

La cadena de esta corrida es:

1. `consultar_stock_roto` lanza `RuntimeError` en la línea 4 de `3_ejercicio_funcion_rota.py`.
2. El llamado `resultado = funciones[nombre](**args)` está en la línea 142 de `agente_manual`. Ahí no hay `try`/`except`, así que la excepción abandona el `for` del loop.
3. `__main__` llama `agente_manual` en la línea 164, también sin `try`/`except`. La excepción llega al intérprete.
4. Python imprime el traceback y el proceso termina con código de salida 1.

El loop se corta en ese llamado. No se ejecutan las trazas `Función:` ni `Resultado:`, que están debajo de la llamada. No se arma `types.Part.from_function_response`, no se agrega el turno con el resultado y no hay pausa de 2 segundos. No hay interacción 2/5. El modelo no recibe el fallo, así que no llega a explicar el inventario caído.

`USO.append` ya corrió, porque está antes de ejecutar la tool: esa llamada al modelo quedó en memoria. El conteo de tokens y el costo están después de `agente_manual` en `__main__`, y esa parte no se alcanza. Por eso la consola no muestra la línea de costo.

La regla del system prompt que pide explicar un error aplica cuando la tool devuelve un valor, por ejemplo `{"error": "..."}`. Aquí la tool no devuelve nada: la excepción reemplaza al valor de retorno y el historial se queda con el pedido de la función, sin la respuesta de la tool.

En `3_ejercicio_funcion_rota.py` hay una línea comentada, `return RuntimeError("Inventario no disponible")`. Un `return` entregaría el objeto excepción como resultado y el loop seguiría. El `raise` activo es lo que propaga el error y termina el proceso.

## Ejemplo de ejecución

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
