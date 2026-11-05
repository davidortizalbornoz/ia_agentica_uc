# Ejecución

Para ejecutar el ejercicio 2 con el loop limitado a 1 interacción:

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
python "CLASE_3/ejercicios/2_ejercicio_loop_agentico_manual_limite_1.py"
```

`agente_manual` arma el loop en Python: el modelo decide, el script ejecuta la función y le devuelve el resultado, hasta que haya texto final o se cumpla `max_iter`. En este archivo el valor por defecto es `1`. `automatic_function_calling` va desactivado. Entre una interacción con tools y la siguiente hay una pausa de 2 segundos. `temperature` es 0.

El contrato junta las tres funciones: `buscar_pedido`, `consultar_stock` y `fecha_estimada_entrega`.

En `__main__` la consulta es el día de la semana de la fecha de entrega del pedido P-1001. Al terminar imprime cuántas llamadas hubo y suma los tokens y el costo, porque cada vuelta reenvía el historial. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

Con `max_iter=1`, `range(1, max_iter + 1)` produce una sola vuelta. En esa vuelta el modelo pide `fecha_estimada_entrega` para P-1001 y Python ejecuta la función: la fecha estimada (`2026-10-17`) queda en el historial. El texto final del modelo sale en una vuelta posterior, cuando `function_calls` viene vacío y la función hace `return respuesta.text`. Esa segunda llamada no ocurre. El `for` termina, la traza escribe `Límite de 1 interacciones alcanzado, sin respuesta final.` y la función devuelve `Se alcanzó el límite de iteraciones sin respuesta final.` Ese cierre es un `return`. El flujo del límite no lanza excepciones: no hay `raise` ni un traceback que leer. Los `raise SystemExit` del archivo cubren la carga de los contratos y una respuesta del modelo sin candidatos, sin turno o sin nombre de tool. `__main__` no imprime el valor devuelto; en consola se ve la línea de la traza y, después, el conteo de tokens.

## Ejemplo de ejecución

```text
Pregunta: Dame el día de la semana, de la fecha de entrega del pedido P-1001
Interacciones máximas: 1
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

--- Interacción 1/1 ---
Llamando al modelo con el historial acumulado.
El modelo pidió 1 función(es).
  Función: fecha_estimada_entrega({'id_pedido': 'P-1001'})
  Resultado: {'id': 'P-1001', 'fecha_despacho': '2026-10-15', 'eta_dias': 2, 'fecha_estimada_entrega': '2026-10-17'}
Resultados enviados al modelo. Pausa de 2.0 s antes de la siguiente interacción.

Límite de 1 interacciones alcanzado, sin respuesta final.
1 llamadas al modelo | tokens entrada: 453 | salida: 3 | costo ≈ US$0.00014
```
