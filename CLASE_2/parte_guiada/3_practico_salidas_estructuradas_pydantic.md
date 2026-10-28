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

5. Activa el entorno e instala `google-genai`, `pandas` y `pydantic` si aún no están. La llamada y el modelo elegido (`MODEL`) salen de `CLASE_1/parte_guiada/common.py`. La key y `PREFERIDOS` se leen con `leer_clave` desde `CLASE_1/parte_guiada/entorno_local.py`. El prompt `v2_estructurado`, la pausa y los correos salen de `2_practico_3versionesde_systemprompt.py`.

```bash
pyenv activate ia_agentica_uc
pip install google-genai pandas pydantic
```

6. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_2/parte_guiada/3_practico_salidas_estructuradas_pydantic.py"
```

El script toma los tres primeros correos y hace una llamada por cada uno. Esas tres respuestas se imprimen como objeto validado. Después consulta el cuarto correo y lo imprime en JSON. Son 4 llamadas, con una pausa de 2 segundos entre ellas. La instrucción es el prompt `v2_estructurado` más el pedido de estimar la urgencia y resumir el correo en una frase.

La respuesta tiene que cumplir el esquema `Clasificacion`: `categoria` solo puede ser `facturacion`, `tecnico`, `reclamo` u `otro`; `urgencia` solo puede ser `baja`, `media` o `alta`; `resumen` es una frase. El formato se fuerza con `response_mime_type="application/json"` y `response_schema`. Pydantic valida el objeto antes de imprimirlo. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

```text
categoria='facturacion' urgencia='media' resumen='Solicitud de reemisión de la factura 7781 por error en el RUT.'
categoria='tecnico' urgencia='media' resumen='El cliente reporta que no recibe el correo de confirmación al crear un pedido en la plataforma.'
categoria='reclamo' urgencia='alta' resumen='El cliente reporta daños en mercancía del pedido P-1004 y retraso en la entrega.'

JSON DEL CUARTO CORREO
¿Tienen cobertura a Punta Arenas?
{
  "categoria": "otro",
  "urgencia": "baja",
  "resumen": "Consulta sobre cobertura de envíos hacia Punta Arenas."
}
```
