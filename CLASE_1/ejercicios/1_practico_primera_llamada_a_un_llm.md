# Ejecución

Para ejecutar el recurso Python:

1. Clona el repositorio.

```bash
git clone https://github.com/davidortizalbornoz/ia_agentica_uc.git
cd ia_agentica_uc
```

2. Crea un archivo `.env` en la raíz del proyecto. Puedes partir de `.env.sample`:

```bash
cp .env.sample .env
```

3. Abre `.env` y coloca el valor correcto en la variable `GEMINI_API_KEY`.

4. Usa Python 3.13.5. El archivo `.python-version` de la raíz apunta al entorno de pyenv `ia_agentica_uc`, creado sobre esa versión. Clonar el repositorio no instala el intérprete ni el entorno: hay que tenerlos en la máquina.

```bash
pyenv install 3.13.5
pyenv virtualenv 3.13.5 ia_agentica_uc
```

`google-genai` pide Python 3.10 o superior, así que 3.13.5 es compatible. Si la consola ya tiene `PYENV_VERSION` definida (por ejemplo en 3.9.18), esa variable pisa a `.python-version`. Quítala antes de activar el entorno:

```bash
unset PYENV_VERSION
```

5. Desde la consola del IDE, en la raíz del proyecto:

```bash
pyenv activate ia_agentica_uc
python "CLASE_1/ejercicios/1_practico_primera_llamada_a_un_llm.py"
```

El script lee `GEMINI_API_KEY` desde el archivo `.env` de la raíz del proyecto. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.
