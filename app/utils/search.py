from sqlalchemy import or_


def like_term(q: str | None) -> str | None:
    """Convierte el texto de búsqueda en un patrón para ILIKE.

    Devuelve None si no hay nada que buscar. Escapa % y _ para que se
    busquen como texto literal.
    """
    if q is None:
        return None
    q = q.strip()
    if not q:
        return None
    escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def ilike_any(pattern: str, *columns):
    return or_(*(column.ilike(pattern, escape="\\") for column in columns))
