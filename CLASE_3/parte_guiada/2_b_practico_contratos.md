# Ejecución

Para ejecutar la parte guiada 2b:

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

3. Activa el entorno e instala `google-genai` si aún no está. El script arma los contratos con `FunctionDeclaration` y carga `buscar_pedido` y `consultar_stock` desde `2_a_practico_funciones_.py`. Esta ejecución no llama al modelo. Los JSON que leen esas funciones los escribe `1_practico_datos_andina_cargo.py`.

```bash
pyenv activate ia_agentica_uc
pip install google-genai
```

4. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_3/parte_guiada/2_b_practico_contratos.py"
```

El script declara dos tools, `buscar_pedido` y `consultar_stock`, y las deja en `TOOLS` y `FUNCIONES`. `estimar_despacho` queda fuera de este contrato. Al ejecutarse imprime los nombres declarados. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

```text
Tools declaradas: ['buscar_pedido', 'consultar_stock']
```
