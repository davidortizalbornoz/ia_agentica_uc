# Ejecución

Para ejecutar el ejercicio 2:

1. Clona el repositorio.

```bash
git clone https://github.com/davidortizalbornoz/ia_agentica_uc.git
cd ia_agentica_uc
```

2. Crea un archivo `.env` en la raíz del proyecto. Puedes partir de `.env.sample`:

```bash
cp .env.sample .env
```

3. Abre `.env` y completa `GEMINI_API_KEY`. `PREFERIDOS` es la lista de modelos, separados por coma y en orden de preferencia. `.env.sample` ya trae esa lista; la primera columna de la comparación usa el primero que esté disponible en el proyecto.

4. Usa Python 3.13.5. El archivo `.python-version` de la raíz apunta al entorno de pyenv `ia_agentica_uc`, creado sobre esa versión. Clonar el repositorio no instala el intérprete ni el entorno: hay que tenerlos en la máquina.

```bash
pyenv install 3.13.5
pyenv virtualenv 3.13.5 ia_agentica_uc
```

`google-genai` pide Python 3.10 o superior, así que 3.13.5 es compatible. Si la consola ya tiene `PYENV_VERSION` definida (por ejemplo en 3.9.18), esa variable pisa a `.python-version`. Quítala antes de activar el entorno:

```bash
unset PYENV_VERSION
```

5. Activa el entorno e instala `google-genai` si aún no está. La consulta y el costo salen de `CLASE_1/parte_guiada/common.py` (`elegir_modelo`, `generar` y `costo_usd`). La key y `PREFERIDOS` se leen con `leer_clave` desde `CLASE_1/parte_guiada/entorno_local.py`.

```bash
pyenv activate ia_agentica_uc
pip install google-genai
```

6. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_1/ejercicios/2_ejercicio_costo_1000_consultas.py"
```

El script hace en paralelo la misma consulta («¿Qué es un token?») con dos modelos: el elegido desde `PREFERIDOS` y `gemini-3.8-flash`. El tope de salida es 1024 tokens porque en `gemini-3.8-flash` ese límite incluye el razonamiento; con un tope bajo la frase visible queda cortada. Imprime cada respuesta y después una tabla. La primera columna de datos es el modelo elegido y la segunda es `gemini-3.8-flash`. Las filas son tokens de entrada, de salida, de razonamiento y total, más el costo de una consulta, el diario (1.000 consultas) y el mensual (30 días). El costo de cada columna usa el precio de ese modelo y suma los tokens de razonamiento a los de salida. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

```text

EJERCICIO 2. COSTO DE 1.000 CONSULTAS
______________________________________________

Modelo: gemini-3.5-flash-lite
Respuesta:
Un token es la unidad básica de texto —como una palabra o parte de ella— que un modelo de lenguaje procesa y comprende. En la IA agéntica, representan tanto el costo computacional como la "memoria" que los agentes pueden leer y generar.
tiempo de respuesta: 6644 ms

Modelo: gemini-3.8-flash
Respuesta:
Un token es la unidad básica de información (como una palabra, una parte de ella o un signo de puntuación) que un modelo de lenguaje procesa para entender y generar texto. En la IA agéntica, los tokens son fundamentales porque determinan el costo operativo, la capacidad de memoria del agente y el límite de su ventana de contexto. En resumen, es la forma en que el modelo fragmenta y cuantifica el lenguaje humano para poder razonar y actuar.
tiempo de respuesta: 77506 ms

TABLA COMPARATIVA DE MODELOS
+------------------------------+-----------------------+------------------+
| detalle                      | gemini-3.5-flash-lite | gemini-3.8-flash |
+------------------------------+-----------------------+------------------+
| tokens de entrada (prompt)   | 32                    | 32               |
| tokens de salida (respuesta) | 54                    | 95               |
| tokens de razonamiento       | 0                     | 466              |
| total                        | 86                    | 593              |
| costo una consulta           | US$0.000145           | US$0.002128      |
| costo diario                 | US$0.144600           | US$2.127750      |
| costo mensual (30 días)      | US$4.338000           | US$63.832500     |
+------------------------------+-----------------------+------------------+
```
