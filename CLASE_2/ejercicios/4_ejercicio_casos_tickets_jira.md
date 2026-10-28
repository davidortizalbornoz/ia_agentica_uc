# Ejecución

Para ejecutar el ejercicio 4:

1. Clona el repositorio.

```bash
git clone https://github.com/davidortizalbornoz/ia_agentica_uc.git
cd ia_agentica_uc
```

2. Usa Python 3.13.5. El archivo `.python-version` de la raíz apunta al entorno de pyenv `ia_agentica_uc`, creado sobre esa versión. Clonar el repositorio no instala el intérprete ni el entorno: hay que tenerlos en la máquina.

```bash
pyenv install 3.13.5
pyenv virtualenv 3.13.5 ia_agentica_uc
```

Si la consola ya tiene `PYENV_VERSION` definida (por ejemplo en 3.9.18), esa variable pisa a `.python-version`. Quítala antes de activar el entorno:

```bash
unset PYENV_VERSION
```

3. Activa el entorno e instala `pandas` si aún no está. Este script no llama a un modelo: arma el dataframe de 18 tickets ya etiquetados.

```bash
pyenv activate ia_agentica_uc
pip install pandas
```

4. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_2/ejercicios/4_ejercicio_casos_tickets_jira.py"
```

El script carga 18 tickets con las columnas `contexto`, `categoria` y `prioridad`. Hay 6 de `desarrollo`, 6 de `despliegue` y 6 de `monitoreo`. En cada categoría hay 2 de prioridad `alta`, 2 de `media` y 2 de `baja`. Imprime el conteo y la tabla. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

```text
Casos: 18 | desarrollo: 6 | despliegue: 6 | monitoreo: 6 | alta: 6 | media: 6 | baja: 6
                                                                                                                                                           contexto   categoria prioridad
0   idTicket DEV-1842 idProject CHECKOUT owner ana.rios assignedTo luis.mora dateCreated 2026-10-12 status InProgress details NullPointer al calcular el total d...  desarrollo      alta
1   idTicket DEV-1901 idProject AUTH owner carmen.vega assignedTo pedro.salas dateCreated 2026-10-18 status Blocked details Los tests de regresión de login fall...  desarrollo      alta
2   idTicket DEV-1766 idProject CATALOG owner sofia.leon assignedTo diego.cruz dateCreated 2026-10-08 status InReview details El filtro de productos no pagina y...  desarrollo     media
3   idTicket DEV-2014 idProject NOTIFY owner maria.paz assignedTo javier.nunez dateCreated 2026-10-21 status Open details Conflicto de merge en el módulo de pla...  desarrollo     media
4   idTicket DEV-1550 idProject AUTH owner elena.ortiz assignedTo tomas.ibanez dateCreated 2026-09-29 status ToDo details Typo en el mensaje de error del formul...  desarrollo      baja
5   idTicket DEV-1622 idProject ORDERS owner luis.mora assignedTo ana.rios dateCreated 2026-10-02 status Open details Warning de dependencia deprecada en el cli...  desarrollo      baja
6   idTicket DEP-331 idProject PAYMENTS owner pedro.salas assignedTo carmen.vega dateCreated 2026-10-22 status Blocked details El pipeline de producción falló a...  despliegue      alta
7   idTicket DEP-348 idProject BILLING owner diego.cruz assignedTo sofia.leon dateCreated 2026-10-23 status InProgress details El rollback no terminó y producci...  despliegue      alta
8   idTicket DEP-290 idProject SEARCH owner javier.nunez assignedTo maria.paz dateCreated 2026-10-15 status Open details El deploy a staging expiró en el health...  despliegue     media
9   idTicket DEP-307 idProject INVENTORY owner tomas.ibanez assignedTo elena.ortiz dateCreated 2026-10-17 status InReview details Falta la variable de entorno d...  despliegue     media
10  idTicket DEP-214 idProject CATALOG owner ana.rios assignedTo diego.cruz dateCreated 2026-10-04 status Resolved details El job de assets estáticos a QA termi...  despliegue      baja
11  idTicket DEP-228 idProject NOTIFY owner carmen.vega assignedTo luis.mora dateCreated 2026-10-06 status ToDo details Warning en el deploy nocturno de configu...  despliegue      baja
12  idTicket MON-88 idProject PAYMENTS owner sofia.leon assignedTo pedro.salas dateCreated 2026-10-24 status Open details Alerta de tasa de error sobre 5 por ci...   monitoreo      alta
13  idTicket MON-91 idProject ORDERS owner javier.nunez assignedTo tomas.ibanez dateCreated 2026-10-24 status InProgress details Disco del nodo de logs al 95 po...   monitoreo      alta
14  idTicket MON-74 idProject INVENTORY owner elena.ortiz assignedTo maria.paz dateCreated 2026-10-19 status Open details Latencia p95 del API de stock por enci...   monitoreo     media
15  idTicket MON-69 idProject BILLING owner diego.cruz assignedTo carmen.vega dateCreated 2026-10-16 status Blocked details El dashboard de SLA no recibe datos ...   monitoreo     media
16  idTicket MON-41 idProject REPORTS owner luis.mora assignedTo sofia.leon dateCreated 2026-10-09 status Resolved details Alerta informativa de CPU en el worke...   monitoreo      baja
17  idTicket MON-53 idProject SEARCH owner maria.paz assignedTo javier.nunez dateCreated 2026-10-11 status ToDo details La métrica de la cola muestra ruido inte...   monitoreo      baja
```
