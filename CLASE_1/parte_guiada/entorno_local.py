from pathlib import Path

_RAIZ_REPO = Path(__file__).resolve().parents[2]
_ENV = _RAIZ_REPO / ".env"


def leer_clave(nombre):
    """Devuelve el valor de `nombre` leído desde el .env de la raíz del repositorio."""
    if not _ENV.is_file():
        raise SystemExit(
            f"No existe el archivo {_ENV}. "
            "Cópialo desde .env.sample y completa los valores."
        )

    for linea in _ENV.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        if clave.strip() != nombre:
            continue
        valor = valor.strip().strip('"').strip("'")
        if not valor:
            raise SystemExit(f"La variable {nombre} está vacía en {_ENV}.")
        return valor

    raise SystemExit(f"No existe la variable {nombre} en {_ENV}.")
