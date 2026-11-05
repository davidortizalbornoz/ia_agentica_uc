# Ejecución

Para ejecutar el ejercicio 1 de contrato:

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

3. Activa el entorno e instala `google-genai` si aún no está. El script arma el contrato con `FunctionDeclaration` y carga `fecha_estimada_entrega` desde `1_ejercicio_funciones.py`. Esta ejecución no llama al modelo. El JSON que lee esa función lo escribe `CLASE_3/parte_guiada/1_practico_datos_andina_cargo.py`.

```bash
pyenv activate ia_agentica_uc
pip install google-genai
```

4. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_3/ejercicios/1_ejercicio_contrato.py"
```

El script declara una sola tool, `fecha_estimada_entrega`, y la deja en `TOOLS` y `FUNCIONES`. `buscar_pedido` y `consultar_stock` quedan fuera de este contrato. El modelo vería el nombre, la descripción y el parámetro `id_pedido`; nunca el código. Al ejecutarse imprime el nombre declarado. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

```text
Tools declaradas: ['fecha_estimada_entrega']
```
