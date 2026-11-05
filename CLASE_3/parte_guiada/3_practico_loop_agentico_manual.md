# Ejecución

Para ejecutar la parte guiada 3:

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

5. Activa el entorno e instala `google-genai` si aún no está. La llamada y el costo salen de `CLASE_1/parte_guiada/common.py` (`generar`, `costo_usd`). La key y `PREFERIDOS` se leen con `leer_clave` desde `CLASE_1/parte_guiada/entorno_local.py`. Las tools y las funciones salen de `2_b_practico_contratos.py`, que a su vez carga `2_a_practico_funciones_.py`. Los JSON los escribe `1_practico_datos_andina_cargo.py`.

```bash
pyenv activate ia_agentica_uc
pip install google-genai
```

6. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_3/parte_guiada/3_practico_loop_agentico_manual.py"
```

`agente_manual` arma el loop en Python: el modelo decide, el script ejecuta la función y le devuelve el resultado, hasta que haya texto final o se cumplan 5 interacciones. `automatic_function_calling` va desactivado. Entre una interacción con tools y la siguiente hay una pausa de 2 segundos. `temperature` es 0.

El contrato de este loop es el de la parte 2b: `buscar_pedido` y `consultar_stock`. `estimar_despacho` no está entre las tools.

En el archivo, `__main__` llama a `agente_manual` con la consulta del pedido P-1004. La consulta de días hábiles a Temuco está en la línea siguiente, comentada. Al terminar imprime cuántas llamadas hubo y suma los tokens y el costo de todas, porque cada vuelta reenvía el historial.

El ejemplo de abajo dejó activas las dos llamadas, una después de la otra:

```python
agente_manual("¿En qué estado está el pedido P-1004 y hay stock para reponer lo que lleva?")
agente_manual("¿Cuántos días hábiles tarda un despacho a Temuco?")
```

La primera consulta usa las dos tools: busca P-1004 y después consulta el SKU CAJ-050. La segunda pregunta por días a Temuco, y el modelo solo puede llamar a las tools declaradas. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

```text
Pregunta: ¿En qué estado está el pedido P-1004 y hay stock para reponer lo que lleva?
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
      }
    ]
  }
]

--- Interacción 1/5 ---
Llamando al modelo con el historial acumulado.
El modelo pidió 1 función(es).
  Función: buscar_pedido({'id_pedido': 'P-1004'})
  Resultado: {'id': 'P-1004', 'cliente': 'Ferretería Lagos', 'ciudad': 'Valparaíso', 'estado': 'retrasado', 'items': [{'sku': 'CAJ-050', 'cant': 40}], 'fecha_despacho': '2026-10-12', 'eta_dias': 3}
Resultados enviados al modelo. Pausa de 2.0 s antes de la siguiente interacción.

--- Interacción 2/5 ---
Llamando al modelo con el historial acumulado.
El modelo pidió 1 función(es).
  Función: consultar_stock({'sku': 'CAJ-050'})
  Resultado: {'sku': 'CAJ-050', 'nombre': 'Caja cartón 50x50', 'stock': 0, 'bodega': 'Santiago'}
Resultados enviados al modelo. Pausa de 2.0 s antes de la siguiente interacción.

--- Interacción 3/5 ---
Llamando al modelo con el historial acumulado.
partes: no se arman, porque no hubo llamadas.
El modelo respondió con texto y no pidió funciones.
Respuesta: El pedido P-1004 está **retrasado** con destino a Valparaíso y una ETA de 3 días.
Respecto al ítem (SKU CAJ-050), **no hay stock** disponible en la bodega de Santiago para reponerlo.




__________________________________________


Pregunta: ¿Cuántos días hábiles tarda un despacho a Temuco?
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
      }
    ]
  }
]

--- Interacción 1/5 ---
Llamando al modelo con el historial acumulado.
El modelo pidió 1 función(es).
  Función: buscar_pedido({'id_pedido': 'P-1001'})
  Resultado: {'id': 'P-1001', 'cliente': 'Ferretería Lagos', 'ciudad': 'Valparaíso', 'estado': 'en_transito', 'items': [{'sku': 'TAL-200', 'cant': 10}], 'fecha_despacho': '2026-10-15', 'eta_dias': 2}
Resultados enviados al modelo. Pausa de 2.0 s antes de la siguiente interacción.

--- Interacción 2/5 ---
Llamando al modelo con el historial acumulado.
partes: no se arman, porque no hubo llamadas.
El modelo respondió con texto y no pidió funciones.
Respuesta: El tiempo de despacho depende del tipo de servicio y origen, pero los envíos estándar tardan generalmente entre 2 y 4 días hábiles. Si tienes un pedido específico para Temuco, por favor indícame su número para verificar la estimación exacta.
5 llamadas al modelo | tokens entrada: 1988 | salida: 181 | costo ≈ US$0.00105
```
