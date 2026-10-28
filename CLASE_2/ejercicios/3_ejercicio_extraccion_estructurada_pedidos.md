# Ejecución

Para ejecutar el ejercicio 3:

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

5. Activa el entorno e instala `google-genai` y `pydantic` si aún no están. La llamada y el modelo elegido (`MODEL`) salen de `CLASE_1/parte_guiada/common.py`. La key y `PREFERIDOS` se leen con `leer_clave` desde `CLASE_1/parte_guiada/entorno_local.py`.

```bash
pyenv activate ia_agentica_uc
pip install google-genai pydantic
```

6. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_2/ejercicios/3_ejercicio_extraccion_estructurada_pedidos.py"
```

El script recorre siete frases y le pide al modelo un objeto JSON con `sku`, `cantidad` y `ciudad`. El formato se fuerza con `response_mime_type="application/json"` y el esquema `Pedido`. Pydantic valida cada respuesta antes de imprimirla. Si la frase no permite determinar un campo, la instrucción pide `null`. `cantidad` es un entero o `null`. `sku` y `ciudad` son texto o `null`. Son 7 llamadas al modelo. Al final imprime una conclusión: el ejercicio 3 de la clase 1 pide texto JSON y lo convierte en un diccionario; este, además, le entrega al modelo el esquema `Pedido` y comprueba que la respuesta lo cumpla. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

```text

EJERCICIO 3. EXTRACCIÓN ESTRUCTURADA DE PEDIDOS
______________________________________________

Modelo: gemini-3.5-flash-lite

Frase: Despacha 40 unidades del SKU CAJ-40 a Valparaíso
{
  "sku": "CAJ-40",
  "cantidad": 40,
  "ciudad": "Valparaíso"
}

Frase: Necesito 15 del SKU GUA-02
{
  "sku": "GUA-02",
  "cantidad": 15,
  "ciudad": null
}

Frase: Envía el SKU PAL-200 a Antofagasta
{
  "sku": "PAL-200",
  "cantidad": null,
  "ciudad": "Antofagasta"
}

Frase: Mándame 8 cajas a Santiago
{
  "sku": null,
  "cantidad": 8,
  "ciudad": "Santiago"
}

Frase: El código de producto es TNT-15
{
  "sku": "TNT-15",
  "cantidad": null,
  "ciudad": null
}

Frase: Quince brochas para la capital de Chile
{
  "sku": "brochas",
  "cantidad": 15,
  "ciudad": "Santiago"
}

Frase: Hola, quisiera hacer un pedido
{
  "sku": null,
  "cantidad": null,
  "ciudad": null
}

________________ CONCLUSION ______________________

Los dos recursos devuelven JSON. El de la clase 1 pide texto JSON y lo convierte en un diccionario. El de la clase 2, además, le entrega al modelo el esquema Pedido y comprueba que la respuesta cumpla ese esquema.

```
