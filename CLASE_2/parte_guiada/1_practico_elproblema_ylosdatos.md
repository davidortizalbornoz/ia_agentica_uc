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

3. Activa el entorno e instala `pandas` si aún no está. Este script no llama a un modelo: arma el dataframe de 31 correos ya etiquetados.

```bash
pyenv activate ia_agentica_uc
pip install pandas
```

4. Desde la consola del IDE, en la raíz del proyecto:

```bash
python "CLASE_2/parte_guiada/1_practico_elproblema_ylosdatos.py"
```

El script carga 31 correos de Andina Cargo con las columnas `correo`, `clasificacion` y `dificultad`. Los 15 primeros son claros (`facil`) y los 16 siguientes son ambiguos (`dificil`): sarcasmo, una palabra clave engañosa, dos temas, otro idioma o un correo sin contenido. La clasificación es una de `facturacion`, `tecnico`, `reclamo` u `otro`. Imprime el conteo y la tabla. Comprueba el intérprete con `python --version`; tiene que mostrar `Python 3.13.5`.

## Ejemplo de ejecución

```text
Casos: 31 | faciles: 15 | dificiles: 16
                                                                                                             correo clasificacion dificultad
0                                                      La factura 7781 tiene el RUT equivocado, ¿pueden reemitirla?   facturacion      facil
1                                     No me llega el correo de confirmación cuando creo un pedido en la plataforma.       tecnico      facil
2                                          El pedido P-1004 llegó con dos cajas rotas y nadie me avisó del retraso.       reclamo      facil
3                                                                                 ¿Tienen cobertura a Punta Arenas?          otro      facil
4                                                          Pagué dos veces el mismo pedido, necesito la devolución.   facturacion      facil
5                                                    La API devuelve error 500 al consultar el estado de un pedido.       tecnico      facil
6                                             Llevo tres días esperando respuesta de su ejecutiva, pésimo servicio.       reclamo      facil
7                                                               Quisiera una cotización para 200 pallets mensuales.          otro      facil
8                                 ¿Pueden enviar la factura en formato electrónico al nuevo correo de contabilidad?   facturacion      facil
9                                                                 La app móvil se cierra sola al abrir el tracking.       tecnico      facil
10                                                              El transportista fue grosero con nuestro bodeguero.       reclamo      facil
11                                                       ¿Cuál es el horario de recepción en la bodega de Santiago?          otro      facil
12                                                      El monto de la nota de crédito no coincide con lo acordado.   facturacion      facil
13                                                 No puedo restablecer mi contraseña, el link expira de inmediato.       tecnico      facil
14                                                                       Mi pedido dice entregado pero nunca llegó.       reclamo      facil
15                                           Gracias por resolver tan rápido el tema de la factura, quedó perfecta.          otro    dificil
16                                      Qué maravilla, tercer despacho atrasado este mes. Felicitaciones al equipo.       reclamo    dificil
17                  El tracking dice 'entregado' desde ayer, pero nuestra bodega estaba cerrada. ¿Dónde lo dejaron?       reclamo    dificil
18                    ¿Me pueden explicar por qué la factura de octubre viene con un recargo por 'manejo especial'?   facturacion    dificil
19                          Necesito integrar su API con nuestro ERP, ¿tienen documentación o un ejecutivo técnico?          otro    dificil
20                                 Mi ejecutiva dijo que me llamaría el lunes por la nota de crédito y nunca llamó.       reclamo    dificil
21                                                                                             Hola, buenas tardes.          otro    dificil
22             El sistema muestra el P-1002 como 'en preparación' pero ya lo recibí. ¿Es un error de la plataforma?       tecnico    dificil
23                                         Good morning, could you send me the invoice for order P-1001 in English?   facturacion    dificil
24  Dejé de recibir notificaciones desde que cambié mi contraseña; además la última factura tiene mal la dirección.       tecnico    dificil
25                              ¿Pueden cotizar 50 pallets a Punta Arenas? La última vez el precio me pareció alto.          otro    dificil
26                                             Se me olvidó la clave del portal, pero no es urgente, cuando puedan.       tecnico    dificil
27                                                           Adjunto la foto de las cajas mojadas que llegaron hoy.       reclamo    dificil
28                          ¿El reembolso del pedido duplicado ya fue procesado? Me dijeron 5 días hábiles y van 8.   facturacion    dificil
29                                                  O pedido chegou com a embalagem rasgada e faltando duas caixas.       reclamo    dificil
30                                                                                               asdfgh 1234 prueba          otro    dificil
```
