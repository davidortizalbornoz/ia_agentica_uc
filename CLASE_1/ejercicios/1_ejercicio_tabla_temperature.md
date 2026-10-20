# Ejecución

Para ejecutar el ejercicio 1:

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

5. Activa el entorno e instala `google-genai` y `pandas` si aún no están. El ejercicio usa `generar` y el modelo elegido (`MODEL`) de `CLASE_1/parte_guiada/common.py`. La key y `PREFERIDOS` se leen con `leer_clave` desde `CLASE_1/parte_guiada/entorno_local.py`.

```bash
pyenv activate ia_agentica_uc
pip install google-genai pandas
```

6. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_1/ejercicios/1_ejercicio_tabla_temperature.py"
```

El script hace la misma consulta con `temperature` 0.0, 0.7 y 1.0, e imprime una tabla con las columnas `temperature`, `tokens_salida` y `respuesta`. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

```text
Modelo: gemini-3.5-flash-lite
Prompt: Solo me darás un breve consejo para incorporar hábitos de lectura a mi rutina diaria

+-------------+----------------+----------------------------------------------------------------------+
| temperature | tokens_salida  | respuesta                                                            |
+-------------+----------------+----------------------------------------------------------------------+
| 0.0         | 35             | Lee **solo 5 páginas** antes de dormir o al despertar; es una meta   |
|             |                | tan pequeña que tu cerebro no pondrá resistencia y el hábito se      |
|             |                | formará sin esfuerzo.                                                |
+-------------+----------------+----------------------------------------------------------------------+
| 0.7         | 57             | **Empieza con solo 5 minutos antes de dormir.**   No intentes leer   |
|             |                | una hora de golpe; reduce la fricción asociando el libro a un hábito |
|             |                | que ya haces todos los días. El impulso hará que, sin darte cuenta,  |
|             |                | quieras leer más cada noche.                                         |
+-------------+----------------+----------------------------------------------------------------------+
| 1.0         | 58             | Empieza ridículamente pequeño: lee **solo una página** (o un         |
|             |                | párrafo) antes de dormir o con el primer café de la mañana. Lo       |
|             |                | importante no es cuánto lees, sino no fallar ningún día. El hábito   |
|             |                | se crea por la constancia, no por el volumen.                        |
+-------------+----------------+----------------------------------------------------------------------+
```
