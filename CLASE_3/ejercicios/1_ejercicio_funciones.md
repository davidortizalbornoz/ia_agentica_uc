# Ejecución

Para ejecutar el ejercicio 1 de funciones:

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

3. Activa el entorno. Esta ejecución no llama al modelo y no importa `google-genai`. Lee `pedidos.json` de `CLASE_3/parte_guiada/data/`. Ese archivo lo escribe `CLASE_3/parte_guiada/1_practico_datos_andina_cargo.py`.

```bash
pyenv activate ia_agentica_uc
```

4. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_3/ejercicios/1_ejercicio_funciones.py"
```

El script llama a `fecha_estimada_entrega` tres veces, sin el modelo. Si el pedido ya fue despachado, suma `eta_dias` (días corridos) a `fecha_despacho` y devuelve la fecha en `YYYY-MM-DD`. P-1001 salió el 2026-10-15 con ETA de 2 días, así que la entrega estimada es 2026-10-17. P-1003 sigue en preparación y `fecha_despacho` es nula: no hay fecha que calcular. P-9999 no está en el JSON y la función devuelve un error. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

```text
Fecha estimada de entrega para P-1001 (despachado)
{'id': 'P-1001', 'fecha_despacho': '2026-10-15', 'eta_dias': 2, 'fecha_estimada_entrega': '2026-10-17'}

Fecha estimada de entrega para P-1003 (aún no despachado)
{'id': 'P-1003', 'estado': 'preparacion', 'mensaje': 'El pedido P-1003 aún no fue despachado (estado: preparacion). No hay fecha estimada de entrega.'}

Fecha estimada de entrega para P-9999 (no existe)
{'error': 'No existe el pedido P-9999'}
```
