"""
Fechas y horas.

Supabase guarda todo en UTC (lo correcto), pero algunas columnas lo devuelven
sin zona horaria ("2026-10-05T21:00:00"). Además Render corre en UTC, así que
ahí date.today() cambia de día a las 20:00 de Bolivia.

Regla: lo que se guarda va en UTC; todo lo que depende de "qué día es" o que
ve una persona (filtros, dashboard, PDFs, Excel) se calcula en hora de Bolivia.
"""
import re
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional

ZONA_BOLIVIA = timezone(timedelta(hours=-4))  # Bolivia no usa horario de verano
DIAS_SEMANA = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


def ahora_bolivia() -> datetime:
    return datetime.now(ZONA_BOLIVIA)


def hoy_bolivia() -> date:
    return ahora_bolivia().date()


def a_bolivia(valor) -> Optional[datetime]:
    """Timestamp de Supabase -> datetime en hora de Bolivia.
    Sin zona horaria se asume UTC, que es como se guardó.
    Normaliza los decimales porque Python 3.10 solo acepta 3 o 6 dígitos."""
    if not valor:
        return None
    if isinstance(valor, datetime):
        dt = valor if valor.tzinfo else valor.replace(tzinfo=timezone.utc)
        return dt.astimezone(ZONA_BOLIVIA)
    m = re.match(r"^(\d{4}-\d{2}-\d{2})(?:[T ](\d{2}:\d{2}(?::\d{2})?)(\.\d+)?)?(Z|[+-]\d{2}(?::?\d{2})?)?$", str(valor).strip())
    if not m:
        return None
    dia, hora, frac, tz = m.groups()
    if hora is None:  # solo fecha: no hay hora que convertir
        return datetime.fromisoformat(dia).replace(hour=12, tzinfo=ZONA_BOLIVIA)
    if len(hora) == 5:
        hora += ":00"
    frac = ((frac or ".0")[1:] + "000000")[:6]
    if not tz or tz == "Z":
        tz = "+00:00"
    elif len(tz) == 3:
        tz += ":00"
    elif ":" not in tz:
        tz = f"{tz[:3]}:{tz[3:]}"
    return datetime.fromisoformat(f"{dia}T{hora}.{frac}{tz}").astimezone(ZONA_BOLIVIA)


def dia_bolivia(valor) -> Optional[date]:
    dt = a_bolivia(valor)
    return dt.date() if dt else None


def texto_fecha(valor, con_hora: bool = False) -> str:
    """'05/10/2026' o '05/10/2026 17:30' en hora de Bolivia (para PDFs)."""
    dt = a_bolivia(valor)
    if not dt:
        return "-"
    return dt.strftime("%d/%m/%Y %H:%M" if con_hora else "%d/%m/%Y")


def _como_fecha(valor) -> date:
    return valor if isinstance(valor, date) else date.fromisoformat(str(valor)[:10])


def _iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def limites_utc(inicio, fin) -> tuple:
    """Días completos en hora de Bolivia -> límites en UTC para filtrar en Supabase.
    Ej.: el 05/10 en Bolivia va de 05/10 04:00 UTC a 06/10 03:59:59.999999 UTC.
    Con la 'Z' sirve tanto para columnas con zona horaria como sin ella
    (Postgres ignora la zona en las columnas sin zona, que ya están en UTC)."""
    inicio, fin = _como_fecha(inicio), _como_fecha(fin)
    if fin < inicio:
        inicio, fin = fin, inicio
    desde = datetime.combine(inicio, time.min, ZONA_BOLIVIA)
    hasta = datetime.combine(fin + timedelta(days=1), time.min, ZONA_BOLIVIA) - timedelta(microseconds=1)
    return _iso_utc(desde), _iso_utc(hasta)


def etiqueta_dia(d: date) -> str:
    return f"{DIAS_SEMANA[d.weekday()]} {d.day:02d}"


def desde_utc(dia) -> str:
    """Inicio del día (hora de Bolivia) expresado en UTC, para .gte() en Supabase."""
    return limites_utc(dia, dia)[0]


def hasta_utc(dia) -> str:
    """Fin del día (hora de Bolivia) expresado en UTC, para .lte() en Supabase."""
    return limites_utc(dia, dia)[1]
