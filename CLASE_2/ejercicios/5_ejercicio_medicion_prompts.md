# Ejecución

Para ejecutar el ejercicio 5:

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

5. Activa el entorno e instala `google-genai`, `pandas` y `pydantic` si aún no están. La llamada y el modelo elegido (`MODEL`) salen de `CLASE_1/parte_guiada/common.py`. La key y `PREFERIDOS` se leen con `leer_clave` desde `CLASE_1/parte_guiada/entorno_local.py`. Los 18 tickets salen de `4_ejercicio_casos_tickets_jira.py`.

```bash
pyenv activate ia_agentica_uc
pip install google-genai pandas pydantic
```

6. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_2/ejercicios/5_ejercicio_medicion_prompts.py"
```

El script asigna la prioridad de los 18 tickets con dos system prompts: `v2_estructurado` y `v3_con_ejemplos`. Las dos versiones comparten el texto de categorías y prioridades. `v3` agrega reglas de ejemplo. Cada versión se consulta 3 ciclos, en una sola llamada por ciclo, con una pausa de 2 segundos entre llamadas. Son 6 llamadas al modelo. Mientras corre, imprime `Consultando <versión>, ciclo N de 3...`.

La respuesta de cada llamada es una lista de ticket y prioridad. El formato se fuerza con `response_mime_type="application/json"` y el esquema `Lote`. La medición compara la prioridad devuelta con la columna `prioridad`.

Al terminar muestra el modelo y estas tablas:

- **Respuesta del modelo:** por versión, la prioridad de cada ciclo junto a `categoria` y `prioridad`.
- **Ciclos:** aciertos, exactitud, desarrollo, despliegue y monitoreo de cada ciclo.
- **Comparación:** promedio, mínimo y máximo de los 3 ciclos. Desarrollo, despliegue y monitoreo salen del último ciclo.
- **Fórmulas:** `promedio = suma de aciertos / (ciclos × tickets)`.
- **Dónde falla:** tickets del último ciclo en los que `v2_estructurado` o `v3_con_ejemplos` no coinciden con la prioridad esperada.
- **Casos inestables:** tickets en los que la misma versión cambió la prioridad entre ciclos.

Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

```text
Consultando v2_estructurado, ciclo 1 de 3...
Consultando v2_estructurado, ciclo 2 de 3...
Consultando v2_estructurado, ciclo 3 de 3...
Consultando v3_con_ejemplos, ciclo 1 de 3...
Consultando v3_con_ejemplos, ciclo 2 de 3...
Consultando v3_con_ejemplos, ciclo 3 de 3...

MODELO: gemini-3.5-flash-lite

RESPUESTA DEL MODELO · v2_estructurado
N   Ticket                                                                    Categoría   Prioridad  Ciclo 1  Ciclo 2  Ciclo 3
------------------------------------------------------------------------------------------------------------------------------
1   idTicket DEV-1842 idProject CHECKOUT owner ana.rios assignedTo luis.m...  desarrollo  alta       alta     media    alta   
2   idTicket DEV-1901 idProject AUTH owner carmen.vega assignedTo pedro.s...  desarrollo  alta       alta     alta     alta   
3   idTicket DEV-1766 idProject CATALOG owner sofia.leon assignedTo diego...  desarrollo  media      media    media    media  
4   idTicket DEV-2014 idProject NOTIFY owner maria.paz assignedTo javier....  desarrollo  media      media    baja     media  
5   idTicket DEV-1550 idProject AUTH owner elena.ortiz assignedTo tomas.i...  desarrollo  baja       baja     baja     baja   
6   idTicket DEV-1622 idProject ORDERS owner luis.mora assignedTo ana.rio...  desarrollo  baja       baja     baja     baja   
7   idTicket DEP-331 idProject PAYMENTS owner pedro.salas assignedTo carm...  despliegue  alta       alta     alta     alta   
8   idTicket DEP-348 idProject BILLING owner diego.cruz assignedTo sofia....  despliegue  alta       alta     alta     alta   
9   idTicket DEP-290 idProject SEARCH owner javier.nunez assignedTo maria...  despliegue  media      media    media    media  
10  idTicket DEP-307 idProject INVENTORY owner tomas.ibanez assignedTo el...  despliegue  media      media    media    media  
11  idTicket DEP-214 idProject CATALOG owner ana.rios assignedTo diego.cr...  despliegue  baja       baja     baja     baja   
12  idTicket DEP-228 idProject NOTIFY owner carmen.vega assignedTo luis.m...  despliegue  baja       baja     baja     baja   
13  idTicket MON-88 idProject PAYMENTS owner sofia.leon assignedTo pedro....  monitoreo   alta       alta     alta     alta   
14  idTicket MON-91 idProject ORDERS owner javier.nunez assignedTo tomas....  monitoreo   alta       alta     alta     alta   
15  idTicket MON-74 idProject INVENTORY owner elena.ortiz assignedTo mari...  monitoreo   media      media    media    media  
16  idTicket MON-69 idProject BILLING owner diego.cruz assignedTo carmen....  monitoreo   media      media    media    media  
17  idTicket MON-41 idProject REPORTS owner luis.mora assignedTo sofia.le...  monitoreo   baja       baja     baja     baja   
18  idTicket MON-53 idProject SEARCH owner maria.paz assignedTo javier.nu...  monitoreo   baja       baja     baja     baja   

RESPUESTA DEL MODELO · v3_con_ejemplos
N   Ticket                                                                    Categoría   Prioridad  Ciclo 1  Ciclo 2  Ciclo 3
------------------------------------------------------------------------------------------------------------------------------
1   idTicket DEV-1842 idProject CHECKOUT owner ana.rios assignedTo luis.m...  desarrollo  alta       alta     alta     alta   
2   idTicket DEV-1901 idProject AUTH owner carmen.vega assignedTo pedro.s...  desarrollo  alta       alta     alta     alta   
3   idTicket DEV-1766 idProject CATALOG owner sofia.leon assignedTo diego...  desarrollo  media      media    media    media  
4   idTicket DEV-2014 idProject NOTIFY owner maria.paz assignedTo javier....  desarrollo  media      media    media    media  
5   idTicket DEV-1550 idProject AUTH owner elena.ortiz assignedTo tomas.i...  desarrollo  baja       baja     baja     baja   
6   idTicket DEV-1622 idProject ORDERS owner luis.mora assignedTo ana.rio...  desarrollo  baja       baja     baja     baja   
7   idTicket DEP-331 idProject PAYMENTS owner pedro.salas assignedTo carm...  despliegue  alta       alta     alta     alta   
8   idTicket DEP-348 idProject BILLING owner diego.cruz assignedTo sofia....  despliegue  alta       alta     alta     alta   
9   idTicket DEP-290 idProject SEARCH owner javier.nunez assignedTo maria...  despliegue  media      media    media    media  
10  idTicket DEP-307 idProject INVENTORY owner tomas.ibanez assignedTo el...  despliegue  media      media    media    media  
11  idTicket DEP-214 idProject CATALOG owner ana.rios assignedTo diego.cr...  despliegue  baja       baja     baja     baja   
12  idTicket DEP-228 idProject NOTIFY owner carmen.vega assignedTo luis.m...  despliegue  baja       baja     baja     baja   
13  idTicket MON-88 idProject PAYMENTS owner sofia.leon assignedTo pedro....  monitoreo   alta       alta     alta     alta   
14  idTicket MON-91 idProject ORDERS owner javier.nunez assignedTo tomas....  monitoreo   alta       alta     alta     alta   
15  idTicket MON-74 idProject INVENTORY owner elena.ortiz assignedTo mari...  monitoreo   media      media    media    media  
16  idTicket MON-69 idProject BILLING owner diego.cruz assignedTo carmen....  monitoreo   media      media    media    media  
17  idTicket MON-41 idProject REPORTS owner luis.mora assignedTo sofia.le...  monitoreo   baja       baja     baja     baja   
18  idTicket MON-53 idProject SEARCH owner maria.paz assignedTo javier.nu...  monitoreo   baja       baja     baja     baja   

CICLOS  ·  18 tickets, 3 ciclos por versión
Versión          Ciclo  Aciertos  Exactitud  Desarrollo  Despliegue  Monitoreo
------------------------------------------------------------------------------
v2_estructurado      1  18 de 18     100.0%      6 de 6      6 de 6     6 de 6
v2_estructurado      2  16 de 18      88.9%      4 de 6      6 de 6     6 de 6
v2_estructurado      3  18 de 18     100.0%      6 de 6      6 de 6     6 de 6
v3_con_ejemplos      1  18 de 18     100.0%      6 de 6      6 de 6     6 de 6
v3_con_ejemplos      2  18 de 18     100.0%      6 de 6      6 de 6     6 de 6
v3_con_ejemplos      3  18 de 18     100.0%      6 de 6      6 de 6     6 de 6

COMPARACIÓN DE SYSTEM PROMPTS
Un acierto es un ticket cuya prioridad coincide con la prioridad esperada.
Versión          Promedio  Mínimo  Máximo  Desarrollo  Despliegue  Monitoreo
----------------------------------------------------------------------------
v2_estructurado     96.3%   88.9%  100.0%      6 de 6      6 de 6     6 de 6
v3_con_ejemplos    100.0%  100.0%  100.0%      6 de 6      6 de 6     6 de 6

FÓRMULAS
Promedio = suma de aciertos / (ciclos × tickets). Mínimo y máximo salen del peor y del mejor ciclo.
Desarrollo, despliegue y monitoreo de la comparación son los del último ciclo.
Versión          Aciertos de los ciclos                Promedio             Mínimo             Máximo
-----------------------------------------------------------------------------------------------------
v2_estructurado       18 + 16 + 18 = 52   52 / (3 × 18) = 96.3%   16 de 18 = 88.9%  18 de 18 = 100.0%
v3_con_ejemplos       18 + 18 + 18 = 54  54 / (3 × 18) = 100.0%  18 de 18 = 100.0%  18 de 18 = 100.0%

DÓNDE FALLA
Último ciclo de v2_estructurado y v3_con_ejemplos.
Las dos versiones coincidieron con la prioridad esperada en todos los tickets.

CASOS INESTABLES
La misma versión cambió la prioridad entre ciclos.
Versión          Casos
----------------------
v2_estructurado      2
v3_con_ejemplos      0

Versión          N  Ticket                                                                    Categoría   Prioridad  Ciclo 1  Ciclo 2  Ciclo 3
----------------------------------------------------------------------------------------------------------------------------------------------
v2_estructurado  1  idTicket DEV-1842 idProject CHECKOUT owner ana.rios assignedTo luis.m...  desarrollo  alta       alta     media    alta   
v2_estructurado  4  idTicket DEV-2014 idProject NOTIFY owner maria.paz assignedTo javier....  desarrollo  media      media    baja     media  
```
