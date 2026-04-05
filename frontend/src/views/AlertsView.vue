<template>
  <div class="h-full flex flex-col gap-6 relative pb-10">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tighter flex items-center gap-2">
          Central de Alertas
        </h1>
        <p class="text-[var(--text-muted)] font-medium">Histórico completo de anomalias e notificações do parque industrial.</p>
      </div>
    </div>

    <!-- Timeline / List (Skeleton Design for Next Phase) -->
    <div class="vintage-panel flex-1 p-6">
      <div class="flex items-center justify-between mb-8 border-b border-[var(--border-color)] pb-4">
        <h2 class="text-xl font-bold">Registro Geral</h2>
        <div class="flex gap-2">
           <button class="px-4 py-2 rounded-lg bg-[var(--bg-app)] border border-[var(--border-color)] text-sm font-bold text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors">Filtrar por Máquina</button>
           <button class="px-4 py-2 rounded-lg bg-[var(--bg-app)] border border-[var(--border-color)] text-sm font-bold text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors">Filtrar por Gravidade</button>
        </div>
      </div>

      <div class="flex flex-col items-center justify-center p-12 text-center text-[var(--text-muted)] mt-10">
         <div class="w-16 h-16 rounded-full bg-[var(--bg-app)] flex items-center justify-center mb-4">
            <Filter class="w-8 h-8 opacity-50" />
         </div>
         <p class="text-lg font-medium">Você será capaz de auditar os 245 alertas gerais aqui.</p>
         <p class="text-sm">Desenvolvimento estrutural desta listagem pendente (Fase 2).</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Filter } from 'lucide-vue-next'
</script>
