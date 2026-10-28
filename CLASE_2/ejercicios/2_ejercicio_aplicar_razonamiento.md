# Ejecución

Para ejecutar el ejercicio 2:

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

5. Activa el entorno e instala `google-genai`, `pandas` y `pydantic` si aún no están. La llamada, el modelo elegido (`MODEL`) y `costo_usd` salen de `CLASE_1/parte_guiada/common.py`. La key y `PREFERIDOS` se leen con `leer_clave` desde `CLASE_1/parte_guiada/entorno_local.py`. Los 31 correos salen de `CLASE_2/parte_guiada/1_practico_elproblema_ylosdatos.py`.

```bash
pyenv activate ia_agentica_uc
pip install google-genai pandas pydantic
```

6. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_2/ejercicios/2_ejercicio_aplicar_razonamiento.py"
```

El script clasifica los 31 correos con el mismo texto en dos versiones: `v2_estructurado` y `v2_razonamiento`. La segunda pide razonamiento alto (`ThinkingLevel.HIGH`) e incluye los pensamientos del modelo. Cada versión se consulta 3 ciclos, en una sola llamada por ciclo, con una pausa de 2 segundos entre llamadas. Son 6 llamadas al modelo. Mientras corre, imprime `Consultando <versión>, ciclo N de 3...`.

Al terminar muestra el modelo y estas tablas:

- **Respuesta del modelo:** por versión, la categoría de cada ciclo junto a `clasificacion`.
- **Ciclos:** aciertos, exactitud, fáciles y difíciles de cada ciclo.
- **Comparación:** promedio, mínimo y máximo de los 3 ciclos. Fáciles y difíciles salen del último ciclo.
- **Fórmulas:** `promedio = suma de aciertos / (ciclos × correos)`.
- **Dónde falla:** correos del último ciclo en los que `v2_estructurado` o `v2_razonamiento` no coinciden con la clasificación.
- **Casos inestables:** correos en los que la misma versión cambió la categoría entre ciclos.
- **Tokens y costo:** tokens del prompt, tokens de salida y costo estimado de cada ciclo, con un total por versión. Los tokens de salida suman la respuesta y el razonamiento. El costo usa el precio del nivel de pago.

Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

```text
Consultando v2_estructurado, ciclo 1 de 3...
Consultando v2_estructurado, ciclo 2 de 3...
Consultando v2_estructurado, ciclo 3 de 3...
Consultando v2_razonamiento, ciclo 1 de 3...
Consultando v2_razonamiento, ciclo 2 de 3...
Consultando v2_razonamiento, ciclo 3 de 3...

MODELO: gemini-3.5-flash-lite

RESPUESTA DEL MODELO · v2_estructurado
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
20  Necesito integrar su API con nuestro ERP, ¿ti...  otro           tecnico      tecnico      tecnico    
21  Mi ejecutiva dijo que me llamaría el lunes po...  reclamo        reclamo      reclamo      reclamo    
22  Hola, buenas tardes.                              otro           otro         otro         otro       
23  El sistema muestra el P-1002 como 'en prepara...  tecnico        tecnico      tecnico      tecnico    
24  Good morning, could you send me the invoice f...  facturacion    facturacion  facturacion  facturacion
25  Dejé de recibir notificaciones desde que camb...  tecnico        facturacion  facturacion  facturacion
26  ¿Pueden cotizar 50 pallets a Punta Arenas? La...  otro           otro         otro         otro       
27  Se me olvidó la clave del portal, pero no es ...  tecnico        tecnico      tecnico      tecnico    
28  Adjunto la foto de las cajas mojadas que lleg...  reclamo        reclamo      reclamo      reclamo    
29  ¿El reembolso del pedido duplicado ya fue pro...  facturacion    facturacion  facturacion  facturacion
30  O pedido chegou com a embalagem rasgada e fal...  reclamo        reclamo      reclamo      reclamo    
31  asdfgh 1234 prueba                                otro           otro         otro         otro       

RESPUESTA DEL MODELO · v2_razonamiento
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
20  Necesito integrar su API con nuestro ERP, ¿ti...  otro           tecnico      tecnico      tecnico    
21  Mi ejecutiva dijo que me llamaría el lunes po...  reclamo        facturacion  facturacion  facturacion
22  Hola, buenas tardes.                              otro           otro         otro         otro       
23  El sistema muestra el P-1002 como 'en prepara...  tecnico        tecnico      tecnico      tecnico    
24  Good morning, could you send me the invoice f...  facturacion    facturacion  facturacion  facturacion
25  Dejé de recibir notificaciones desde que camb...  tecnico        facturacion  facturacion  tecnico    
26  ¿Pueden cotizar 50 pallets a Punta Arenas? La...  otro           otro         otro         otro       
27  Se me olvidó la clave del portal, pero no es ...  tecnico        tecnico      tecnico      tecnico    
28  Adjunto la foto de las cajas mojadas que lleg...  reclamo        reclamo      reclamo      reclamo    
29  ¿El reembolso del pedido duplicado ya fue pro...  facturacion    facturacion  facturacion  facturacion
30  O pedido chegou com a embalagem rasgada e fal...  reclamo        reclamo      reclamo      reclamo    
31  asdfgh 1234 prueba                                otro           otro         otro         otro       

CICLOS  ·  31 correos, 3 ciclos por versión
Versión          Ciclo  Aciertos  Exactitud   Fáciles  Difíciles
----------------------------------------------------------------
v2_estructurado      1  28 de 31      90.3%  15 de 15   13 de 16
v2_estructurado      2  28 de 31      90.3%  15 de 15   13 de 16
v2_estructurado      3  28 de 31      90.3%  15 de 15   13 de 16
v2_razonamiento      1  27 de 31      87.1%  15 de 15   12 de 16
v2_razonamiento      2  27 de 31      87.1%  15 de 15   12 de 16
v2_razonamiento      3  28 de 31      90.3%  15 de 15   13 de 16

COMPARACIÓN DE SYSTEM PROMPTS
Un acierto es un correo cuya categoría coincide con la clasificación.
Versión          Promedio  Mínimo  Máximo   Fáciles  Difíciles
--------------------------------------------------------------
v2_estructurado     90.3%   90.3%   90.3%  15 de 15   13 de 16
v2_razonamiento     88.2%   87.1%   90.3%  15 de 15   13 de 16

FÓRMULAS
Promedio = suma de aciertos / (ciclos × correos). Mínimo y máximo salen del peor y del mejor ciclo.
Fáciles y difíciles de la comparación son los del último ciclo.
Versión          Aciertos de los ciclos               Promedio            Mínimo            Máximo
--------------------------------------------------------------------------------------------------
v2_estructurado       28 + 28 + 28 = 84  84 / (3 × 31) = 90.3%  28 de 31 = 90.3%  28 de 31 = 90.3%
v2_razonamiento       27 + 27 + 28 = 82  82 / (3 × 31) = 88.2%  27 de 31 = 87.1%  28 de 31 = 90.3%

DÓNDE FALLA
Último ciclo de v2_estructurado y v2_razonamiento.
N   Correo                                            Clasificación  Dificultad  v2_estructurado  v2_razonamiento
-----------------------------------------------------------------------------------------------------------------
16  Gracias por resolver tan rápido el tema de la...  otro           dificil     facturacion      facturacion    
20  Necesito integrar su API con nuestro ERP, ¿ti...  otro           dificil     tecnico          tecnico        
21  Mi ejecutiva dijo que me llamaría el lunes po...  reclamo        dificil     reclamo          facturacion    
25  Dejé de recibir notificaciones desde que camb...  tecnico        dificil     facturacion      tecnico        

CASOS INESTABLES
La misma versión cambió la categoría entre ciclos.
Versión          Casos
----------------------
v2_estructurado      0
v2_razonamiento      1

Versión          N   Correo                                            Clasificación  Dificultad  Ciclo 1      Ciclo 2      Ciclo 3
-----------------------------------------------------------------------------------------------------------------------------------
v2_razonamiento  25  Dejé de recibir notificaciones desde que camb...  tecnico        dificil     facturacion  facturacion  tecnico

TOKENS Y COSTO
Tokens de salida = respuesta + razonamiento.
El costo estimado incluye el prompt y la salida, a precio del nivel de pago.
El total suma los ciclos de cada prompt.
Versión          Ciclo  Tokens del prompt  Tokens de salida  Costo estimado
---------------------------------------------------------------------------
v2_estructurado      1                762               307     US$0.000996
v2_estructurado      2                762               307     US$0.000996
v2_estructurado      3                762               502     US$0.001484
v2_estructurado  Total               2286              1116     US$0.003476
v2_razonamiento      1                762              2248     US$0.005849
v2_razonamiento      2                762              2811     US$0.007256
v2_razonamiento      3                762              2401     US$0.006231
v2_razonamiento  Total               2286              7460     US$0.019336
```
