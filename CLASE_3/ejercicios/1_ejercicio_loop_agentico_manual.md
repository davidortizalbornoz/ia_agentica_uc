# Ejecución

Para ejecutar el ejercicio 1 del loop manual:

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

5. Activa el entorno e instala `google-genai` si aún no está. La llamada y el costo salen de `CLASE_1/parte_guiada/common.py` (`generar`, `costo_usd`). La key y `PREFERIDOS` se leen con `leer_clave` desde `CLASE_1/parte_guiada/entorno_local.py`. `buscar_pedido` y `consultar_stock` salen de `CLASE_3/parte_guiada/2_b_practico_contratos.py`. `fecha_estimada_entrega` sale de `1_ejercicio_contrato.py`, que carga `1_ejercicio_funciones.py`. Los JSON los escribe `CLASE_3/parte_guiada/1_practico_datos_andina_cargo.py`.

```bash
pyenv activate ia_agentica_uc
pip install google-genai
```

6. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_3/ejercicios/1_ejercicio_loop_agentico_manual.py"
```

`agente_manual` arma el loop en Python: el modelo decide, el script ejecuta la función y le devuelve el resultado, hasta que haya texto final o se cumpla `max_iter`. En este archivo el valor por defecto es `5`. `automatic_function_calling` va desactivado. Entre una interacción con tools y la siguiente hay una pausa de 2 segundos. `temperature` es 0.

El contrato junta las tres funciones: `buscar_pedido`, `consultar_stock` y `fecha_estimada_entrega`.

En `__main__` la consulta es el día de la semana de la fecha de entrega del pedido P-1001. Al terminar imprime cuántas llamadas hubo y suma los tokens y el costo, porque cada vuelta reenvía el historial. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

En la primera vuelta el modelo pide `fecha_estimada_entrega` para P-1001. Python ejecuta la función y deja en el historial la fecha `2026-10-17`. En la segunda vuelta `function_calls` viene vacío y la función hace `return respuesta.text`. El día de la semana no sale de una herramienta: la función solo devolvió la fecha, y el texto lo escribe el modelo. En esta corrida dijo viernes. El 17 de octubre de 2026 es sábado.

## Ejemplo de ejecución

```text
Pregunta: Dame el día de la semana, de la fecha de entrega del pedido P-1001
Interacciones máximas: 5
Tools:
[
  {
    "function_declarations": [
      {
        "description": "Busca un pedido por su id (formato P-1234) y devuelve estado, cliente, ciudad, items, fecha de despacho y ETA en días.",
        "name": "buscar_pedido",
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
      },
      {
        "description": "Consulta las unidades disponibles de un producto por su SKU (formato ABC-123) y en qué bodega está.",
        "name": "consultar_stock",
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
  (el modelo está con mucha demanda, esperando 20 s...)
El modelo pidió 1 función(es).
  Función: fecha_estimada_entrega({'id_pedido': 'P-1001'})
  Resultado: {'id': 'P-1001', 'fecha_despacho': '2026-10-15', 'eta_dias': 2, 'fecha_estimada_entrega': '2026-10-17'}
Resultados enviados al modelo. Pausa de 2.0 s antes de la siguiente interacción.

--- Interacción 2/5 ---
Llamando al modelo con el historial acumulado.
partes: no se arman, porque no hubo llamadas.
El modelo respondió con texto y no pidió funciones.
Respuesta: La fecha estimada de entrega para el pedido P-1001 es el viernes 17 de octubre de 2026.
2 llamadas al modelo | tokens entrada: 1005 | salida: 56 | costo ≈ US$0.00044
```
