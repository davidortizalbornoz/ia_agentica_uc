# Ejecución

Para ejecutar el ejercicio 3 del loop automático con la función que lanza una excepción:

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

5. Activa el entorno e instala `google-genai` si aún no está. El cliente, el modelo elegido (`MODEL`) y el costo salen de `CLASE_1/parte_guiada/common.py` (`client`, `MODEL`, `costo_usd`). La key y `PREFERIDOS` se leen con `leer_clave` desde `CLASE_1/parte_guiada/entorno_local.py`. `consultar_stock_roto` sale de `3_ejercicio_funcion_rota.py`, en esta misma carpeta.

```bash
pyenv activate ia_agentica_uc
pip install google-genai
```

6. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_3/ejercicios/3_ejercicio_loop_agentico_auto_handler.py"
```

`agente_automatico` le pasa al SDK la función `consultar_stock_roto` como función Python. El SDK arma el contrato desde el type hint y el docstring, y hace el loop. La conversación vive en `client.chats.create`. `send_message` (línea 78) resuelve las vueltas intermedias dentro de esa misma llamada. Este archivo no fija `AutomaticFunctionCallingConfig`, así que queda el tope por defecto del SDK: 10 llamadas remotas. `temperature` es 0.

En `__main__` (línea 93) la consulta es la misma que en los loops manuales del ejercicio 3: cuántas unidades de TAL-200 hay que importar para completar un pedido de 100. Al terminar imprime la respuesta, el historial del chat y los tokens que devolvió `send_message`. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Captura de la excepción dentro del SDK

En la primera vuelta el modelo pide `consultar_stock_roto` con `sku='TAL-200'`. El SDK llama la función Python. En `3_ejercicio_funcion_rota.py` la línea que corre sigue siendo `raise RuntimeError("Inventario no disponible")`. Este script no tiene `try`/`except`: el `raise` sale de `consultar_stock_roto` igual que en el loop manual.

La cadena de esta corrida es:

1. `consultar_stock_roto` lanza `RuntimeError` en la línea 4 de `3_ejercicio_funcion_rota.py`.
2. `send_message` (línea 78 de este archivo) no envuelve esa llamada. El loop automático de `google.genai` ejecuta la función en `invoke_function_from_dict_args`.
3. Ese helper atrapa `Exception` y la vuelve a lanzar como `FunctionInvocationError`. El mensaje conserva el texto original: `because of error Inventario no disponible`.
4. `get_function_response_parts` atrapa esa segunda excepción y arma `{"error": "<mensaje>"}`. `Part.from_function_response` mete ese dict en el historial con `role` `user`.
5. El SDK llama otra vez al modelo dentro del mismo `send_message`. El modelo responde con texto.
6. `agente_automatico` imprime `Respuesta:` y el historial (`trazar_historial`, líneas 43-57). `__main__` imprime tokens y costo. El proceso termina con código de salida 0.

Lo que recibe el modelo en el historial es:

```json
{"error": "Failed to invoke function consultar_stock_roto with converted arguments {'sku': 'TAL-200'} from model returned function call argument {'sku': 'TAL-200'} because of error Inventario no disponible"}
```

La regla 3 del system prompt pide explicar un error cuando la herramienta devuelve un valor. Aquí la tool sí devuelve un valor: el SDK convirtió la excepción en ese dict. En la vuelta siguiente el modelo dice que el inventario de TAL-200 no está disponible y propone verificar el código del producto o intentar más tarde. No inventa unidades. El SKU sale en el texto final porque también iba en la llamada de la tool y en el mensaje de error.

`USO.append` corre una sola vez, cuando `send_message` ya devolvió la respuesta final (líneas 79-80). Las vueltas intermedias quedan dentro de esa llamada, así que la consola muestra `1 respuesta(s) de send_message`. En esta corrida: 300 tokens de entrada, 36 de salida, ≈ US$0.00018.

## Comparación del manejo de la excepción

Los tres scripts usan la misma `consultar_stock_roto` y la misma pregunta. En los manuales el contrato también incluye `fecha_estimada_entrega`. En este archivo la única tool es `consultar_stock_roto` (línea 64).

| | `3_ejercicio_loop_agentico_manual_force_error.py` | `3_ejercicio_loop_agentico_manual_robusto_handler.py` | `3_ejercicio_loop_agentico_auto_handler.py` |
| --- | --- | --- | --- |
| Quién llama a la función | El script, línea 142, sin `try`/`except` | El script, líneas 144-147, con `try`/`except Exception` | El SDK, dentro de `send_message` (línea 78). Este archivo no tiene `try`/`except` |
| Qué hace el `RuntimeError` | Sube hasta el intérprete | Se detiene en el `except`. `resultado` pasa a ser `{"error": "Inventario no disponible"}` | El SDK lo envuelve y lo devuelve como `{"error": "Failed to invoke function ... because of error Inventario no disponible"}` |
| Texto que ve el modelo | Ninguno: el historial se corta en el pedido de la tool | `Inventario no disponible` | El mensaje largo del SDK, que incluye `Inventario no disponible` |
| Vueltas | Se corta en la interacción 1/5 | Interacción 2/5 con texto final. Pausa de 2 segundos entre medias | Las dos vueltas ocurren dentro de un solo `send_message`. No hay pausa de 2 segundos |
| Costo en consola | No se imprime. Código de salida 1 | 2 llamadas, 779 de entrada, 55 de salida, ≈ US$0.00037. Código de salida 0 | 1 respuesta de `send_message`, 300 de entrada, 36 de salida, ≈ US$0.00018. Código de salida 0 |

En `3_ejercicio_funcion_rota.py` la línea comentada `return RuntimeError("Inventario no disponible")` entregaría el objeto excepción como resultado. El `raise` activo es el que dispara el handler del SDK. El modelo aplica la regla 3 sobre el dict `error` y cierra sin inventar stock.

## Ejemplo de ejecución

Salida de `3_ejercicio_loop_agentico_auto_handler.py`. El proceso termina con código de salida 0.

```text
Pregunta: Cuantas unidades del producto TAL-200 debo importar para cumplir un pedido de 100 unidades?
Tools: ['consultar_stock_roto']

Respuesta: El sistema indica que el inventario para el SKU TAL-200 no está disponible en este momento. Te sugiero verificar el código del producto o intentar nuevamente más tarde.

Historial automático:
[user] Cuantas unidades del producto TAL-200 debo importar para cumplir un pedido de 100 unidades?
[model] pide consultar_stock_roto({'sku': 'TAL-200'})
[user] resultado -> {'error': "Failed to invoke function consultar_stock_roto with converted arguments {'sku': 'TAL-200'} from model returned function call argument {'sku': 'TAL-200'} because of error Inventario no disponible"}
[model] El sistema indica que el inventario para el SKU TAL-200 no está disponible en este momento. Te sugiero verificar el código del producto o intentar nuevamente más tarde.
1 respuesta(s) de send_message | tokens entrada: 300 | salida: 36 | costo ≈ US$0.00018
```

La respuesta final dice que el inventario de TAL-200 no está disponible y propone verificar el código del producto o intentar más tarde. No aparece una cantidad de unidades. Esa sugerencia es del modelo: la tool solo lanzó `Inventario no disponible`, y el SDK lo entregó dentro del mensaje `Failed to invoke function ...`.
