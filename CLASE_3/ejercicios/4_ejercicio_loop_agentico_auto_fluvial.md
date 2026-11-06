# Ejecución

Para ejecutar el ejercicio 4 del loop automático sobre la base fluvial:

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

5. Activa el entorno e instala `google-genai` si aún no está. El cliente, el modelo elegido (`MODEL`) y el costo salen de `CLASE_1/parte_guiada/common.py` (`client`, `MODEL`, `costo_usd`). La key y `PREFERIDOS` se leen con `leer_clave` desde `CLASE_1/parte_guiada/entorno_local.py`. Las siete búsquedas salen de `4_ejercicio_funciones.py`, en esta misma carpeta. Los JSON viven en `CLASE_3/ejercicios/data/`: `rios.json`, `ciudades.json` y `puntos_fluviales.json`.

```bash
pyenv activate ia_agentica_uc
pip install google-genai
```

6. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_3/ejercicios/4_ejercicio_loop_agentico_auto_fluvial.py"
```

`agente_automatico` le pasa al SDK las siete funciones como funciones Python (líneas 30-38). El SDK arma el contrato desde el type hint y el docstring, y hace el loop. La conversación vive en `client.chats.create`. `send_message` (línea 94) resuelve las vueltas intermedias dentro de esa misma llamada. Este archivo no fija `AutomaticFunctionCallingConfig`, así que queda el tope por defecto del SDK: 10 llamadas remotas. `temperature` es 0.

En `__main__` (líneas 109-113) hay cuatro consultas. Deja activa una por vez y comenta las otras tres. Cada bloque de más abajo es una corrida aparte, con su propia línea de tokens. `USO.append` corre una sola vez por llamada, cuando `send_message` ya devolvió el texto final. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

Las cuatro preguntas piden el mismo tipo de dato con un anidamiento de tools distinto. Una tool resuelve un archivo, o dos archivos si la función ya cruza el nombre de la ciudad con su id. Cuando la pregunta cruza región, lluvia y ríos, el modelo encadena varias tools: la salida de una vuelta es el argumento de la siguiente. Si en una vuelta pide varias tools a la vez, el historial muestra esos `pide` seguidos y después los `resultado`.


## Ríos en Temuco

Esta pregunta se cierra con una sola tool.

`rios.json` guarda `id_ciudad`, no el nombre. `buscar_rios_por_ciudad` hace ese cruce por dentro: busca el nombre en `ciudades.json` y devuelve los ríos de esos ids. El modelo pide `buscar_rios_por_ciudad` con `nombre_ciudad` `Temuco`. El resultado trae tres ríos de `TEM`: Rio Tolten (R1), Río Cautín (R5) y Río Cholchol (R6).

El texto final los nombra como Río Toltén, Río Cautín y Río Cholchol. Hay una respuesta de `send_message`: 2366 tokens de entrada, 26 de salida, ≈ US$0.00077.

```text
Pregunta: ¿Qué ríos hay en Temuco
Tools: ['buscar_rios_por_ciudad', 'buscar_rios_por_nombre', 'buscar_ciudad_por_id', 'buscar_ciudad_por_region', 'buscar_ciudad_por_nombre', 'buscar_punto_por_id', 'buscar_punto_por_ciudad']

Respuesta: En Temuco se encuentran los siguientes ríos:
- Río Toltén
- Río Cautín
- Río Cholchol

Historial automático:
[user] ¿Qué ríos hay en Temuco
[model] pide buscar_rios_por_ciudad({'nombre_ciudad': 'Temuco'})
[user] resultado -> {'result': [{'id_rio': 'R1', 'nombre_rio': 'Rio Tolten', 'id_ciudad': 'TEM'}, {'id_rio': 'R5', 'nombre_rio': 'Río Cautín', 'id_ciudad': 'TEM'}, {'id_rio': 'R6', 'nombre_rio': 'Río Cholchol', 'id_ciudad': 'TEM'}]}
[model] En Temuco se encuentran los siguientes ríos:
- Río Toltén
- Río Cautín
- Río Cholchol
1 respuesta(s) de send_message | tokens entrada: 2366 | salida: 26 | costo ≈ US$0.00077
```


## Ríos en la región de la Araucanía

Ninguna tool recibe una región y devuelve ríos. El modelo arma dos vueltas.

En la primera pide `buscar_ciudad_por_region` con `nombre_region` `Araucania`. El JSON guarda la región sin tilde, y la tool compara por coincidencia parcial. El resultado trae Temuco (`TEM`), Villarica (`VIL`) y Angol (`ANG`).

En la segunda vuelta pide tres `buscar_rios_por_ciudad` en paralelo, una por ciudad. Temuco devuelve Rio Tolten, Río Cautín y Río Cholchol. Villarica devuelve Río Trancura (R7). Angol devuelve una lista vacía: tiene ciudad y punto fluvial, y ningún río en `rios.json`.

El texto final nombra Río Toltén, Río Cautín y Río Trancura, y dice que Angol no tiene ríos. Río Cholchol iba en el resultado de Temuco y no aparece en ese texto. Hay una respuesta de `send_message`: 2657 tokens de entrada, 57 de salida, ≈ US$0.00094.

```text
Pregunta: ¿Qué ríos hay en la región de la Araucanía?
Tools: ['buscar_rios_por_ciudad', 'buscar_rios_por_nombre', 'buscar_ciudad_por_id', 'buscar_ciudad_por_region', 'buscar_ciudad_por_nombre', 'buscar_punto_por_id', 'buscar_punto_por_ciudad']

Respuesta: En la región de la Araucanía se encuentran el **Río Toltén**, el **Río Cautín** (ambos en Temuco) y el **Río Trancura** (en Villarrica). No se registraron ríos asociados a Angol.

Historial automático:
[user] ¿Qué ríos hay en la región de la Araucanía?
[model] pide buscar_ciudad_por_region({'nombre_region': 'Araucania'})
[user] resultado -> {'result': [{'id_ciudad': 'TEM', 'nombre_region': 'Araucania', 'nombre_ciudad': 'Temuco', 'habitantes': 120000, 'superficie_km2': 100}, {'id_ciudad': 'VIL', 'nombre_region': 'Araucania', 'nombre_ciudad': 'Villarica', 'habitantes': 180000, 'superficie_km2': 36}, {'id_ciudad': 'ANG', 'nombre_region': 'Araucania', 'nombre_ciudad': 'Angol', 'habitantes': 80000, 'superficie_km2': 67}]}
[model] pide buscar_rios_por_ciudad({'nombre_ciudad': 'Temuco'})
[model] pide buscar_rios_por_ciudad({'nombre_ciudad': 'Villarica'})
[model] pide buscar_rios_por_ciudad({'nombre_ciudad': 'Angol'})
[user] resultado -> {'result': [{'id_rio': 'R1', 'nombre_rio': 'Rio Tolten', 'id_ciudad': 'TEM'}, {'id_rio': 'R5', 'nombre_rio': 'Río Cautín', 'id_ciudad': 'TEM'}, {'id_rio': 'R6', 'nombre_rio': 'Río Cholchol', 'id_ciudad': 'TEM'}]}
[user] resultado -> {'result': [{'id_rio': 'R7', 'nombre_rio': 'Río Trancura', 'id_ciudad': 'VIL'}]}
[user] resultado -> {'result': []}
[model] En la región de la Araucanía se encuentran el **Río Toltén**, el **Río Cautín** (ambos en Temuco) y el **Río Trancura** (en Villarrica). No se registraron ríos asociados a Angol.
1 respuesta(s) de send_message | tokens entrada: 2657 | salida: 57 | costo ≈ US$0.00094
```


## Milímetros en cinco días de lluvia

La pregunta pide un total de agua caída. Los milímetros están en `puntos_fluviales.json`, otra vez por `id_ciudad`. El modelo usa dos vueltas y el producto lo calcula él.

Primero `buscar_ciudad_por_region` con `Araucania`: Temuco, Villarica y Angol.

Después tres `buscar_punto_por_ciudad`. Temuco devuelve P1 con 7 mm. Villarica devuelve P6 con 0.2 mm y P7 con 1.4 mm. Angol devuelve P8 con 4.2 mm. Son cuatro puntos.

La suma diaria es 7 + 0.2 + 1.4 + 4.2 = 12.8 mm. Por cinco días, 12.8 × 5 = 64 mm. El texto final dice eso: cuatro puntos en Temuco, Villarrica y Angol, y 64 mm en toda la región. En esta corrida no llama a las tools de ríos. Hay una respuesta de `send_message`: 2695 tokens de entrada, 58 de salida, ≈ US$0.00095.

```text
Pregunta: ¿Cuantos mm (milimetros) totales de agua caída se acumularían si llueve durante 5 días seguidos en la región de la Araucanía?
Tools: ['buscar_rios_por_ciudad', 'buscar_rios_por_nombre', 'buscar_ciudad_por_id', 'buscar_ciudad_por_region', 'buscar_ciudad_por_nombre', 'buscar_punto_por_id', 'buscar_punto_por_ciudad']

Respuesta: En la región de la Araucanía hay cuatro puntos de medición (Temuco, Villarrica y Angol). Con un promedio diario total de 12.8 mm, en 5 días seguidos se acumularían 64 mm de agua caída en toda la región.

Historial automático:
[user] ¿Cuantos mm (milimetros) totales de agua caída se acumularían si llueve durante 5 días seguidos en la región de la Araucanía?
[model] pide buscar_ciudad_por_region({'nombre_region': 'Araucania'})
[user] resultado -> {'result': [{'id_ciudad': 'TEM', 'nombre_region': 'Araucania', 'nombre_ciudad': 'Temuco', 'habitantes': 120000, 'superficie_km2': 100}, {'id_ciudad': 'VIL', 'nombre_region': 'Araucania', 'nombre_ciudad': 'Villarica', 'habitantes': 180000, 'superficie_km2': 36}, {'id_ciudad': 'ANG', 'nombre_region': 'Araucania', 'nombre_ciudad': 'Angol', 'habitantes': 80000, 'superficie_km2': 67}]}
[model] pide buscar_punto_por_ciudad({'nombre_ciudad': 'Temuco'})
[model] pide buscar_punto_por_ciudad({'nombre_ciudad': 'Villarica'})
[model] pide buscar_punto_por_ciudad({'nombre_ciudad': 'Angol'})
[user] resultado -> {'result': [{'id_punto': 'P1', 'id_ciudad': 'TEM', 'mm_acumulados_promedio': 7}]}
[user] resultado -> {'result': [{'id_punto': 'P6', 'id_ciudad': 'VIL', 'mm_acumulados_promedio': 0.2}, {'id_punto': 'P7', 'id_ciudad': 'VIL', 'mm_acumulados_promedio': 1.4}]}
[user] resultado -> {'result': [{'id_punto': 'P8', 'id_ciudad': 'ANG', 'mm_acumulados_promedio': 4.2}]}
[model] En la región de la Araucanía hay cuatro puntos de medición (Temuco, Villarrica y Angol). Con un promedio diario total de 12.8 mm, en 5 días seguidos se acumularían 64 mm de agua caída en toda la región.
1 respuesta(s) de send_message | tokens entrada: 2695 | salida: 58 | costo ≈ US$0.00095
```


## Ríos en riesgo de desborde

Esta pregunta junta las dos cadenas anteriores y agrega un umbral: sobre 60 mm el río se considera en riesgo. El modelo usa tres vueltas.

La primera es `buscar_ciudad_por_region` con `Araucania`. La segunda pide los puntos de Temuco, Villarica y Angol, los mismos cuatro de la consulta anterior. Cada promedio por cinco días queda así: Temuco 35 mm, Villarica 1 mm y 7 mm, Angol 21 mm. El mayor es 35 mm.

La tercera vuelta pide los ríos de las tres ciudades. Temuco devuelve Rio Tolten, Río Cautín y Río Cholchol. Villarica devuelve Río Trancura. Angol devuelve una lista vacía. El modelo ya tiene el umbral y los ríos, y cierra: ningún punto supera 60 mm, así que ningún río queda en riesgo de desborde.

El total regional de 64 mm es la suma de los cuatro puntos. El umbral de esta pregunta se aplica a cada punto, y ninguno llega a 60. Son siete llamadas de tool dentro del tope de 10. Hay una respuesta de `send_message`: 2932 tokens de entrada, 66 de salida, ≈ US$0.00104.

```text
Pregunta: Supongamos en que la región de la Araucanía llueve durante 5 días seguidos... ¿Que rios estarían estarían en riesgo de desborde (sobre 60 mm es considerado riesgoso)
Tools: ['buscar_rios_por_ciudad', 'buscar_rios_por_nombre', 'buscar_ciudad_por_id', 'buscar_ciudad_por_region', 'buscar_ciudad_por_nombre', 'buscar_punto_por_id', 'buscar_punto_por_ciudad']

Respuesta: Con 5 días de lluvia, multiplicando los promedios diarios, ningún punto fluvial en la Araucanía supera los 60 mm (el más alto es Temuco con 35 mm acumulados).
Por lo tanto, bajo este escenario, **ningún río** estaría en riesgo de desborde.

Historial automático:
[user] Supongamos en que la región de la Araucanía llueve durante 5 días seguidos... ¿Que rios estarían estarían en riesgo de desborde (sobre 60 mm es considerado riesgoso)
[model] pide buscar_ciudad_por_region({'nombre_region': 'Araucania'})
[user] resultado -> {'result': [{'id_ciudad': 'TEM', 'nombre_region': 'Araucania', 'nombre_ciudad': 'Temuco', 'habitantes': 120000, 'superficie_km2': 100}, {'id_ciudad': 'VIL', 'nombre_region': 'Araucania', 'nombre_ciudad': 'Villarica', 'habitantes': 180000, 'superficie_km2': 36}, {'id_ciudad': 'ANG', 'nombre_region': 'Araucania', 'nombre_ciudad': 'Angol', 'habitantes': 80000, 'superficie_km2': 67}]}
[model] pide buscar_punto_por_ciudad({'nombre_ciudad': 'Temuco'})
[model] pide buscar_punto_por_ciudad({'nombre_ciudad': 'Villarica'})
[model] pide buscar_punto_por_ciudad({'nombre_ciudad': 'Angol'})
[user] resultado -> {'result': [{'id_punto': 'P1', 'id_ciudad': 'TEM', 'mm_acumulados_promedio': 7}]}
[user] resultado -> {'result': [{'id_punto': 'P6', 'id_ciudad': 'VIL', 'mm_acumulados_promedio': 0.2}, {'id_punto': 'P7', 'id_ciudad': 'VIL', 'mm_acumulados_promedio': 1.4}]}
[user] resultado -> {'result': [{'id_punto': 'P8', 'id_ciudad': 'ANG', 'mm_acumulados_promedio': 4.2}]}
[model] pide buscar_rios_por_ciudad({'nombre_ciudad': 'Temuco'})
[model] pide buscar_rios_por_ciudad({'nombre_ciudad': 'Villarica'})
[model] pide buscar_rios_por_ciudad({'nombre_ciudad': 'Angol'})
[user] resultado -> {'result': [{'id_rio': 'R1', 'nombre_rio': 'Rio Tolten', 'id_ciudad': 'TEM'}, {'id_rio': 'R5', 'nombre_rio': 'Río Cautín', 'id_ciudad': 'TEM'}, {'id_rio': 'R6', 'nombre_rio': 'Río Cholchol', 'id_ciudad': 'TEM'}]}
[user] resultado -> {'result': [{'id_rio': 'R7', 'nombre_rio': 'Río Trancura', 'id_ciudad': 'VIL'}]}
[user] resultado -> {'result': []}
[model] Con 5 días de lluvia, multiplicando los promedios diarios, ningún punto fluvial en la Araucanía supera los 60 mm (el más alto es Temuco con 35 mm acumulados).
Por lo tanto, bajo este escenario, **ningún río** estaría en riesgo de desborde.
1 respuesta(s) de send_message | tokens entrada: 2932 | salida: 66 | costo ≈ US$0.00104
```
