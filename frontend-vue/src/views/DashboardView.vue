<template>
  <div class="p-8 pl-10">
    
    <!-- 1. HERO BANNER -->
    <header class="bg-white rounded-2xl border-l-[6px] border-[#FF6B2B] p-8 mb-10 shadow-sm flex items-center gap-6">
      <div class="w-20 h-20 bg-[#FFF3EE] rounded-full flex items-center justify-center text-4xl border border-[#FFCCB3]">
        🛒
      </div>
      <div>
        <span class="inline-block bg-[#FFF3EE] text-[#E85510] px-3 py-1 rounded-full text-xs font-black tracking-widest uppercase border border-[#FFCCB3] mb-2">
          Sistema de Gestión Comercial
        </span>
        <h1 class="text-4xl font-black text-[#2A1A0A]">Almacen <span class="text-[#FF6B2B]">Gloria</span></h1>
        <p class="text-gray-500 italic mt-1">Precio, calidad y confianza.</p>
      </div>
    </header>

    <!-- 2. GRID DE MÓDULOS -->
    <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      
      <!-- Control de Caja -->
      <article class="app-card">
        <h3 class="text-xl font-bold text-[#2A1A0A] mb-3">💵 Control de Caja</h3>
        <p class="text-sm text-gray-600 mb-6 leading-relaxed">
          Abre y cierra la caja del día. Realiza el arqueo y consulta el historial histórico.
        </p>
        <router-link to="/caja" class="btn-primary">Ir a Caja</router-link>
      </article>

      <!-- Inventario -->
      <article class="app-card">
        <h3 class="text-xl font-bold text-[#2A1A0A] mb-3">📦 Inventario</h3>
        <p class="text-sm text-gray-600 mb-6 leading-relaxed">
          Registra productos, actualiza precios y gestiona el stock disponible con el lector.
        </p>
        <router-link to="/inventario" class="btn-primary">Ir a Inventario</router-link>
      </article>

      <!-- Punto de Venta -->
      <article class="app-card">
        <h3 class="text-xl font-bold text-[#2A1A0A] mb-3">🛒 Punto de Venta</h3>
        <p class="text-sm text-gray-600 mb-6 leading-relaxed">
          Escanea códigos de barra, procesa ventas y cobra de forma rápida y sencilla.
        </p>
        <router-link to="/pos" class="btn-primary">Ir a POS</router-link>
      </article>

      <!-- Reportes -->
      <article class="app-card">
        <h3 class="text-xl font-bold text-[#2A1A0A] mb-3">📊 Reportes</h3>
        <p class="text-sm text-gray-600 mb-6 leading-relaxed">
          Consulta gráficos de ventas, utilidades netas y los artículos más vendidos del mes.
        </p>
        <router-link to="/reportes" class="btn-primary">Ir a Reportes</router-link>
      </article>

    </section>

    <!-- 3. FOOTER -->
    <footer class="mt-16 pt-8 border-t border-[#FFE0CC] text-center text-gray-400 text-sm">
      <p>Panel Central de Administración - Almacen Gloria · Beni, Bolivia</p>
    </footer>

  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/authStore';

const authStore = useAuthStore();</script>