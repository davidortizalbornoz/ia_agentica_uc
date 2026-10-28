import warnings
warnings.filterwarnings("ignore", message="Pandas requires version")
import pandas as pd


MIS_CASOS = [
    # --- desarrollo ---
    ("idTicket DEV-1842 idProject CHECKOUT owner ana.rios assignedTo luis.mora dateCreated 2026-10-12 status InProgress details NullPointer al calcular el total del carrito con cupón.", "desarrollo", "alta"),
    ("idTicket DEV-1901 idProject AUTH owner carmen.vega assignedTo pedro.salas dateCreated 2026-10-18 status Blocked details Los tests de regresión de login fallan en main y frenan el release.", "desarrollo", "alta"),
    ("idTicket DEV-1766 idProject CATALOG owner sofia.leon assignedTo diego.cruz dateCreated 2026-10-08 status InReview details El filtro de productos no pagina y repite la primera página.", "desarrollo", "media"),
    ("idTicket DEV-2014 idProject NOTIFY owner maria.paz assignedTo javier.nunez dateCreated 2026-10-21 status Open details Conflicto de merge en el módulo de plantillas de correo.", "desarrollo", "media"),
    ("idTicket DEV-1550 idProject AUTH owner elena.ortiz assignedTo tomas.ibanez dateCreated 2026-09-29 status ToDo details Typo en el mensaje de error del formulario de registro.", "desarrollo", "baja"),
    ("idTicket DEV-1622 idProject ORDERS owner luis.mora assignedTo ana.rios dateCreated 2026-10-02 status Open details Warning de dependencia deprecada en el cliente interno de pedidos.", "desarrollo", "baja"),
    # --- despliegue ---
    ("idTicket DEP-331 idProject PAYMENTS owner pedro.salas assignedTo carmen.vega dateCreated 2026-10-22 status Blocked details El pipeline de producción falló a mitad y el servicio quedó caído.", "despliegue", "alta"),
    ("idTicket DEP-348 idProject BILLING owner diego.cruz assignedTo sofia.leon dateCreated 2026-10-23 status InProgress details El rollback no terminó y producción quedó con dos versiones mezcladas.", "despliegue", "alta"),
    ("idTicket DEP-290 idProject SEARCH owner javier.nunez assignedTo maria.paz dateCreated 2026-10-15 status Open details El deploy a staging expiró en el healthcheck del pod nuevo.", "despliegue", "media"),
    ("idTicket DEP-307 idProject INVENTORY owner tomas.ibanez assignedTo elena.ortiz dateCreated 2026-10-17 status InReview details Falta la variable de entorno de la cola en el release de staging.", "despliegue", "media"),
    ("idTicket DEP-214 idProject CATALOG owner ana.rios assignedTo diego.cruz dateCreated 2026-10-04 status Resolved details El job de assets estáticos a QA terminó con demora, sin corte.", "despliegue", "baja"),
    ("idTicket DEP-228 idProject NOTIFY owner carmen.vega assignedTo luis.mora dateCreated 2026-10-06 status ToDo details Warning en el deploy nocturno de configuración, sin impacto.", "despliegue", "baja"),
    # --- monitoreo ---
    ("idTicket MON-88 idProject PAYMENTS owner sofia.leon assignedTo pedro.salas dateCreated 2026-10-24 status Open details Alerta de tasa de error sobre 5 por ciento en el cobro.", "monitoreo", "alta"),
    ("idTicket MON-91 idProject ORDERS owner javier.nunez assignedTo tomas.ibanez dateCreated 2026-10-24 status InProgress details Disco del nodo de logs al 95 por ciento, se pierden eventos.", "monitoreo", "alta"),
    ("idTicket MON-74 idProject INVENTORY owner elena.ortiz assignedTo maria.paz dateCreated 2026-10-19 status Open details Latencia p95 del API de stock por encima del umbral acordado.", "monitoreo", "media"),
    ("idTicket MON-69 idProject BILLING owner diego.cruz assignedTo carmen.vega dateCreated 2026-10-16 status Blocked details El dashboard de SLA no recibe datos desde esta mañana.", "monitoreo", "media"),
    ("idTicket MON-41 idProject REPORTS owner luis.mora assignedTo sofia.leon dateCreated 2026-10-09 status Resolved details Alerta informativa de CPU en el worker de reportes, sin usuarios afectados.", "monitoreo", "baja"),
    ("idTicket MON-53 idProject SEARCH owner maria.paz assignedTo javier.nunez dateCreated 2026-10-11 status ToDo details La métrica de la cola muestra ruido intermitente, sin impacto.", "monitoreo", "baja"),
]
df = pd.DataFrame(MIS_CASOS, columns=["contexto", "categoria", "prioridad"])

if __name__ == "__main__":
    pd.set_option("display.max_rows", 40)
    pd.set_option("display.max_colwidth", 160)
    pd.set_option("display.width", 200)
    por_categoria = df.categoria.value_counts()
    por_prioridad = df.prioridad.value_counts()
    print(
        f"Casos: {len(df)} | "
        f"desarrollo: {int(por_categoria.get('desarrollo', 0))} | "
        f"despliegue: {int(por_categoria.get('despliegue', 0))} | "
        f"monitoreo: {int(por_categoria.get('monitoreo', 0))} | "
        f"alta: {int(por_prioridad.get('alta', 0))} | "
        f"media: {int(por_prioridad.get('media', 0))} | "
        f"baja: {int(por_prioridad.get('baja', 0))}"
    )
    print(df)
