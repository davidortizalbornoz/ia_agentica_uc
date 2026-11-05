# Ejecución

Para ejecutar la parte guiada 2a:

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

`google-genai` pide Python 3.10 o superior, así que 3.13.5 es compatible. Si la consola ya tiene `PYENV_VERSION` definida (por ejemplo en 3.9.18), esa variable pisa a `.python-version`. Quítala antes de activar el entorno:

```bash
unset PYENV_VERSION
```

3. Activa el entorno e instala `google-genai` si aún no está. El script lo importa, pero esta ejecución no llama al modelo: lee los JSON de `CLASE_3/parte_guiada/data/`. Esos archivos los escribe `1_practico_datos_andina_cargo.py`.

```bash
pyenv activate ia_agentica_uc
pip install google-genai
```

4. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_3/parte_guiada/2_a_practico_funciones_.py"
```

El script llama tres funciones de Python, sin el modelo: `buscar_pedido("P-1004")`, `consultar_stock("CAJ-050")` y `estimar_despacho("Temuco")`. Cada una devuelve un diccionario. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

```text
Buscar Pedido ID: P-1004
{'id': 'P-1004', 'cliente': 'Ferretería Lagos', 'ciudad': 'Valparaíso', 'estado': 'retrasado', 'items': [{'sku': 'CAJ-050', 'cant': 40}], 'fecha_despacho': '2026-10-12', 'eta_dias': 3}

Consultar Stock para Producto SKU: CAJ-050
{'sku': 'CAJ-050', 'nombre': 'Caja cartón 50x50', 'stock': 0, 'bodega': 'Santiago'}

Estimar Despacho para Temuco
{'ciudad': 'Temuco', 'dias_habiles': 3}
```
