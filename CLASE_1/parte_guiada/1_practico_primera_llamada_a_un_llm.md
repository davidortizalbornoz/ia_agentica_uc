# Ejecución

Para ejecutar la parte guiada:

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

5. Activa el entorno e instala `google-genai` si aún no está. La key se lee con `leer_clave` desde `CLASE_1/parte_guiada/entorno_local.py`. La elección del modelo, la llamada, el costo y el conteo de tokens están en `CLASE_1/parte_guiada/common.py` (`elegir_modelo`, `generar`, `costo_usd`, `contar_tokens`).

```bash
pyenv activate ia_agentica_uc
pip install google-genai
```

6. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_1/parte_guiada/1_practico_primera_llamada_a_un_llm.py"
```

El script importa esas funciones desde `common.py`. Muestra el modelo elegido, una respuesta a «¿Qué es un token?», los tokens y el costo de esa llamada, el conteo de tokens de varios textos y tres respuestas con `temperature` 0.0 y 1.0. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

```text

SECCION 1. ELECCION DEL MODELO
______________________________________________

Listo. Modelo: gemini-3.5-flash-lite


SECCION 2. PETICION A LLM
______________________________________________

Un token es la unidad básica de texto —como una palabra o parte de ella— que un modelo de lenguaje procesa y comprende. En la IA agéntica, representan tanto el costo computacional como la "memoria" disponible para que el agente razone y actúe. Cuantos más tokens maneje un agente, mayor será su capacidad de contexto y planificación.
tiempo de respuesta: 16179 ms


SECCION 3. RESUMEN DE COSTOS
______________________________________________

tokens de entrada (prompt)   : 32
tokens de salida (respuesta) : 76
tokens de razonamiento       : 0   <- algunos modelos 'piensan' antes de responder y eso también son tokens
total                        : 108
costaría (nivel de pago)     : US$0.000200


SECCION 4. CONTABILIZAR TOKENS EN BASE A TEXTO
______________________________________________

'Hola'                                   -> 2 tokens
'Los agentes usan herramientas.'         -> 6 tokens
'Agents use tools.'                      -> 5 tokens
'Supercalifragilístico'                  -> 7 tokens


SECCION 5. TEMPERATURA (ALEATORIEDAD)
______________________________________________

--- temperature=0.0 ---
 · Tu café de siempre, a un paso.
 · Tu café de siempre, a un paso.
 · Tu café de siempre, a un paso de casa.
--- temperature=1.0 ---
 · Tu café de siempre, a un paso.
 · Tu café de siempre, a un paso de casa.
 · Tu café de siempre, a un paso.

 FIN SCRIPT
```
