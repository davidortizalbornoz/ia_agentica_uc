# Ejecución

Para ejecutar la parte guiada 4:

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

5. Activa el entorno e instala `google-genai` si aún no está. El cliente y el modelo elegido (`MODEL`) salen de `CLASE_1/parte_guiada/common.py`. La key y `PREFERIDOS` se leen con `leer_clave` desde `CLASE_1/parte_guiada/entorno_local.py`. Las tres funciones salen de `2_a_practico_funciones_.py`. Los JSON los escribe `1_practico_datos_andina_cargo.py`.

```bash
pyenv activate ia_agentica_uc
pip install google-genai
```

6. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_3/parte_guiada/4_practico_loop_agentico_automatico.py"
```

`agente_automatico` le pasa al SDK las funciones `buscar_pedido`, `consultar_stock` y `estimar_despacho`. El SDK arma el contrato desde el type hint y el docstring, ejecuta el loop y devuelve el texto final. La pregunta es «¿Cuándo le llega a Clínica Norte su pedido P-1003?». `temperature` es 0.

Al terminar imprime la respuesta, el historial del chat (pregunta, pedido de tool, resultado y texto) y los tokens de `send_message`. Las vueltas intermedias quedan dentro de esa misma llamada. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

```text
Pregunta: ¿Cuándo le llega a Clínica Norte su pedido P-1003?
Tools: ['buscar_pedido', 'consultar_stock', 'estimar_despacho']

Respuesta: El pedido P-1003 para Clínica Norte (Antofagasta) está en estado "preparación" y tiene un ETA estimado de 4 días hábiles.

Historial automático:
[user] ¿Cuándo le llega a Clínica Norte su pedido P-1003?
[model] pide buscar_pedido({'id_pedido': 'P-1003'})
[user] resultado -> {'result': {'id': 'P-1003', 'cliente': 'Clínica Norte', 'ciudad': 'Antofagasta', 'estado': 'preparacion', 'items': [{'sku': 'GUA-010', 'cant': 50}, {'sku': 'TAL-200', 'cant': 5}], 'fecha_despacho': None, 'eta_dias': 4}}
[model] El pedido P-1003 para Clínica Norte (Antofagasta) está en estado "preparación" y tiene un ETA estimado de 4 días hábiles.
1 respuesta(s) de send_message | tokens entrada: 459 | salida: 37 | costo ≈ US$0.00023
```
