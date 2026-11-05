# Ejecución

Para ejecutar la parte guiada 1:

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

3. Activa el entorno. Este script no llama a un modelo y no instala paquetes: usa la biblioteca estándar.

```bash
pyenv activate ia_agentica_uc
```

4. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_3/parte_guiada/1_practico_datos_andina_cargo.py"
```

El script escribe tres JSON en `CLASE_3/parte_guiada/data/`: `pedidos.json` (5 pedidos), `stock.json` (4 SKU) y `dias_despacho.json` (5 ciudades). Si la carpeta `data/` no existe, la crea. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

```text
5 pedidos, 4 SKUs y 5 lugares de despacho guardados en /Users/Ext_DHOrtizA/Desktop/DavidOrtiz/UC/repo/ia_agentica_uc/CLASE_3/parte_guiada/data/
```
