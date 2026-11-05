def consultar_stock_roto(sku: str) -> dict:
    """Devuelve nombre, unidades disponibles y bodega de un SKU."""
    #return RuntimeError("Inventario no disponible")
    raise RuntimeError("Inventario no disponible")


if __name__ == "__main__":
    print("Consultar stock para CAJ-050 (existe, stock 0)")
    print(consultar_stock_roto("CAJ-050"))
    print()

    print("Consultar stock para TAL-200 (existe)")
    print(consultar_stock_roto("TAL-200"))
    print()

    print("Consultar stock para XXX-999 (no existe)")
    print(consultar_stock_roto("XXX-999"))
    print()
