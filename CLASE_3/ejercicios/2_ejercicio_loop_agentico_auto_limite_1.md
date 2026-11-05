# Ejecución

Para ejecutar el ejercicio 2 con el loop automático limitado a 1 llamada remota:

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

5. Activa el entorno e instala `google-genai` si aún no está. El cliente, el modelo elegido (`MODEL`) y el costo salen de `CLASE_1/parte_guiada/common.py`. La key y `PREFERIDOS` se leen con `leer_clave` desde `CLASE_1/parte_guiada/entorno_local.py`. `buscar_pedido`, `consultar_stock` y `estimar_despacho` salen de `CLASE_3/parte_guiada/2_a_practico_funciones_.py`. Los JSON los escribe `CLASE_3/parte_guiada/1_practico_datos_andina_cargo.py`.

```bash
pyenv activate ia_agentica_uc
pip install google-genai
```

6. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_3/ejercicios/2_ejercicio_loop_agentico_auto_limite_1.py"
```

`agente_automatico` le pasa al SDK las tres funciones como funciones Python. El SDK arma el contrato desde el type hint y el docstring, y hace el loop. El tope va en `AutomaticFunctionCallingConfig.maximum_remote_calls`. En este archivo el valor por defecto, `max_llamadas`, es `1`. La conversación vive en `client.chats.create` y `send_message` corta el ciclo automático en ese tope. `temperature` es 0.

En `__main__` la consulta es «¿Cuándo le llega a Clínica Norte su pedido P-1003?». Al terminar imprime el historial del chat y los tokens de la respuesta que devolvió `send_message`. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

Con el límite en 1, esa única llamada remota la usa el modelo para pedir `buscar_pedido` con `id_pedido` `P-1003`. El SDK se detiene ahí. No queda una llamada para enviarle el resultado, así que la función Python no se ejecuta y el texto final no llega. `texto_respuesta` lee las partes del candidato y devuelve `None`. No usa `response.text`: con solo un `function_call`, ese atributo avisa y también devuelve `None`. La traza escribe `Respuesta: None`, `function_calls: buscar_pedido({'id_pedido': 'P-1003'})` y `Límite de 1 llamada(s) remota(s) alcanzado, sin respuesta final.` El historial termina en el pedido de la tool, sin resultado. Ese cierre no lanza excepciones. El único `raise SystemExit` del archivo cubre que falte `2_a_practico_funciones_.py`. `send_message` informa el usage de la respuesta que devolvió, que es el pedido de tool, no el texto final.

## Ejemplo de ejecución

```text
Pregunta: ¿Cuándo le llega a Clínica Norte su pedido P-1003?
Tools: ['buscar_pedido', 'consultar_stock', 'estimar_despacho']
Llamadas remotas máximas: 1

Respuesta: None
function_calls: buscar_pedido({'id_pedido': 'P-1003'})
Límite de 1 llamada(s) remota(s) alcanzado, sin respuesta final.

Historial automático:
[user] ¿Cuándo le llega a Clínica Norte su pedido P-1003?
[model] pide buscar_pedido({'id_pedido': 'P-1003'})
1 respuesta(s) de send_message | tokens entrada: 348 | salida: 23 | costo ≈ US$0.00016
```
