-- ═══════════════════════════════════════════════════════════════
-- HISTORIAL DE MOVIMIENTOS — Almacen Cori
-- ═══════════════════════════════════════════════════════════════
-- Bitácora de quién agregó productos, cambió precios o movió stock,
-- y cuándo. La llena el backend; solo el admin la consulta desde la app.
--
-- Correr UNA vez en el SQL Editor de Supabase antes de desplegar.
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.historial_movimientos (
  id              BIGSERIAL PRIMARY KEY,
  fecha           TIMESTAMPTZ NOT NULL DEFAULT now(),
  usuario         TEXT NOT NULL,          -- username de quien hizo el cambio
  rol             TEXT,                   -- admin / cajero / vendedor
  accion          TEXT NOT NULL,          -- producto_creado, precio_editado, stock_editado...
  modulo          TEXT NOT NULL,          -- inventario / compras / ventas
  producto_id     BIGINT,                 -- sin llave foránea a propósito: si el producto
  producto_nombre TEXT,                   -- se borra, el historial no debe perderse
  nivel           TEXT,                   -- caja, paquete, unidad...
  detalle         TEXT,                   -- texto legible: "Precio venta: Bs 7.00 → Bs 8.00"
  datos           JSONB                   -- antes/después estructurado
);

CREATE INDEX IF NOT EXISTS idx_historial_fecha   ON public.historial_movimientos (fecha DESC);
CREATE INDEX IF NOT EXISTS idx_historial_usuario ON public.historial_movimientos (usuario);
CREATE INDEX IF NOT EXISTS idx_historial_accion  ON public.historial_movimientos (accion);

-- RLS activado SIN políticas: nadie con la llave pública de la app puede
-- leer ni borrar el historial. El backend usa la llave service_role, que
-- no se ve afectada por RLS, así que sigue pudiendo escribir y consultar.
ALTER TABLE public.historial_movimientos ENABLE ROW LEVEL SECURITY;
