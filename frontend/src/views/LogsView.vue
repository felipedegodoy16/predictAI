<template>
  <div class="h-full flex flex-col">
    <!-- Header Estilo PredictAI -->
    <div class="px-6 py-6 pb-8 border-b border-[var(--border-color)] bg-transparent">
      <!-- Title Section -->
      <div class="mb-6 flex flex-col items-start">
        <h1 class="text-3xl font-bold tracking-tighter flex items-center gap-2 text-[var(--text-main)]">
          Logs de Auditoria
        </h1>
        <p class="text-sm text-[var(--text-muted)] font-medium mt-1">Monitore, pesquise e rastreie o histórico operacional de todas as atividades administrativas do sistema.</p>
      </div>

      <!-- Filters & Search Container - Flex Col to keep filters below search -->
      <div class="flex flex-col gap-5 w-full">
        
        <!-- Search Input (Exactly like MachineView) -->
        <div class="flex-1 w-full relative">
          <label for="search" class="sr-only">Pesquisar</label>
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search class="w-5 h-5 text-[var(--text-muted)]" />
          </div>
          <input 
            id="search"
            v-model="searchQuery"
            type="text" 
            placeholder="Pesquisar por autor, entidade ou descrição..." 
            class="w-full pl-10 pr-10 py-2.5 bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl text-sm focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors text-[var(--text-main)] font-medium shadow-sm"
          />
          <button 
            v-if="searchQuery" 
            @click="searchQuery = ''"
            class="absolute inset-y-0 cursor-pointer right-0 pr-3 flex items-center text-[var(--text-muted)] hover:text-[var(--text-main)]"
          >
            <X class="w-4 h-4 ml-2" />
          </button>
        </div>

        <!-- Filters Container (below search) -->
        <div class="flex items-center gap-3 overflow-x-auto scroller max-w-full pb-1">
          <button 
            @click="filterAction = ''"
            class="flex items-center justify-center border text-sm font-semibold rounded-xl px-4 py-2.5 transition-colors shrink-0 shadow-sm"
            :class="filterAction === '' ? 'bg-[var(--text-main)] border-[var(--text-main)] text-[var(--bg-app)]' : 'bg-[var(--bg-app)] text-[var(--text-main)] border-[var(--border-color)] hover:border-[var(--text-muted)]'"
          >
            Todas as Ações
          </button>
          
          <button 
            @click="filterAction = 'CREATE'"
            class="flex items-center gap-2 border text-sm font-semibold rounded-xl px-4 py-2.5 transition-colors shrink-0 shadow-sm"
            :class="filterAction === 'CREATE' ? 'bg-[var(--bg-app)] border-[var(--color-vintage-mint)] text-[var(--color-vintage-mint)]' : 'bg-[var(--bg-app)] text-[var(--text-main)] border-[var(--border-color)] hover:border-[var(--color-vintage-mint)]'"
          >
            <div class="w-2 h-2 rounded-full" :class="filterAction === 'CREATE' ? 'bg-[var(--color-vintage-mint)]' : 'bg-[var(--color-vintage-mint)] opacity-70'"></div>
            Criação
          </button>
          
          <button 
            @click="filterAction = 'UPDATE'"
            class="flex items-center gap-2 border text-sm font-semibold rounded-xl px-4 py-2.5 transition-colors shrink-0 shadow-sm"
            :class="filterAction === 'UPDATE' ? 'bg-[var(--bg-app)] border-[var(--color-vintage-blue)] text-[var(--color-vintage-blue)]' : 'bg-[var(--bg-app)] text-[var(--text-main)] border-[var(--border-color)] hover:border-[var(--color-vintage-blue)]'"
          >
            <div class="w-2 h-2 rounded-full" :class="filterAction === 'UPDATE' ? 'bg-[var(--color-vintage-blue)]' : 'bg-[var(--color-vintage-blue)] opacity-70'"></div>
            Atualização
          </button>
          
          <button 
            @click="filterAction = 'DELETE'"
            class="flex items-center gap-2 border text-sm font-semibold rounded-xl px-4 py-2.5 transition-colors shrink-0 shadow-sm"
            :class="filterAction === 'DELETE' ? 'bg-[var(--bg-app)] border-[var(--color-vintage-rose)] text-[var(--color-vintage-rose)]' : 'bg-[var(--bg-app)] text-[var(--text-main)] border-[var(--border-color)] hover:border-[var(--color-vintage-rose)]'"
          >
            <div class="w-2 h-2 rounded-full" :class="filterAction === 'DELETE' ? 'bg-[var(--color-vintage-rose)]' : 'bg-[var(--color-vintage-rose)] opacity-70'"></div>
            Remoção
          </button>
        </div>

      </div>
    </div>

    <!-- Status Messages -->
    <div v-if="loading" class="p-8 text-center text-[var(--text-muted)] flex flex-col items-center">
      <Loader2 class="w-8 h-8 animate-spin mb-4 text-[var(--color-vintage-mint)]" />
      <p class="font-medium">Carregando logs...</p>
    </div>

    <div v-else-if="error" class="m-6 p-4 bg-[var(--color-vintage-rose)]/10 text-[var(--color-vintage-rose)] rounded-xl border border-[var(--color-vintage-rose)]/20 flex items-center gap-3">
      <AlertTriangle class="w-5 h-5 shrink-0" />
      <div>
        <p class="text-sm font-bold">Erro ao carregar auditoria</p>
        <p class="text-xs opacity-90">{{ error }}</p>
      </div>
      <button @click="fetchLogs" class="ml-auto px-3 py-1 text-xs font-bold bg-[var(--bg-card)]/50 hover:bg-[var(--bg-card)] rounded-lg border border-[var(--color-vintage-rose)]/20 transition-colors">
        Tentar Novamente
      </button>
    </div>

    <div v-else-if="filteredLogs.length === 0" class="flex-1 flex flex-col items-center justify-center p-8 text-[var(--text-muted)]">
      <div class="w-16 h-16 bg-[var(--bg-card)] rounded-2xl flex items-center justify-center mb-4 border border-[var(--border-color)] shadow-sm">
        <ShieldAlert class="w-8 h-8 opacity-50" />
      </div>
      <p class="font-bold text-lg mb-1">Nenhum log encontrado</p>
      <p class="text-sm">Tente ajustar seus termos de busca ou filtros.</p>
      <button v-if="searchQuery || filterAction" @click="searchQuery = ''; filterAction = ''" class="mt-4 px-4 py-2 bg-[var(--bg-card)] hover:bg-[var(--border-color)] text-sm font-medium rounded-lg transition-colors border border-[var(--border-color)]">
        Limpar Filtros
      </button>
    </div>

    <!-- Content Table -->
    <div v-else class="flex-1 overflow-auto p-6">
      <div class="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl shadow-sm overflow-hidden hidden md:block">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-[var(--border-color)] bg-[var(--bg-app)]/50">
              <th class="px-6 py-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Data / Hora</th>
              <th class="px-6 py-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Ação</th>
              <th class="px-6 py-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Autor</th>
              <th class="px-6 py-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Contexto</th>
              <th class="px-6 py-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Descrição Detalhada</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[var(--border-color)]">
            <tr v-for="log in filteredLogs" :key="log.id" class="hover:bg-[var(--bg-app)]/50 transition-colors group">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <Clock class="w-4 h-4 text-[var(--text-muted)]" />
                  <div>
                    <div class="text-sm font-medium">{{ formatDate(log.timestamp) }}</div>
                    <div class="text-xs text-[var(--text-muted)]">{{ formatTime(log.timestamp) }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-bold border" :class="getActionClass(log.action)">
                  {{ getActionLabel(log.action) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-full bg-[var(--color-vintage-mint)]/10 flex items-center justify-center border border-[var(--color-vintage-mint)]/20">
                    <User class="w-4 h-4 text-[var(--color-vintage-mint)]" />
                  </div>
                  <div class="text-sm font-semibold truncate max-w-[150px]" :title="log.user_email">
                    {{ log.user_name || log.user_email }}
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm font-medium px-2.5 py-1 bg-[var(--bg-app)] border border-[var(--border-color)] rounded-md list-none">
                  {{ log.entity_type }} <span class="text-[var(--text-muted)] opacity-50 ml-1">#{{ log.entity_id?.substring(0,6) }}</span>
                </span>
              </td>
              <td class="px-6 py-4">
                <p class="text-sm text-[var(--text-muted)] line-clamp-2" :title="log.description">{{ log.description }}</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile List View -->
      <div class="md:hidden space-y-4">
        <div v-for="log in filteredLogs" :key="log.id" class="p-4 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl shadow-sm">
          <div class="flex justify-between items-start mb-3">
            <div>
              <span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-bold border mb-2" :class="getActionClass(log.action)">
                {{ getActionLabel(log.action) }}
              </span>
              <div class="flex items-center gap-1.5 text-xs text-[var(--text-muted)] font-medium">
                <Clock class="w-3.5 h-3.5" />
                {{ formatDate(log.timestamp) }} às {{ formatTime(log.timestamp) }}
              </div>
            </div>
            <span class="text-xs font-bold px-2 py-1 bg-[var(--bg-app)] border border-[var(--border-color)] rounded-md">
              {{ log.entity_type }}
            </span>
          </div>
          
          <div class="bg-[var(--bg-app)]/50 p-3 rounded-xl border border-[var(--border-color)] mb-3">
            <p class="text-sm font-medium leading-relaxed">{{ log.description }}</p>
          </div>
          
          <div class="flex items-center gap-2 pt-3 border-t border-[var(--border-color)]">
            <div class="w-6 h-6 rounded-full bg-[var(--color-vintage-mint)]/10 flex items-center justify-center border border-[var(--color-vintage-mint)]/20 shrink-0">
              <User class="w-3 h-3 text-[var(--color-vintage-mint)]" />
            </div>
            <p class="text-xs font-medium text-[var(--text-muted)] truncate">{{ log.user_name || log.user_email }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ShieldAlert, Search, Loader2, AlertTriangle, Clock, User } from 'lucide-vue-next'
import api from '@/services/api'

const logs = ref([])
const loading = ref(false)
const error = ref('')

const searchQuery = ref('')
const filterAction = ref('')

const fetchLogs = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await api.get('audit/')
    logs.value = res.data.results || res.data // Trata tanto paginação local quanto direta
  } catch (err) {
    console.error('Erro ao buscar logs:', err)
    error.value = 'Não foi possível carregar os registros de auditoria.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLogs()
})

const filteredLogs = computed(() => {
  let result = logs.value

  if (filterAction.value) {
    result = result.filter(log => log.action === filterAction.value)
  }

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(log => 
      (log.description && log.description.toLowerCase().includes(q)) ||
      (log.user_name && log.user_name.toLowerCase().includes(q)) ||
      (log.user_email && log.user_email.toLowerCase().includes(q)) ||
      (log.entity_type && log.entity_type.toLowerCase().includes(q))
    )
  }

  return result
})

const getActionLabel = (action) => {
  const map = {
    'CREATE': 'Criação',
    'UPDATE': 'Atualização',
    'DELETE': 'Remoção',
    'LOGIN': 'Login'
  }
  return map[action] || action
}

const getActionClass = (action) => {
  const map = {
    'CREATE': 'bg-[var(--color-vintage-mustard)]/10 text-[var(--color-vintage-mustard)] border-[var(--color-vintage-mustard)]/20',
    'UPDATE': 'bg-blue-500/10 text-blue-500 border-blue-500/20',
    'DELETE': 'bg-[var(--color-vintage-rose)]/10 text-[var(--color-vintage-rose)] border-[var(--color-vintage-rose)]/20',
    'LOGIN': 'bg-[var(--color-vintage-mint)]/10 text-[var(--color-vintage-mint)] border-[var(--color-vintage-mint)]/20',
  }
  return map[action] || 'bg-gray-500/10 text-gray-500 border-gray-500/20'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('pt-BR')
}

const formatTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.scroller::-webkit-scrollbar {
  height: 4px;
}
.scroller::-webkit-scrollbar-track {
  background: transparent;
}
.scroller::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}
</style>
