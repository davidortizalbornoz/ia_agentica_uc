import json
from pathlib import Path

# JSON de este ejercicio: rios, ciudades y puntos fluviales.
DATA = Path(__file__).resolve().parent / "data"


def _cargar(nombre: str) -> list | dict:
    """Lee una lista de registros desde ``data``. Si falla, devuelve ``{"error": ...}``."""
    try:
        with (DATA / nombre).open("r", encoding="utf-8") as f:
            registros = json.load(f)
    except Exception as e:
        return {"error": f"Error al leer {nombre}: {e}"}

    if not isinstance(registros, list):
        return {"error": f"{nombre} no contiene una lista de registros."}
    return registros


def _contiene(valor: str, criterio: str) -> bool:
    """Coincidencia parcial, sin distinguir mayúsculas ni espacios en los extremos."""
    return criterio.casefold() in str(valor).casefold()


def _ids_ciudad_por_nombre(nombre_ciudad: str) -> set[str] | dict:
    """Ids de ``ciudades.json`` cuyo ``nombre_ciudad`` contiene el criterio."""
    criterio = nombre_ciudad.strip()
    if not criterio:
        return set()

    ciudades = _cargar("ciudades.json")
    if isinstance(ciudades, dict):
        return ciudades

    return {
        ciudad["id_ciudad"]
        for ciudad in ciudades
        if _contiene(ciudad.get("nombre_ciudad", ""), criterio)
    }


def buscar_rios_por_ciudad(nombre_ciudad: str) -> list | dict:
    """Busca ríos asociados a una ciudad, con coincidencia parcial del nombre.

    ``rios.json`` no guarda el nombre de la ciudad: guarda ``id_ciudad``.
    Esta función busca en ``ciudades.json`` las ciudades cuyo
    ``nombre_ciudad`` contiene ``nombre_ciudad`` (sin distinguir mayúsculas
    y sin exigir el texto completo) y devuelve los ríos de esos ids.
    ``"tem"`` alcanza a Temuco y por lo tanto al río de ``TEM``.

    Un criterio vacío, o un nombre que no aparece en ninguna ciudad, devuelve
    una lista vacía. Un id de río sin ciudad en ``ciudades.json`` no sale por
    esta búsqueda.

    Args:
        nombre_ciudad: Texto a buscar dentro del nombre de la ciudad,
            por ejemplo ``"Temuco"`` o ``"ama"``.

    Returns:
        Una lista de ríos. Cada elemento tiene la forma::

            {
                "id_rio": "R4",
                "nombre_rio": "Rio Loa",
                "id_ciudad": "CAL"
            }

        Si no se puede leer alguno de los JSON, devuelve ``{"error": "..."}``.
    """
    ids = _ids_ciudad_por_nombre(nombre_ciudad)
    if isinstance(ids, dict):
        return ids
    if not ids:
        return []

    rios = _cargar("rios.json")
    if isinstance(rios, dict):
        return rios
    return [rio for rio in rios if rio.get("id_ciudad") in ids]


def buscar_rios_por_nombre(nombre_rio: str) -> list | dict:
    """Busca ríos cuyo nombre contiene el criterio, sin coincidencia exacta.

    Compara ``nombre_rio`` con el campo ``nombre_rio`` de ``rios.json``.
    No distingue mayúsculas y basta con que el criterio aparezca dentro del
    nombre: ``"loa"`` devuelve el Rio Loa y ``"rio"`` devuelve todos.

    Args:
        nombre_rio: Texto a buscar dentro del nombre del río,
            por ejemplo ``"Loa"`` o ``"pal"``.

    Returns:
        Una lista de ríos. Cada elemento tiene la forma::

            {
                "id_rio": "R4",
                "nombre_rio": "Rio Loa",
                "id_ciudad": "CAL"
            }

        Si el criterio viene vacío o ningún río coincide, la lista queda
        vacía. Si no se puede leer el JSON, devuelve ``{"error": "..."}``.
    """
    criterio = nombre_rio.strip()
    if not criterio:
        return []

    rios = _cargar("rios.json")
    if isinstance(rios, dict):
        return rios
    return [rio for rio in rios if _contiene(rio.get("nombre_rio", ""), criterio)]


def buscar_ciudad_por_id(id_ciudad: str) -> list | dict:
    """Busca una ciudad por su id, con coincidencia exacta.

    Compara ``id_ciudad`` con el campo ``id_ciudad`` de ``ciudades.json``.
    El id se normaliza a mayúsculas y sin espacios en los extremos, así
    ``"cal"`` encuentra ``CAL``. No es una búsqueda parcial: ``"CA"`` no
    alcanza a ``CAL``.

    Args:
        id_ciudad: Identificador de la ciudad, por ejemplo ``"CAL"``.

    Returns:
        Una lista de ciudades. Cada elemento tiene la forma::

            {
                "id_ciudad": "CAL",
                "nombre_region": "Antofagasta",
                "nombre_ciudad": "Calama",
                "habitantes": 75000,
                "superficie_km2": 160
            }

        Si el id no existe o viene vacío, la lista queda vacía. Si no se
        puede leer el JSON, devuelve ``{"error": "..."}``.
    """
    criterio = id_ciudad.strip().upper()
    if not criterio:
        return []

    ciudades = _cargar("ciudades.json")
    if isinstance(ciudades, dict):
        return ciudades
    return [ciudad for ciudad in ciudades if ciudad.get("id_ciudad", "").strip().upper() == criterio]


def buscar_ciudad_por_region(nombre_region: str) -> list | dict:
    """Busca ciudades cuya región contiene el criterio, sin coincidencia exacta.

    Compara ``nombre_region`` con el campo ``nombre_region`` de
    ``ciudades.json``. No distingue mayúsculas y basta con una parte del
    nombre: ``"Los"`` devuelve las ciudades de Los Rios y de Los Lagos.

    Args:
        nombre_region: Texto a buscar dentro del nombre de la región,
            por ejemplo ``"Araucania"`` o ``"lagos"``.

    Returns:
        Una lista de ciudades. Cada elemento tiene la forma::

            {
                "id_ciudad": "CAL",
                "nombre_region": "Antofagasta",
                "nombre_ciudad": "Calama",
                "habitantes": 75000,
                "superficie_km2": 160
            }

        Si el criterio viene vacío o ninguna región coincide, la lista queda
        vacía. Si no se puede leer el JSON, devuelve ``{"error": "..."}``.
    """
    criterio = nombre_region.strip()
    if not criterio:
        return []

    ciudades = _cargar("ciudades.json")
    if isinstance(ciudades, dict):
        return ciudades
    return [
        ciudad
        for ciudad in ciudades
        if _contiene(ciudad.get("nombre_region", ""), criterio)
    ]


def buscar_ciudad_por_nombre(nombre_ciudad: str) -> list | dict:
    """Busca ciudades cuyo nombre contiene el criterio, sin coincidencia exacta.

    Compara ``nombre_ciudad`` con el campo ``nombre_ciudad`` de
    ``ciudades.json``. No distingue mayúsculas y basta con una parte del
    nombre: ``"varas"`` devuelve Puerto Varas y ``"ama"`` devuelve Calama.

    Args:
        nombre_ciudad: Texto a buscar dentro del nombre de la ciudad,
            por ejemplo ``"Calama"`` o ``"tem"``.

    Returns:
        Una lista de ciudades. Cada elemento tiene la forma::

            {
                "id_ciudad": "CAL",
                "nombre_region": "Antofagasta",
                "nombre_ciudad": "Calama",
                "habitantes": 75000,
                "superficie_km2": 160
            }

        Si el criterio viene vacío o ninguna ciudad coincide, la lista queda
        vacía. Si no se puede leer el JSON, devuelve ``{"error": "..."}``.
    """
    criterio = nombre_ciudad.strip()
    if not criterio:
        return []

    ciudades = _cargar("ciudades.json")
    if isinstance(ciudades, dict):
        return ciudades
    return [
        ciudad
        for ciudad in ciudades
        if _contiene(ciudad.get("nombre_ciudad", ""), criterio)
    ]


def buscar_punto_por_id(id_punto: str) -> list | dict:
    """Busca un punto fluvial por su id, con coincidencia exacta.

    Compara ``id_punto`` con el campo ``id_punto`` de
    ``puntos_fluviales.json``. El id se normaliza a mayúsculas y sin
    espacios en los extremos, así ``"p5"`` encuentra ``P5``. No es una
    búsqueda parcial: ``"P"`` no devuelve todos los puntos.

    Args:
        id_punto: Identificador del punto, por ejemplo ``"P5"``.

    Returns:
        Una lista de puntos fluviales. Cada elemento tiene la forma::

            {
                "id_punto": "P5",
                "id_ciudad": "SAN",
                "mm_acumulados_promedio": 0.2
            }

        Si el id no existe o viene vacío, la lista queda vacía. Si no se
        puede leer el JSON, devuelve ``{"error": "..."}``.
    """
    criterio = id_punto.strip().upper()
    if not criterio:
        return []

    puntos = _cargar("puntos_fluviales.json")
    if isinstance(puntos, dict):
        return puntos
    return [punto for punto in puntos if punto.get("id_punto", "").strip().upper() == criterio]


def buscar_punto_por_ciudad(nombre_ciudad: str) -> list | dict:
    """Busca puntos fluviales de una ciudad, con coincidencia parcial del nombre.

    ``puntos_fluviales.json`` no guarda el nombre de la ciudad: guarda
    ``id_ciudad``. Esta función busca en ``ciudades.json`` las ciudades cuyo
    ``nombre_ciudad`` contiene ``nombre_ciudad`` y devuelve los puntos de
    esos ids. ``"cala"`` alcanza a Calama y por lo tanto al punto de ``CAL``.

    Un criterio vacío, o un nombre que no aparece en ninguna ciudad, devuelve
    una lista vacía. Un punto cuyo ``id_ciudad`` no está en ``ciudades.json``
    (por ejemplo ``SAN``) no sale por el nombre de la ciudad.

    Args:
        nombre_ciudad: Texto a buscar dentro del nombre de la ciudad,
            por ejemplo ``"Valdivia"`` o ``"varas"``.

    Returns:
        Una lista de puntos fluviales. Cada elemento tiene la forma::

            {
                "id_punto": "P5",
                "id_ciudad": "SAN",
                "mm_acumulados_promedio": 0.2
            }

        Si no se puede leer alguno de los JSON, devuelve ``{"error": "..."}``.
    """
    ids = _ids_ciudad_por_nombre(nombre_ciudad)
    if isinstance(ids, dict):
        return ids
    if not ids:
        return []

    puntos = _cargar("puntos_fluviales.json")
    if isinstance(puntos, dict):
        return puntos
    return [punto for punto in puntos if punto.get("id_ciudad") in ids]


if __name__ == "__main__":
    print("Ríos de una ciudad cuyo nombre contiene 'tem' (Temuco)")
    print(buscar_rios_por_ciudad("tem"))
    print()

    print("Ríos cuyo nombre contiene 'loa'")
    print(buscar_rios_por_nombre("loa"))
    print()

    print("Ciudad con id CAL")
    print(buscar_ciudad_por_id("cal"))
    print()

    print("Ciudades cuya región contiene 'Los'")
    print(buscar_ciudad_por_region("Los"))
    print()

    print("Ciudades cuyo nombre contiene 'varas'")
    print(buscar_ciudad_por_nombre("varas"))
    print()

    print("Punto fluvial P5")
    print(buscar_punto_por_id("p5"))
    print()

    print("Puntos fluviales de una ciudad cuyo nombre contiene 'cala'")
    print(buscar_punto_por_ciudad("cala"))
    print()
