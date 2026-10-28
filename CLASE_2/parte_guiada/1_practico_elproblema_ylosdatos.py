import warnings
warnings.filterwarnings("ignore", message="Pandas requires version")
import pandas as pd


CASOS = [
 # --- claros ---
 ("La factura 7781 tiene el RUT equivocado, ¿pueden reemitirla?", "facturacion", "facil"),
 ("No me llega el correo de confirmación cuando creo un pedido en la plataforma.", "tecnico", "facil"),
 ("El pedido P-1004 llegó con dos cajas rotas y nadie me avisó del retraso.", "reclamo", "facil"),
 ("¿Tienen cobertura a Punta Arenas?", "otro", "facil"),
 ("Pagué dos veces el mismo pedido, necesito la devolución.", "facturacion", "facil"),
 ("La API devuelve error 500 al consultar el estado de un pedido.", "tecnico", "facil"),
 ("Llevo tres días esperando respuesta de su ejecutiva, pésimo servicio.", "reclamo", "facil"),
 ("Quisiera una cotización para 200 pallets mensuales.", "otro", "facil"),
 ("¿Pueden enviar la factura en formato electrónico al nuevo correo de contabilidad?", "facturacion", "facil"),
 ("La app móvil se cierra sola al abrir el tracking.", "tecnico", "facil"),
 ("El transportista fue grosero con nuestro bodeguero.", "reclamo", "facil"),
 ("¿Cuál es el horario de recepción en la bodega de Santiago?", "otro", "facil"),
 ("El monto de la nota de crédito no coincide con lo acordado.", "facturacion", "facil"),
 ("No puedo restablecer mi contraseña, el link expira de inmediato.", "tecnico", "facil"),
 ("Mi pedido dice entregado pero nunca llegó.", "reclamo", "facil"),
 # --- difíciles: palabra clave engañosa, sarcasmo, dos temas, otro idioma, sin contenido ---
 ("Gracias por resolver tan rápido el tema de la factura, quedó perfecta.", "otro", "dificil"),            # elogio con la palabra "factura"
 ("Qué maravilla, tercer despacho atrasado este mes. Felicitaciones al equipo.", "reclamo", "dificil"),     # sarcasmo
 ("El tracking dice 'entregado' desde ayer, pero nuestra bodega estaba cerrada. ¿Dónde lo dejaron?", "reclamo", "dificil"),  # pregunta, pero entrega no realizada
 ("¿Me pueden explicar por qué la factura de octubre viene con un recargo por 'manejo especial'?", "facturacion", "dificil"),  # pregunta sobre factura, no reclamo
 ("Necesito integrar su API con nuestro ERP, ¿tienen documentación o un ejecutivo técnico?", "otro", "dificil"),  # "API" pero es consulta comercial, no hay error
 ("Mi ejecutiva dijo que me llamaría el lunes por la nota de crédito y nunca llamó.", "reclamo", "dificil"),   # molestia por servicio, aunque mencione nota de crédito
 ("Hola, buenas tardes.", "otro", "dificil"),                                                                   # sin contenido
 ("El sistema muestra el P-1002 como 'en preparación' pero ya lo recibí. ¿Es un error de la plataforma?", "tecnico", "dificil"),  # error de datos, sin daño
 ("Good morning, could you send me the invoice for order P-1001 in English?", "facturacion", "dificil"),       # otro idioma
 ("Dejé de recibir notificaciones desde que cambié mi contraseña; además la última factura tiene mal la dirección.", "tecnico", "dificil"),  # dos temas: gana el primero
 ("¿Pueden cotizar 50 pallets a Punta Arenas? La última vez el precio me pareció alto.", "otro", "dificil"),   # cotización con queja leve
 ("Se me olvidó la clave del portal, pero no es urgente, cuando puedan.", "tecnico", "dificil"),               # tono amable, sigue siendo técnico
 ("Adjunto la foto de las cajas mojadas que llegaron hoy.", "reclamo", "dificil"),                             # reclamo implícito
 ("¿El reembolso del pedido duplicado ya fue procesado? Me dijeron 5 días hábiles y van 8.", "facturacion", "dificil"),  # pide dinero → facturación, aunque haya demora
 ("O pedido chegou com a embalagem rasgada e faltando duas caixas.", "reclamo", "dificil"),                    # portugués
 ("asdfgh 1234 prueba", "otro", "dificil"),                                                                    # basura
]
df = pd.DataFrame(CASOS, columns=["correo", "clasificacion", "dificultad"])

if __name__ == "__main__":
    pd.set_option("display.max_rows", 40)
    pd.set_option("display.max_colwidth", 120)
    pd.set_option("display.width", 160)
    conteo = df.dificultad.value_counts()
    print(f"Casos: {len(df)} | faciles: {int(conteo.get('facil', 0))} | dificiles: {int(conteo.get('dificil', 0))}")
    print(df)
