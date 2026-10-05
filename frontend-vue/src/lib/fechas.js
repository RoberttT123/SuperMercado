// Fechas en hora de Bolivia.
//
// Supabase guarda todo en UTC, pero algunas columnas lo devuelven sin zona
// horaria ("2026-10-05T21:00:00"). El navegador tomaría eso como hora local y
// lo mostraría 4 horas adelantado, así que aquí siempre se interpreta como UTC
// y se muestra en hora de Bolivia.
export const ZONA_BOLIVIA = 'America/La_Paz'

export const aFecha = (valor) => {
  if (!valor) return null
  if (valor instanceof Date) return isNaN(valor) ? null : valor
  let s = String(valor).trim().replace(' ', 'T')
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) s += 'T16:00:00Z' // solo fecha: mediodía de Bolivia, no cambia de día
  s = s.replace(/(\.\d{3})\d+/, '$1') // microsegundos -> milisegundos (Safari no lee 6 decimales)
  if (/[+-]\d{2}$/.test(s)) s += ':00' // "+00" -> "+00:00"
  else if (!/(Z|[+-]\d{2}:?\d{2})$/.test(s)) s += 'Z' // sin zona horaria: es UTC
  const d = new Date(s)
  return isNaN(d) ? null : d
}

const FORMATO_COMPLETO = { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }

export const formatoFechaHora = (valor, opciones = FORMATO_COMPLETO) => {
  const d = aFecha(valor)
  return d ? d.toLocaleString('es-BO', { timeZone: ZONA_BOLIVIA, ...opciones }) : '—'
}

// "YYYY-MM-DD" del día en Bolivia (por defecto, hoy). No usar toISOString():
// da el día en UTC, que después de las 20:00 de Bolivia ya es "mañana".
export const diaBolivia = (valor = new Date()) => {
  const d = aFecha(valor)
  if (!d) return ''
  return new Intl.DateTimeFormat('en-CA', { timeZone: ZONA_BOLIVIA, year: 'numeric', month: '2-digit', day: '2-digit' }).format(d)
}

// Días de calendario entre dos fechas "YYYY-MM-DD"
export const diasEntre = (desde, hasta) =>
  Math.round((Date.parse(`${hasta}T00:00:00Z`) - Date.parse(`${desde}T00:00:00Z`)) / 86400000)
