<template>
  <div class="h-full flex flex-col gap-6 pb-10">

    <!-- Page Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tighter flex items-center gap-3">
          <span class="p-2 rounded-xl bg-[var(--color-vintage-blue)]/10 border border-[var(--color-vintage-blue)]/20">
            <FileText class="w-6 h-6 text-[var(--color-vintage-blue)]" />
          </span>
          Central de Relatórios
        </h1>
        <p class="text-[var(--text-muted)] font-medium mt-1">
          Exporte dados operacionais em CSV, Excel ou PDF com um clique.
        </p>
      </div>

      <!-- Period Selector -->
      <div class="flex items-center gap-3 vintage-panel px-4 py-3 shrink-0">
        <CalendarDays class="w-4 h-4 text-[var(--color-vintage-blue)]" />
        <div class="flex items-center gap-2">
          <div class="flex flex-col">
            <label class="text-[9px] font-bold uppercase tracking-widest text-[var(--text-muted)]">De</label>
            <input
              type="date"
              v-model="dateFrom"
              class="bg-transparent text-sm font-bold text-[var(--text-main)] focus:outline-none cursor-pointer"
            />
          </div>
          <span class="text-[var(--text-muted)] font-bold">→</span>
          <div class="flex flex-col">
            <label class="text-[9px] font-bold uppercase tracking-widest text-[var(--text-muted)]">Até</label>
            <input
              type="date"
              v-model="dateTo"
              class="bg-transparent text-sm font-bold text-[var(--text-main)] focus:outline-none cursor-pointer"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Stats Bar -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div
        v-for="stat in quickStats"
        :key="stat.label"
        class="vintage-panel p-4 flex items-center gap-3"
      >
        <div class="p-2.5 rounded-xl shrink-0" :class="stat.bgClass">
          <component :is="stat.icon" class="w-5 h-5" :class="stat.iconClass" />
        </div>
        <div>
          <p class="text-[10px] font-bold uppercase tracking-widest text-[var(--text-muted)]">{{ stat.label }}</p>
          <p class="font-bold text-[var(--text-main)] text-lg leading-tight">{{ stat.value }}</p>
        </div>
      </div>
    </div>

    <!-- Report Cards Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

      <!-- Card: Falhas -->
      <div class="vintage-panel p-6 flex flex-col gap-5 hover:border-[var(--color-vintage-rose)]/50 transition-all group">
        <!-- Card Header -->
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-3">
            <div class="p-3 rounded-xl bg-[var(--color-vintage-rose)]/10 border border-[var(--color-vintage-rose)]/20 group-hover:scale-110 transition-transform">
              <AlertTriangle class="w-6 h-6 text-[var(--color-vintage-rose)]" />
            </div>
            <div>
              <h2 class="font-bold text-[var(--text-main)] text-lg leading-tight">Relatório de Falhas</h2>
              <p class="text-xs text-[var(--text-muted)] font-medium mt-0.5">
                Alertas disparados no período selecionado
              </p>
            </div>
          </div>
          <span class="px-2.5 py-1 text-[10px] uppercase tracking-wider font-bold rounded-full bg-[var(--color-vintage-rose)]/10 text-[var(--color-vintage-rose)] border border-[var(--color-vintage-rose)]/20">
            Alertas
          </span>
        </div>

        <!-- Divider -->
        <div class="border-t border-[var(--border-color)]"></div>

        <!-- Fields Preview -->
        <div class="flex flex-wrap gap-2">
          <span v-for="field in failureFields" :key="field" class="field-tag">{{ field }}</span>
        </div>

        <!-- Format Selection + Action -->
        <div class="flex items-center gap-3 mt-auto">
          <div class="flex-1 flex items-center gap-2 bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl p-1">
            <button
              v-for="fmt in formats"
              :key="fmt.value"
              @click="selectedFormat.failures = fmt.value"
              :class="[
                'flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs font-bold transition-all',
                selectedFormat.failures === fmt.value
                  ? 'bg-[var(--color-vintage-rose)] text-white shadow-sm'
                  : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'
              ]"
            >
              <component :is="fmt.icon" class="w-3.5 h-3.5" />
              {{ fmt.label }}
            </button>
          </div>
          <button
            @click="downloadReport('failures')"
            :disabled="loadingStates.failures"
            class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[var(--color-vintage-rose)] text-white font-bold text-sm shadow-md hover:-translate-y-0.5 active:translate-y-0 transition-all disabled:opacity-60 disabled:cursor-not-allowed disabled:translate-y-0"
          >
            <div v-if="loadingStates.failures" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <Download v-else class="w-4 h-4" />
            Baixar
          </button>
        </div>
      </div>

      <!-- Card: Desempenho -->
      <div class="vintage-panel p-6 flex flex-col gap-5 hover:border-[var(--color-vintage-mint)]/50 transition-all group">
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-3">
            <div class="p-3 rounded-xl bg-[var(--color-vintage-mint)]/10 border border-[var(--color-vintage-mint)]/20 group-hover:scale-110 transition-transform">
              <TrendingUp class="w-6 h-6 text-[var(--color-vintage-mint)]" />
            </div>
            <div>
              <h2 class="font-bold text-[var(--text-main)] text-lg leading-tight">Desempenho das Máquinas</h2>
              <p class="text-xs text-[var(--text-muted)] font-medium mt-0.5">
                Taxa de anomalia e total de alertas por máquina
              </p>
            </div>
          </div>
          <span class="px-2.5 py-1 text-[10px] uppercase tracking-wider font-bold rounded-full bg-[var(--color-vintage-mint)]/10 text-[var(--color-vintage-mint)] border border-[var(--color-vintage-mint)]/20">
            Máquinas
          </span>
        </div>
        <div class="border-t border-[var(--border-color)]"></div>
        <div class="flex flex-wrap gap-2">
          <span v-for="field in performanceFields" :key="field" class="field-tag">{{ field }}</span>
        </div>
        <div class="flex items-center gap-3 mt-auto">
          <div class="flex-1 flex items-center gap-2 bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl p-1">
            <button
              v-for="fmt in formats"
              :key="fmt.value"
              @click="selectedFormat.performance = fmt.value"
              :class="[
                'flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs font-bold transition-all',
                selectedFormat.performance === fmt.value
                  ? 'bg-[var(--color-vintage-mint)] text-white shadow-sm'
                  : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'
              ]"
            >
              <component :is="fmt.icon" class="w-3.5 h-3.5" />
              {{ fmt.label }}
            </button>
          </div>
          <button
            @click="downloadReport('performance')"
            :disabled="loadingStates.performance"
            class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[var(--color-vintage-mint)] text-white font-bold text-sm shadow-md hover:-translate-y-0.5 active:translate-y-0 transition-all disabled:opacity-60 disabled:cursor-not-allowed disabled:translate-y-0"
          >
            <div v-if="loadingStates.performance" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <Download v-else class="w-4 h-4" />
            Baixar
          </button>
        </div>
      </div>

      <!-- Card: Alertas -->
      <div class="vintage-panel p-6 flex flex-col gap-5 hover:border-[var(--color-vintage-mustard)]/50 transition-all group">
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-3">
            <div class="p-3 rounded-xl bg-[var(--color-vintage-mustard)]/10 border border-[var(--color-vintage-mustard)]/20 group-hover:scale-110 transition-transform">
              <Bell class="w-6 h-6 text-[var(--color-vintage-mustard)]" />
            </div>
            <div>
              <h2 class="font-bold text-[var(--text-main)] text-lg leading-tight">Central de Alertas</h2>
              <p class="text-xs text-[var(--text-muted)] font-medium mt-0.5">
                Alertas com tipo, risco, status e recomendação
              </p>
            </div>
          </div>
          <span class="px-2.5 py-1 text-[10px] uppercase tracking-wider font-bold rounded-full bg-[var(--color-vintage-mustard)]/10 text-[var(--color-vintage-mustard)] border border-[var(--color-vintage-mustard)]/20">
            Notificações
          </span>
        </div>

        <!-- Alert Filters -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-[9px] font-bold uppercase tracking-widest text-[var(--text-muted)] block mb-1">Nível de Risco</label>
            <select
              v-model="alertFilters.risk"
              class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-2 px-3 text-xs font-bold text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mustard)] transition-colors cursor-pointer"
            >
              <option value="">Todos os Riscos</option>
              <option value="HIGH">Alto Risco</option>
              <option value="MEDIUM">Risco Médio</option>
              <option value="LOW">Baixo Risco</option>
            </select>
          </div>
          <div>
            <label class="text-[9px] font-bold uppercase tracking-widest text-[var(--text-muted)] block mb-1">Status</label>
            <select
              v-model="alertFilters.status"
              class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-2 px-3 text-xs font-bold text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mustard)] transition-colors cursor-pointer"
            >
              <option value="">Todos os Status</option>
              <option value="OPEN">Abertos</option>
              <option value="RESOLVED">Resolvidos</option>
            </select>
          </div>
        </div>

        <div class="border-t border-[var(--border-color)]"></div>
        <div class="flex flex-wrap gap-2">
          <span v-for="field in alertFields" :key="field" class="field-tag">{{ field }}</span>
        </div>
        <div class="flex items-center gap-3 mt-auto">
          <div class="flex-1 flex items-center gap-2 bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl p-1">
            <button
              v-for="fmt in formats"
              :key="fmt.value"
              @click="selectedFormat.alerts = fmt.value"
              :class="[
                'flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs font-bold transition-all',
                selectedFormat.alerts === fmt.value
                  ? 'bg-[var(--color-vintage-mustard)] text-white shadow-sm'
                  : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'
              ]"
            >
              <component :is="fmt.icon" class="w-3.5 h-3.5" />
              {{ fmt.label }}
            </button>
          </div>
          <button
            @click="downloadReport('alerts')"
            :disabled="loadingStates.alerts"
            class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[var(--color-vintage-mustard)] text-white font-bold text-sm shadow-md hover:-translate-y-0.5 active:translate-y-0 transition-all disabled:opacity-60 disabled:cursor-not-allowed disabled:translate-y-0"
          >
            <div v-if="loadingStates.alerts" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <Download v-else class="w-4 h-4" />
            Baixar
          </button>
        </div>
      </div>

      <!-- Card: Exportação Genérica -->
      <div class="vintage-panel p-6 flex flex-col gap-5 hover:border-[var(--color-vintage-blue)]/50 transition-all group">
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-3">
            <div class="p-3 rounded-xl bg-[var(--color-vintage-blue)]/10 border border-[var(--color-vintage-blue)]/20 group-hover:scale-110 transition-transform">
              <Database class="w-6 h-6 text-[var(--color-vintage-blue)]" />
            </div>
            <div>
              <h2 class="font-bold text-[var(--text-main)] text-lg leading-tight">Exportação de Dados</h2>
              <p class="text-xs text-[var(--text-muted)] font-medium mt-0.5">
                Dump completo de qualquer entidade do sistema
              </p>
            </div>
          </div>
          <span class="px-2.5 py-1 text-[10px] uppercase tracking-wider font-bold rounded-full bg-[var(--color-vintage-blue)]/10 text-[var(--color-vintage-blue)] border border-[var(--color-vintage-blue)]/20">
            Exportar
          </span>
        </div>

        <!-- Entity Selector as styled cards -->
        <div class="grid grid-cols-2 gap-2">
          <button
            v-for="entity in entities"
            :key="entity.value"
            @click="selectedEntity = entity.value"
            :class="[
              'flex items-center gap-2.5 p-3 rounded-xl border text-left transition-all',
              selectedEntity === entity.value
                ? 'bg-[var(--color-vintage-blue)]/10 border-[var(--color-vintage-blue)]/40 text-[var(--text-main)]'
                : 'border-[var(--border-color)] text-[var(--text-muted)] hover:border-[var(--color-vintage-blue)]/30 hover:bg-[var(--bg-app)]'
            ]"
          >
            <component :is="entity.icon" class="w-4 h-4 shrink-0" :class="selectedEntity === entity.value ? 'text-[var(--color-vintage-blue)]' : ''" />
            <span class="text-xs font-bold">{{ entity.label }}</span>
          </button>
        </div>

        <div class="border-t border-[var(--border-color)]"></div>
        <div class="flex items-center gap-3 mt-auto">
          <div class="flex-1 flex items-center gap-2 bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl p-1">
            <button
              v-for="fmt in formatsWithCsv"
              :key="fmt.value"
              @click="selectedFormat.export = fmt.value"
              :class="[
                'flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs font-bold transition-all',
                selectedFormat.export === fmt.value
                  ? 'bg-[var(--color-vintage-blue)] text-white shadow-sm'
                  : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'
              ]"
            >
              <component :is="fmt.icon" class="w-3.5 h-3.5" />
              {{ fmt.label }}
            </button>
          </div>
          <button
            @click="downloadExport()"
            :disabled="loadingStates.export || !selectedEntity"
            class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[var(--color-vintage-blue)] text-white font-bold text-sm shadow-md hover:-translate-y-0.5 active:translate-y-0 transition-all disabled:opacity-60 disabled:cursor-not-allowed disabled:translate-y-0"
          >
            <div v-if="loadingStates.export" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <Download v-else class="w-4 h-4" />
            Exportar
          </button>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <Teleport to="body">
      <transition name="toast">
        <div
          v-if="toast.visible"
          class="fixed bottom-6 right-6 z-[200] flex items-center gap-3 px-5 py-4 rounded-2xl shadow-2xl border text-sm font-bold"
          :class="toast.success
            ? 'bg-[var(--bg-card)] border-[var(--color-vintage-mint)] text-[var(--color-vintage-mint)]'
            : 'bg-[var(--bg-card)] border-[var(--color-vintage-rose)] text-[var(--color-vintage-rose)]'"
        >
          <CheckCircle v-if="toast.success" class="w-5 h-5 shrink-0" />
          <XCircle v-else class="w-5 h-5 shrink-0" />
          {{ toast.message }}
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  FileText, CalendarDays, Download, AlertTriangle, TrendingUp, Bell,
  Database, Factory, Truck, Users, ShieldAlert,
  Table2, Sheet, FileType, CheckCircle, XCircle
} from 'lucide-vue-next'
import api from '@/services/api'

// ───────────────────────────── Date defaults ─────────────────────────────
const today = new Date()
const thirtyDaysAgo = new Date()
thirtyDaysAgo.setDate(today.getDate() - 30)

const fmt = (d) => d.toISOString().split('T')[0]
const dateFrom = ref(fmt(thirtyDaysAgo))
const dateTo   = ref(fmt(today))

// ───────────────────────────── Quick Stats ─────────────────────────────
const quickStats = [
  { label: 'Tipos de Relatório', value: '4', icon: FileText,    bgClass: 'bg-[var(--color-vintage-blue)]/10',    iconClass: 'text-[var(--color-vintage-blue)]'    },
  { label: 'Formatos Suportados', value: '3',  icon: Sheet,      bgClass: 'bg-[var(--color-vintage-mint)]/10',    iconClass: 'text-[var(--color-vintage-mint)]'    },
  { label: 'Fontes de Dados',   value: '4',   icon: Database,   bgClass: 'bg-[var(--color-vintage-mustard)]/10', iconClass: 'text-[var(--color-vintage-mustard)]' },
  { label: 'Download Direto',   value: '✓',   icon: Download,   bgClass: 'bg-[var(--color-vintage-rose)]/10',    iconClass: 'text-[var(--color-vintage-rose)]'    },
]

// ───────────────────────────── Format Options ─────────────────────────────
const formats = [
  { value: 'xlsx', label: 'XLSX', icon: Sheet     },
  { value: 'pdf',  label: 'PDF',  icon: FileType  },
]

const formatsWithCsv = [
  { value: 'csv',  label: 'CSV',  icon: Table2    },
  { value: 'xlsx', label: 'XLSX', icon: Sheet     },
  { value: 'pdf',  label: 'PDF',  icon: FileType  },
]

// ───────────────────────────── Field Tags ─────────────────────────────
const failureFields     = ['Máquina', 'Sensor', 'Título', 'Risco', 'Status', 'Criado em', 'Resolvido em']
const performanceFields = ['Máquina', 'Status', 'Localização', 'Total Alertas', 'Leituras', 'Taxa Anomalia (%)']
const alertFields       = ['Máquina', 'Tipo', 'Risco', 'Status', 'Título', 'Recomendação', 'Data']

// ───────────────────────────── Entity Options ─────────────────────────────
const entities = [
  { value: 'machines',  label: 'Máquinas',       icon: Factory    },
  { value: 'suppliers', label: 'Fornecedores',    icon: Truck      },
  { value: 'users',     label: 'Usuários',        icon: Users      },
  { value: 'audit',     label: 'Logs de Auditoria', icon: ShieldAlert },
]

// ───────────────────────────── State ─────────────────────────────
const selectedFormat = ref({
  failures:    'xlsx',
  performance: 'xlsx',
  alerts:      'xlsx',
  export:      'csv',
})

const alertFilters = ref({ risk: '', status: '' })
const selectedEntity = ref('machines')

const loadingStates = ref({
  failures: false, performance: false, alerts: false, export: false,
})

// ───────────────────────────── Toast ─────────────────────────────
const toast = ref({ visible: false, message: '', success: true })

const showToast = (message, success = true) => {
  toast.value = { visible: true, message, success }
  setTimeout(() => { toast.value.visible = false }, 3500)
}

// ───────────────────────────── Download Helpers ─────────────────────────────
const triggerBlobDownload = (data, filename, mimeType) => {
  const blob = new Blob([data], { type: mimeType })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const getMimeType = (format) => {
  const map = {
    csv:  'text/csv',
    xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    pdf:  'application/pdf',
  }
  return map[format] || 'application/octet-stream'
}

// ───────────────────────────── Report Downloads ─────────────────────────────
const downloadReport = async (type) => {
  loadingStates.value[type] = true
  try {
    const format = selectedFormat.value[type]
    const params = { output: format, start: dateFrom.value, end: dateTo.value }

    if (type === 'alerts') {
      if (alertFilters.value.risk)   params.risk   = alertFilters.value.risk
      if (alertFilters.value.status) params.status = alertFilters.value.status
    }

    const endpointMap = {
      failures:    '/reports/failures/',
      performance: '/reports/performance/',
      alerts:      '/reports/alerts/',
    }

    const response = await api.get(endpointMap[type], {
      params,
      responseType: 'blob',
    })

    const nameMap = {
      failures:    `relatorio_falhas.${format}`,
      performance: `relatorio_desempenho.${format}`,
      alerts:      `relatorio_alertas.${format}`,
    }

    triggerBlobDownload(response.data, nameMap[type], getMimeType(format))
    showToast(`Relatório exportado com sucesso!`, true)
  } catch (err) {
    console.error(`Error downloading ${type} report:`, err)
    showToast('Falha ao gerar relatório. Tente novamente.', false)
  } finally {
    loadingStates.value[type] = false
  }
}

const downloadExport = async () => {
  if (!selectedEntity.value) return
  loadingStates.value.export = true
  try {
    const format = selectedFormat.value.export
    const response = await api.post('/reports/export/', {
      entity: selectedEntity.value,
      output: format,
    }, { responseType: 'blob' })

    triggerBlobDownload(
      response.data,
      `export_${selectedEntity.value}.${format}`,
      getMimeType(format)
    )
    showToast(`Exportação concluída com sucesso!`, true)
  } catch (err) {
    console.error('Error exporting data:', err)
    showToast('Falha ao exportar dados. Tente novamente.', false)
  } finally {
    loadingStates.value.export = false
  }
}
</script>

<style scoped>
.field-tag {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  background: var(--bg-app);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  letter-spacing: 0.05em;
}

/* Toast animation */
.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.25s ease, transform 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(12px) scale(0.97);
}
</style>
