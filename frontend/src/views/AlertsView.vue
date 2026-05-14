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

    <!-- Timeline / List -->
    <div class="vintage-panel flex-1 p-6 flex flex-col">
      <div class="flex items-center justify-between mb-8 border-b border-[var(--border-color)] pb-4">
        <h2 class="text-xl font-bold">Registro Geral</h2>
        <div class="flex gap-2">
          <button @click="fetchNotifications" class="px-4 py-2 rounded-lg bg-[var(--bg-app)] border border-[var(--border-color)] text-sm font-bold text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors flex items-center gap-2">
            <RefreshCw class="w-4 h-4" /> Atualizar
          </button>
        </div>
      </div>

      <!-- Content -->
      <div v-if="loading" class="flex flex-col items-center justify-center flex-1 text-[var(--text-muted)]">
        <Loader2 class="w-8 h-8 animate-spin opacity-50 mb-4" />
        <p class="text-sm font-medium">Carregando notificações...</p>
      </div>

      <div v-else-if="notifications.length === 0" class="flex flex-col items-center justify-center flex-1 text-[var(--text-muted)]">
        <div class="w-16 h-16 rounded-full bg-[var(--bg-app)] flex items-center justify-center mb-4">
           <BellOff class="w-8 h-8 opacity-50" />
        </div>
        <p class="text-lg font-medium">Nenhuma notificação encontrada.</p>
        <p class="text-sm">Você está em dia com os seus alertas.</p>
      </div>

      <div v-else class="flex flex-col gap-4 overflow-y-auto pr-2">
        <div
          v-for="noty in notifications"
          :key="noty.id"
          class="border border-[var(--border-color)] p-4 rounded-xl flex gap-4 items-start bg-[var(--bg-card)] transition-colors"
          :class="!noty.is_read ? 'border-l-4 ' + getBorderColor(noty.notification_type) : ''"
        >
          <!-- Icon -->
          <div class="p-3 rounded-full shrink-0 mt-1" :class="getIconColors(noty.notification_type)">
            <AlertTriangle v-if="noty.notification_type === 'CRITICAL'" class="w-5 h-5" />
            <AlertCircle v-else-if="noty.notification_type === 'WARNING'" class="w-5 h-5" />
            <Info v-else class="w-5 h-5" />
          </div>
          
          <div class="flex-1 min-w-0">
            <div class="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-2">
              <h3 class="text-base sm:text-lg font-bold" :class="!noty.is_read ? 'text-[var(--text-main)]' : 'text-[var(--text-muted)]'">{{ noty.title }}</h3>
              <div class="flex items-center gap-2 shrink-0">
                <span class="text-[10px] sm:text-xs font-bold text-[var(--text-muted)] bg-[var(--bg-app)] px-2 py-1 rounded whitespace-nowrap">{{ new Date(noty.created_at).toLocaleString() }}</span>
                <button v-if="!noty.is_read" @click="handleMarkAsRead(noty)" class="p-1 px-2 rounded-lg bg-[var(--color-vintage-mint)]/10 text-[var(--color-vintage-mint)] hover:bg-[var(--color-vintage-mint)] hover:text-white transition-colors text-[10px] sm:text-xs font-bold flex items-center gap-1 shrink-0">
                  <Check class="w-3 h-3" />
                  Marcar Lida
                </button>
              </div>
            </div>
            <p class="text-sm mt-2 text-[var(--text-muted)] whitespace-pre-wrap">{{ noty.message }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { AlertTriangle, AlertCircle, Info, Check, RefreshCw, Loader2, BellOff } from 'lucide-vue-next'
import { getNotifications, markAsRead } from '@/services/notifications'

const notifications = ref([])
const loading = ref(true)

const fetchNotifications = async () => {
  loading.value = true
  try {
    const res = await getNotifications()
    notifications.value = res.data.results || res.data
  } catch (err) {
    console.error('Failed to fetch notifications', err)
  } finally {
    loading.value = false
  }
}

const handleMarkAsRead = async (noty) => {
  try {
    await markAsRead(noty.id)
    noty.is_read = true
    // Dispatch event to update the layout bubble counter
    window.dispatchEvent(new Event('refresh-notifications'))
  } catch (err) {
    console.error('Failed to mark as read', err)
  }
}

const getIconColors = (type) => {
  if (type === 'CRITICAL') return 'bg-[var(--color-vintage-rose)]/10 text-[var(--color-vintage-rose)]'
  if (type === 'WARNING') return 'bg-[var(--color-vintage-mustard)]/10 text-[var(--color-vintage-mustard)]'
  return 'bg-blue-500/10 text-blue-500'
}

const getBorderColor = (type) => {
  if (type === 'CRITICAL') return 'border-l-[var(--color-vintage-rose)]'
  if (type === 'WARNING') return 'border-l-[var(--color-vintage-mustard)]'
  return 'border-l-blue-500'
}

onMounted(() => {
  fetchNotifications()
  
  // Also refresh if the topbar marks something as read
  window.addEventListener('refresh-notifications', fetchNotifications)
})
</script>
