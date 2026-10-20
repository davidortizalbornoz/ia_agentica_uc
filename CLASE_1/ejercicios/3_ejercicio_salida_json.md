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

3. Abre `.env` y completa `GEMINI_API_KEY`. `PREFERIDOS` es la lista de modelos, separados por coma y en orden de preferencia. `.env.sample` ya trae esa lista; el script usa el primero que esté disponible en el proyecto.

4. Usa Python 3.13.5. El archivo `.python-version` de la raíz apunta al entorno de pyenv `ia_agentica_uc`, creado sobre esa versión. Clonar el repositorio no instala el intérprete ni el entorno: hay que tenerlos en la máquina.

```bash
pyenv install 3.13.5
pyenv virtualenv 3.13.5 ia_agentica_uc
```

`google-genai` pide Python 3.10 o superior, así que 3.13.5 es compatible. Si la consola ya tiene `PYENV_VERSION` definida (por ejemplo en 3.9.18), esa variable pisa a `.python-version`. Quítala antes de activar el entorno:

```bash
unset PYENV_VERSION
```

5. Activa el entorno e instala `google-genai` si aún no está. La consulta sale de `CLASE_1/parte_guiada/common.py` (`generar` y el modelo elegido, `MODEL`). La key y `PREFERIDOS` se leen con `leer_clave` desde `CLASE_1/parte_guiada/entorno_local.py`.

```bash
pyenv activate ia_agentica_uc
pip install google-genai
```

6. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_1/ejercicios/3_ejercicio_salida_json.py"
```

El script recorre tres frases y le pide al modelo un objeto JSON con `producto`, `cantidad` y `ciudad`, forzando el formato con `response_mime_type="application/json"`. Convierte cada respuesta con `json.loads` y comprueba que sea un diccionario. Si la frase no trae un dato, ese campo queda en `null`. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

```text

EJERCICIO 3. SALIDA EN JSON
______________________________________________

Modelo: gemini-3.5-flash-lite

Frase: Necesito 40 cajas de cartón para Valparaíso
{
  "producto": "cajas de cartón",
  "cantidad": 40,
  "ciudad": "Valparaíso"
}

Frase: Mándame guantes a Antofagasta
{
  "producto": "guantes",
  "cantidad": null,
  "ciudad": "Antofagasta"
}

Frase: Incorporar un par de promotores de preservativos en la ciudad de Santiago
{
  "producto": "promotores de preservativos",
  "cantidad": 2,
  "ciudad": "Santiago"
}
```
