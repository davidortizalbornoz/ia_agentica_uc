# Ejecución

Para ejecutar la parte guiada 2:

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

5. Activa el entorno e instala `google-genai`, `pandas` y `pydantic` si aún no están. La llamada y el modelo elegido (`MODEL`) salen de `CLASE_1/parte_guiada/common.py`. La key y `PREFERIDOS` se leen con `leer_clave` desde `CLASE_1/parte_guiada/entorno_local.py`. Los 31 correos salen de `1_practico_elproblema_ylosdatos.py`.

```bash
pyenv activate ia_agentica_uc
pip install google-genai pandas pydantic
```

6. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_2/parte_guiada/2_practico_3versionesde_systemprompt.py"
```

El script clasifica los 31 correos con tres system prompts: `v1_vago`, `v2_estructurado` y `v3_con_ejemplos`. Cada versión se consulta 3 ciclos, en una sola llamada por ciclo, con una pausa de 2 segundos entre llamadas. Son 9 llamadas al modelo. Mientras corre, imprime `Consultando <versión>, ciclo N de 3...`.

Al terminar muestra el modelo y estas tablas:

- **Respuesta del modelo:** por versión, la categoría de cada ciclo junto a `clasificacion`.
- **Ciclos:** aciertos, exactitud, fáciles y difíciles de cada ciclo.
- **Comparación:** promedio, mínimo y máximo de los 3 ciclos. Fáciles y difíciles salen del último ciclo.
- **Fórmulas:** `promedio = suma de aciertos / (ciclos × correos)`.
- **Dónde falla:** correos del último ciclo en los que `v2` o `v3` no coinciden con la clasificación. `v1` no entra.
- **Casos inestables:** correos en los que la misma versión (`v2` o `v3`) cambió la categoría entre ciclos. `clasificacion` y `dificultad` no cambian; cambian las columnas `Ciclo 1`, `Ciclo 2` y `Ciclo 3`.

Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

La consola empieza con `MODELO:` y una tabla de respuestas para `v1_vago` y otra para `v2_estructurado`. Este recorte es el resto de la misma ejecución.

```text
RESPUESTA DEL MODELO · v3_con_ejemplos
N   Correo                                            Clasificación  Ciclo 1      Ciclo 2      Ciclo 3
----------------------------------------------------------------------------------------------------------
1   La factura 7781 tiene el RUT equivocado, ¿pue...  facturacion    facturacion  facturacion  facturacion
2   No me llega el correo de confirmación cuando ...  tecnico        tecnico      tecnico      tecnico
3   El pedido P-1004 llegó con dos cajas rotas y ...  reclamo        reclamo      reclamo      reclamo
4   ¿Tienen cobertura a Punta Arenas?                 otro           otro         otro         otro
5   Pagué dos veces el mismo pedido, necesito la ...  facturacion    facturacion  facturacion  facturacion
6   La API devuelve error 500 al consultar el est...  tecnico        tecnico      tecnico      tecnico
7   Llevo tres días esperando respuesta de su eje...  reclamo        reclamo      reclamo      reclamo
8   Quisiera una cotización para 200 pallets mens...  otro           otro         otro         otro
9   ¿Pueden enviar la factura en formato electrón...  facturacion    facturacion  facturacion  facturacion
10  La app móvil se cierra sola al abrir el track...  tecnico        tecnico      tecnico      tecnico
11  El transportista fue grosero con nuestro bode...  reclamo        reclamo      reclamo      reclamo
12  ¿Cuál es el horario de recepción en la bodega...  otro           otro         otro         otro
13  El monto de la nota de crédito no coincide co...  facturacion    facturacion  facturacion  facturacion
14  No puedo restablecer mi contraseña, el link e...  tecnico        tecnico      tecnico      tecnico
15  Mi pedido dice entregado pero nunca llegó.        reclamo        reclamo      reclamo      reclamo
16  Gracias por resolver tan rápido el tema de la...  otro           facturacion  facturacion  facturacion
17  Qué maravilla, tercer despacho atrasado este ...  reclamo        reclamo      reclamo      reclamo
18  El tracking dice 'entregado' desde ayer, pero...  reclamo        reclamo      reclamo      reclamo
19  ¿Me pueden explicar por qué la factura de oct...  facturacion    facturacion  facturacion  facturacion
20  Necesito integrar su API con nuestro ERP, ¿ti...  otro           otro         tecnico      tecnico
21  Mi ejecutiva dijo que me llamaría el lunes po...  reclamo        reclamo      reclamo      reclamo
22  Hola, buenas tardes.                              otro           otro         otro         otro
23  El sistema muestra el P-1002 como 'en prepara...  tecnico        tecnico      tecnico      tecnico
24  Good morning, could you send me the invoice f...  facturacion    facturacion  facturacion  facturacion
25  Dejé de recibir notificaciones desde que camb...  tecnico        facturacion  tecnico      facturacion
26  ¿Pueden cotizar 50 pallets a Punta Arenas? La...  otro           otro         otro         otro
27  Se me olvidó la clave del portal, pero no es ...  tecnico        tecnico      tecnico      tecnico
28  Adjunto la foto de las cajas mojadas que lleg...  reclamo        reclamo      reclamo      reclamo
29  ¿El reembolso del pedido duplicado ya fue pro...  facturacion    facturacion  facturacion  facturacion
30  O pedido chegou com a embalagem rasgada e fal...  reclamo        reclamo      reclamo      reclamo
31  asdfgh 1234 prueba                                otro           otro         otro         otro

CICLOS  ·  31 correos, 3 ciclos por versión
Versión          Ciclo  Aciertos  Exactitud   Fáciles  Difíciles
----------------------------------------------------------------
v1_vago              1   0 de 31       0.0%   0 de 15    0 de 16
v1_vago              2   0 de 31       0.0%   0 de 15    0 de 16
v1_vago              3   0 de 31       0.0%   0 de 15    0 de 16
v2_estructurado      1  28 de 31      90.3%  15 de 15   13 de 16
v2_estructurado      2  28 de 31      90.3%  15 de 15   13 de 16
v2_estructurado      3  29 de 31      93.5%  15 de 15   14 de 16
v3_con_ejemplos      1  29 de 31      93.5%  15 de 15   14 de 16
v3_con_ejemplos      2  29 de 31      93.5%  15 de 15   14 de 16
v3_con_ejemplos      3  28 de 31      90.3%  15 de 15   13 de 16

COMPARACIÓN DE SYSTEM PROMPTS
Un acierto es un correo cuya categoría coincide con la clasificación.
Versión          Promedio  Mínimo  Máximo   Fáciles  Difíciles
--------------------------------------------------------------
v1_vago              0.0%    0.0%    0.0%   0 de 15    0 de 16
v2_estructurado     91.4%   90.3%   93.5%  15 de 15   14 de 16
v3_con_ejemplos     92.5%   90.3%   93.5%  15 de 15   13 de 16

FÓRMULAS
Promedio = suma de aciertos / (ciclos × correos). Mínimo y máximo salen del peor y del mejor ciclo.
Fáciles y difíciles de la comparación son los del último ciclo.
Versión          Aciertos de los ciclos               Promedio            Mínimo            Máximo
--------------------------------------------------------------------------------------------------
v1_vago                   0 + 0 + 0 = 0    0 / (3 × 31) = 0.0%    0 de 31 = 0.0%    0 de 31 = 0.0%
v2_estructurado       28 + 28 + 29 = 85  85 / (3 × 31) = 91.4%  28 de 31 = 90.3%  29 de 31 = 93.5%
v3_con_ejemplos       29 + 29 + 28 = 86  86 / (3 × 31) = 92.5%  28 de 31 = 90.3%  29 de 31 = 93.5%

DÓNDE FALLA
Último ciclo de v2 y v3. v1 no entra: inventa los nombres de las categorías.
N   Correo                                            Clasificación  Dificultad  v2_estructurado  v3_con_ejemplos
-----------------------------------------------------------------------------------------------------------------
16  Gracias por resolver tan rápido el tema de la...  otro           dificil     facturacion      facturacion
20  Necesito integrar su API con nuestro ERP, ¿ti...  otro           dificil     tecnico          tecnico
25  Dejé de recibir notificaciones desde que camb...  tecnico        dificil     tecnico          facturacion

CASOS INESTABLES
La misma versión cambió la categoría entre ciclos. v1 no entra.
Versión          Casos
----------------------
v2_estructurado      1
v3_con_ejemplos      2

Versión          N   Correo                                            Clasificación  Dificultad  Ciclo 1      Ciclo 2      Ciclo 3
---------------------------------------------------------------------------------------------------------------------------------------
v2_estructurado  25  Dejé de recibir notificaciones desde que camb...  tecnico        dificil     facturacion  facturacion  tecnico
v3_con_ejemplos  20  Necesito integrar su API con nuestro ERP, ¿ti...  otro           dificil     otro         tecnico      tecnico
v3_con_ejemplos  25  Dejé de recibir notificaciones desde que camb...  tecnico        dificil     facturacion  tecnico      facturacion
```
