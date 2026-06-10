<template>
  <div class="h-full flex flex-col gap-6 relative pb-10">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tighter flex items-center gap-2">
          Ordens de Serviço (Kanban)
        </h1>
        <p class="text-[var(--text-muted)] font-medium">Arraste os cartões para atualizar o status em tempo real.</p>
      </div>
      
      <button 
        v-if="canCreate"
        @click="openCreateModal"
        class="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[var(--color-vintage-mint)] text-white font-bold shadow-md hover:-translate-y-0.5 transition-transform"
      >
        <Plus class="w-5 h-5" />
        Nova OS
      </button>
    </div>

    <!-- Toolbar Filters -->
    <div class="flex flex-col md:flex-row gap-4 items-center justify-between">
      <div class="flex items-center gap-3 flex-wrap">
        <!-- Filtro de visão -->
        <div class="flex items-center bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl px-2 shadow-sm">
          <Filter class="w-4 h-4 text-[var(--text-muted)] ml-2 shrink-0" />
          <select 
            v-model="myTasksFilter" 
            class="bg-transparent border-none focus:outline-none py-2.5 px-3 text-sm font-bold text-[var(--text-main)] cursor-pointer"
          >
            <option :value="false">Todas as OS visíveis</option>
            <option :value="true">Abertas por mim</option>
            <option value="assigned">Atribuídas a mim</option>
          </select>
        </div>

        <!-- Filtro de Dias -->
        <div class="flex items-center bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl px-2 shadow-sm">
          <CalendarDays class="w-4 h-4 text-[var(--text-muted)] ml-2 shrink-0" />
          <select 
            v-model="daysFilter" 
            @change="fetchData"
            class="bg-transparent border-none focus:outline-none py-2.5 px-3 text-sm font-bold text-[var(--text-main)] cursor-pointer"
          >
            <option :value="7">Últimos 7 dias</option>
            <option :value="15">Últimos 15 dias</option>
            <option :value="30">Últimos 30 dias</option>
            <option :value="90">Últimos 90 dias</option>
            <option :value="''">Todas as datas</option>
          </select>
        </div>

        <!-- Info de visibilidade para técnicos -->
        <div 
          v-if="authStore.isTechnician"
          class="flex items-center gap-1.5 text-xs font-bold text-[var(--text-muted)] bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl px-3 py-2"
        >
          <EyeOff class="w-3.5 h-3.5" />
          Exibindo apenas suas OS
        </div>
      </div>
    </div>

    <!-- Kanban Board -->
    <div class="flex-1 flex gap-6 overflow-x-auto overflow-y-hidden pb-4 kanban-scrollbar">
      <!-- Loading Overlay -->
      <div v-if="loading" class="absolute inset-0 z-10 bg-[var(--bg-card)]/50 backdrop-blur-sm flex items-center justify-center">
         <div class="w-10 h-10 border-4 border-[var(--color-vintage-mint)] border-t-transparent rounded-full animate-spin"></div>
      </div>

      <!-- Columns -->
      <div 
        v-for="col in columns" 
        :key="col.id"
        class="kanban-column flex-shrink-0 w-80 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl flex flex-col overflow-hidden shadow-sm"
        :class="{ 'drag-over': dragOverColumn === col.id }"
        @dragenter.prevent
        @dragover.prevent="onDragOver($event, col.id)"
        @dragleave.self="dragOverColumn = null"
        @drop.prevent="onDrop($event, col.id)"
      >
        <!-- Column Header -->
        <div class="p-4 border-b border-[var(--border-color)] bg-[var(--bg-app)]/50 flex justify-between items-center">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full" :class="colColor(col)"></span>
            <h3 class="font-bold text-[var(--text-main)] tracking-tight">{{ col.name }}</h3>
          </div>
          <span class="text-xs font-bold bg-[var(--text-main)]/10 text-[var(--text-main)] px-2 py-0.5 rounded-full">
            {{ getOrdersForColumn(col.id).length }}
          </span>
        </div>

        <!-- Column Body -->
        <div class="flex-1 overflow-y-auto p-3 space-y-3 card-scrollbar">
          <!-- Empty State -->
          <div v-if="getOrdersForColumn(col.id).length === 0" class="h-full min-h-[80px] flex items-center justify-center text-center text-xs font-medium text-[var(--text-muted)] p-4 border-2 border-dashed border-[var(--border-color)] rounded-xl opacity-50">
            Nenhuma OS aqui
          </div>

          <!-- Kanban Card -->
          <div 
            v-for="wo in getOrdersForColumn(col.id)" 
            :key="wo.id"
            :draggable="!authStore.isViewer"
            @dragstart="onDragStart($event, wo)"
            @dragend="onDragEnd"
            @dragenter.prevent
            @dragover.prevent
            @click="onCardClick(wo)"
            class="kanban-card bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl p-3 shadow-sm hover:border-[var(--color-vintage-mint)] hover:shadow-md transition-all group relative"
            :class="!authStore.isViewer ? 'cursor-grab active:cursor-grabbing' : 'cursor-pointer'"
          >
            <div class="flex justify-between items-start mb-2">
              <!-- Priority badge -->
              <span class="px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider rounded border"
                :class="priorityClass(wo.priority)"
              >
                {{ priorityLabel(wo.priority) }}
              </span>

              <!-- Edit button -->
              <button 
                v-if="canEdit(wo)"
                @click.stop="openEditModal(wo)" 
                class="opacity-0 group-hover:opacity-100 p-1 rounded-md text-[var(--text-muted)] hover:text-[var(--color-vintage-mint)] hover:bg-[var(--color-vintage-mint)]/10 transition-all"
                title="Editar OS"
              >
                <Edit3 class="w-4 h-4" />
              </button>
            </div>

            <!-- OS ID + Type -->
            <h4 class="font-bold text-sm text-[var(--text-main)] mb-1 leading-snug">
              OS-{{ wo.id }}
              <span class="font-normal text-[var(--text-muted)]">· {{ wo.order_type_display || wo.order_type }}</span>
            </h4>

            <!-- Machine -->
            <p class="text-[11px] text-[var(--text-muted)] font-medium mb-1 flex items-center gap-1">
              <Activity class="w-3 h-3 shrink-0" />
              {{ machineName(wo.machine_detail) }}
            </p>

            <!-- Observation snippet — compacto, sem expandir o card -->
            <p v-if="wo.observation" class="text-[10px] text-[var(--text-muted)] mb-2 line-clamp-2 italic leading-snug overflow-hidden">
              {{ wo.observation }}
            </p>

            <!-- Footer -->
            <div class="flex items-center justify-between text-[10px] text-[var(--text-muted)] pt-2 border-t border-[var(--border-color)]">
              <span class="font-bold uppercase flex items-center gap-1">
                <CalendarDays class="w-3 h-3" />
                {{ formatDate(wo.opening_date) }}
              </span>
              <!-- Técnico atribuído -->
              <span v-if="wo.assigned_to_detail" class="flex items-center gap-1 font-bold text-[var(--color-vintage-mint)] truncate max-w-[100px]" :title="wo.assigned_to_detail.name">
                <UserCheck class="w-3 h-3 shrink-0" />
                {{ firstName(wo.assigned_to_detail.name) }}
              </span>
              <span v-else class="flex items-center gap-1 text-[var(--text-muted)]/60 italic">
                <User class="w-3 h-3" />
                Não atribuído
              </span>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- CREATE / EDIT MODAL -->
    <Teleport to="body">
      <div v-if="showEditModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="closeEditModal"></div>
        
        <div class="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-3xl w-full max-w-2xl max-h-[90vh] flex flex-col relative z-[101] shadow-2xl overflow-hidden">
          
          <div class="p-6 border-b border-[var(--border-color)] flex justify-between items-center bg-[var(--bg-app)] shrink-0">
            <div>
              <h2 class="text-xl font-bold tracking-tight text-[var(--text-main)]">{{ isEditing ? 'Editar OS' : 'Criar Nova OS' }}</h2>
              <p class="text-xs text-[var(--text-muted)] font-bold mt-1">Preencha os dados da ordem de serviço.</p>
            </div>
            <button @click="closeEditModal" class="p-2 hover:bg-[var(--bg-card)] rounded-lg transition-colors">
              <X class="w-5 h-5 text-[var(--text-muted)]" />
            </button>
          </div>

          <form @submit.prevent="saveWorkOrder" class="p-6 overflow-y-auto flex-1 space-y-5">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">

              <!-- Tipo de OS -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Tipo de OS *</label>
                <select v-model="form.order_type" required class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] font-bold focus:outline-none focus:border-[var(--color-vintage-mint)]">
                  <option value="emergencial">Emergencial</option>
                  <option value="preditiva">Preditiva</option>
                  <option value="preventiva">Preventiva</option>
                  <option value="corretiva">Corretiva</option>
                </select>
              </div>

              <!-- Status (coluna Kanban) -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Status *</label>
                <select v-model="form.status" required class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] font-bold focus:outline-none focus:border-[var(--color-vintage-mint)]">
                  <option v-for="s in columns" :key="s.id" :value="s.id">{{ s.name }}</option>
                </select>
              </div>

              <!-- Máquina -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Máquina *</label>
                <select v-model="form.machine" required class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] font-bold focus:outline-none focus:border-[var(--color-vintage-mint)]">
                  <option :value="null" disabled>Selecione...</option>
                  <option v-for="m in machinesList" :key="m.id" :value="m.id">{{ machineName(m) }}</option>
                </select>
              </div>

              <!-- Atribuir para (Técnico responsável) -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">
                  Atribuir para
                </label>
                <select v-model="form.assigned_to" class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] font-bold focus:outline-none focus:border-[var(--color-vintage-mint)]">
                  <option :value="null">Não atribuído</option>
                  <option v-for="u in usersList" :key="u.id" :value="u.id">{{ u.name }}</option>
                </select>
              </div>

              <!-- Linha de Produção -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Linha de Produção</label>
                <input 
                  v-model="form.production_line" type="text"
                  placeholder="Ex: Linha A, Setor 3 (opcional)"
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)]" 
                />
              </div>

              <!-- Prioridade -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Prioridade</label>
                <select v-model="form.priority" class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] font-bold focus:outline-none focus:border-[var(--color-vintage-mint)]">
                  <option value="baixa">Baixa</option>
                  <option value="media">Média</option>
                  <option value="alta">Alta</option>
                  <option value="critica">Crítica</option>
                </select>
              </div>


              <!-- Observação -->
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Observação / Relato</label>
                <textarea 
                  v-model="form.observation" rows="3"
                  placeholder="Descreva o problema, contexto ou instruções..."
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] resize-none" 
                ></textarea>
              </div>

            </div>

            <!-- Actions -->
            <div class="flex gap-4 pt-4 border-t border-[var(--border-color)]">
              <button v-if="isEditing" type="button" @click="deleteWO(currentEditingId)" class="py-3 px-4 border-2 border-[var(--color-vintage-rose)] bg-[var(--color-vintage-rose)]/10 text-[var(--color-vintage-rose)] font-bold text-sm rounded-xl hover:bg-[var(--color-vintage-rose)] hover:text-white transition-colors">
                <Trash2 class="w-4 h-4" />
              </button>
              <button type="button" @click="closeEditModal" class="flex-1 py-3 border-2 border-[var(--border-color)] text-[var(--text-muted)] font-bold text-sm rounded-xl hover:bg-[var(--bg-app)] hover:text-[var(--text-main)] transition-colors">
                Cancelar
              </button>
              <button type="submit" class="flex-1 py-3 bg-[var(--color-vintage-mint)] text-white font-bold text-sm rounded-xl shadow-md hover:opacity-90 active:scale-[0.98] transition-all flex justify-center items-center gap-2">
                <Save class="w-4 h-4" />
                {{ isEditing ? 'Salvar Mudanças' : 'Criar Ordem' }}
              </button>
            </div>
          </form>

        </div>
      </div>
    </Teleport>

    <!-- READ-ONLY MODAL -->
    <Teleport to="body">
      <div v-if="showReadModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="showReadModal = false"></div>
        
        <div class="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-3xl w-full max-w-xl flex flex-col relative z-[101] shadow-2xl overflow-hidden">
          <div class="p-6 border-b border-[var(--border-color)] bg-[var(--bg-app)] flex justify-between items-start">
             <div>
               <div class="flex items-center gap-2 mb-2">
                  <span class="px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider rounded border" :class="priorityClass(selectedWO.priority)">
                     {{ priorityLabel(selectedWO.priority) }}
                  </span>
                  <span class="px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider rounded border border-[var(--color-vintage-mint)]/30 bg-[var(--color-vintage-mint)]/10 text-[var(--color-vintage-mint)]">
                     {{ selectedWO.status_detail?.name || '—' }}
                  </span>
               </div>
               <h2 class="text-xl font-bold tracking-tight text-[var(--text-main)]">
                 OS-{{ selectedWO.id }}
                 <span class="font-normal text-[var(--text-muted)] text-base">· {{ selectedWO.order_type_display || selectedWO.order_type }}</span>
               </h2>
             </div>
             <button @click="showReadModal = false" class="p-2 hover:bg-[var(--bg-card)] rounded-lg transition-colors border border-transparent hover:border-[var(--border-color)]">
                <X class="w-5 h-5 text-[var(--text-muted)]" />
             </button>
          </div>
          <div class="p-6 space-y-5 overflow-y-auto max-h-[60vh] card-scrollbar">
             <!-- Observação — expansível aqui no modal -->
             <div>
                <p class="text-[11px] font-bold uppercase text-[var(--text-muted)] mb-1">Observação / Relato</p>
                <div class="p-4 bg-[var(--bg-app)] rounded-xl border border-[var(--border-color)] text-sm text-[var(--text-main)] leading-relaxed min-h-[70px] whitespace-pre-wrap">
                   {{ selectedWO.observation || 'Sem observações registradas.' }}
                </div>
             </div>

             <div class="grid grid-cols-2 gap-4">
                <!-- Máquina -->
                <div class="p-4 bg-[var(--bg-app)] rounded-xl border border-[var(--border-color)] flex items-center gap-3">
                   <div class="p-2 bg-[var(--bg-card)] rounded-lg text-[var(--text-muted)]"><Activity class="w-5 h-5" /></div>
                   <div>
                     <p class="text-[10px] font-bold uppercase text-[var(--text-muted)]">Máquina</p>
                     <p class="text-sm font-bold text-[var(--text-main)] truncate max-w-[130px]">
                       {{ machineName(selectedWO.machine_detail) }}
                     </p>
                   </div>
                </div>
                <!-- Técnico atribuído -->
                <div class="p-4 bg-[var(--bg-app)] rounded-xl border border-[var(--border-color)] flex items-center gap-3">
                   <div class="p-2 bg-[var(--bg-card)] rounded-lg text-[var(--color-vintage-mint)]"><UserCheck class="w-5 h-5" /></div>
                   <div>
                     <p class="text-[10px] font-bold uppercase text-[var(--text-muted)]">Técnico</p>
                     <p class="text-sm font-bold text-[var(--text-main)] truncate max-w-[130px]">
                       {{ selectedWO.assigned_to_detail?.name || 'Não atribuído' }}
                     </p>
                   </div>
                </div>
                <!-- Linha de Produção -->
                <div class="p-4 bg-[var(--bg-app)] rounded-xl border border-[var(--border-color)] flex items-center gap-3">
                   <div class="p-2 bg-[var(--bg-card)] rounded-lg text-[var(--text-muted)]"><Settings class="w-5 h-5" /></div>
                   <div>
                     <p class="text-[10px] font-bold uppercase text-[var(--text-muted)]">Linha</p>
                     <p class="text-sm font-bold text-[var(--text-main)] truncate max-w-[130px]">{{ selectedWO.production_line || '—' }}</p>
                   </div>
                </div>
                <!-- Abertura -->
                <div class="p-4 bg-[var(--bg-app)] rounded-xl border border-[var(--border-color)] flex items-center gap-3">
                   <div class="p-2 bg-[var(--bg-card)] rounded-lg text-[var(--text-muted)]"><CalendarDays class="w-5 h-5" /></div>
                   <div>
                     <p class="text-[10px] font-bold uppercase text-[var(--text-muted)]">Abertura</p>
                     <p class="text-xs font-bold text-[var(--text-main)]">{{ formatDate(selectedWO.opening_date) }}</p>
                   </div>
                </div>
             </div>

             <!-- Histórico de Telemetria (ECharts) -->
             <div>
                <p class="text-[11px] font-bold uppercase text-[var(--text-muted)] mb-1">Histórico de Telemetria a partir da abertura</p>
                <div class="p-4 bg-[var(--bg-app)] rounded-xl border border-[var(--border-color)] min-h-[300px]">
                  <div v-if="osTelemetryLoading" class="flex justify-center items-center h-[260px]">
                    <div class="w-8 h-8 border-4 border-[var(--color-vintage-mint)] border-t-transparent rounded-full animate-spin"></div>
                  </div>
                  <div v-else-if="osTelemetryOption && osTelemetryOption.series.length > 0" class="h-[260px] w-full">
                    <v-chart class="chart" :option="osTelemetryOption" :update-options="{ notMerge: true }" autoresize />
                  </div>
                  <div v-else class="flex justify-center items-center h-[260px] text-[var(--text-muted)] text-sm italic">
                    Nenhum dado de telemetria encontrado a partir da data de abertura.
                  </div>
                </div>
              </div>
          </div>
          
          <div class="p-4 border-t border-[var(--border-color)] flex justify-between items-center bg-[var(--bg-app)]">
            <span class="text-xs text-[var(--text-muted)] font-medium">
               Aberta por {{ selectedWO.opened_by_detail?.name || 'Sistema' }}
            </span>
            <button 
              v-if="canEdit(selectedWO)"
              @click="openEditModalFromRead" 
              class="px-4 py-2 bg-[var(--color-vintage-mint)] text-white font-bold text-sm rounded-xl shadow-md hover:opacity-90 transition-all flex items-center gap-2"
            >
               <Edit3 class="w-4 h-4" /> Editar OS
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Plus, Filter, Edit3, Trash2, X, Save, Activity, CalendarDays, Settings, UserCheck, User, EyeOff } from 'lucide-vue-next'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { getWorkOrders, createWorkOrder, updateWorkOrder, deleteWorkOrder, getStatuses, moveWorkOrderStatus } from '@/services/work_orders'

import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent])

const authStore = useAuthStore()

// Data
const workOrders = ref([])
const columns = ref([])
const machinesList = ref([])
const usersList = ref([])

// UI State
const loading = ref(true)
const myTasksFilter = ref(false)
const daysFilter = ref(15)
const dragOverColumn = ref(null)
const isDragging = ref(false)
const draggedWoId = ref(null)
// Non-reactive reference to persist across dragend/drop event ordering
let _activeDragId = null
let _wasDragging = false

const canCreate = computed(() => authStore.user?.profile !== 'visualizador')

// Modals
const showEditModal = ref(false)
const isEditing = ref(false)
let currentEditingId = null

const showReadModal = ref(false)
const selectedWO = ref({})

// Form
const defaultForm = () => ({
  order_type: 'corretiva',
  production_line: '',
  machine: null,
  status: null,
  priority: 'media',
  observation: '',
  assigned_to: null,
})
const form = ref(defaultForm())

// ─── Helpers ──────────────────────────────────────────────
const firstName = (name) => name ? name.split(' ')[0] : ''

// ─── Kanban ───────────────────────────────────────────────
const getOrdersForColumn = (statusId) => {
  let list = workOrders.value.filter(w => w.status === statusId)
  if (myTasksFilter.value === true) {
    list = list.filter(w => w.opened_by === authStore.user?.id)
  } else if (myTasksFilter.value === 'assigned') {
    list = list.filter(w => w.assigned_to === authStore.user?.id)
  }
  return list
}

const colColor = (col) => {
  const map = {
    'To Do': 'bg-blue-400',
    'In Progress': 'bg-yellow-400',
    'Waiting': 'bg-orange-400',
    'Done': 'bg-green-400',
  }
  return map[col.name] || 'bg-gray-400'
}

// ─── Drag & Drop ──────────────────────────────────────────
const onDragStart = (e, wo) => {
  // Store in both reactive ref and non-reactive module var
  // _activeDragId persists reliably even when dragend fires before drop
  _activeDragId = wo.id
  _wasDragging = false
  isDragging.value = true
  draggedWoId.value = wo.id
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', String(wo.id))
  }
  // Visual feedback: slight opacity on the dragged card
  setTimeout(() => {
    if (e.target) e.target.style.opacity = '0.5'
  }, 0)
}

const onDragEnd = (e) => {
  // Mark that a drag just happened (for click guard)
  _wasDragging = true
  isDragging.value = false
  dragOverColumn.value = null
  if (e.target) e.target.style.opacity = ''
  // Clear _wasDragging after a short delay so click handler can check it
  setTimeout(() => {
    _wasDragging = false
    draggedWoId.value = null
    _activeDragId = null
  }, 200)
}

const onDragOver = (e, colId) => {
  e.preventDefault()
  if (e.dataTransfer) {
    e.dataTransfer.dropEffect = 'move'
  }
  dragOverColumn.value = colId
}

const onCardClick = (wo) => {
  // Ignore click if it was triggered right after a drag
  if (_wasDragging || isDragging.value) return
  openReadModal(wo)
}

const onDrop = async (e, toStatusId) => {
  e.preventDefault()
  dragOverColumn.value = null

  // Use _activeDragId (non-reactive, persists reliably across dragend/drop ordering)
  // Fallback to dataTransfer for cross-browser compatibility
  const rawId = _activeDragId ?? (e.dataTransfer ? e.dataTransfer.getData('text/plain') : null)
  const sourceId = rawId ? parseInt(rawId) : null

  // Clear state after reading
  _activeDragId = null
  draggedWoId.value = null
  isDragging.value = false

  if (!sourceId) {
    console.warn('[Kanban] onDrop: nenhum ID de card encontrado')
    return
  }

  const wo = workOrders.value.find(x => x.id === sourceId)
  if (!wo) {
    console.warn('[Kanban] onDrop: work order não encontrada:', sourceId)
    return
  }
  if (wo.status === toStatusId) return  // sem mudança

  const originalStatus = wo.status
  wo.status = toStatusId  // optimistic update

  try {
    await moveWorkOrderStatus(wo.id, toStatusId)
    window.dispatchEvent(new Event('refresh-notifications'))
  } catch (error) {
    const status = error.response?.status
    const detail = error.response?.data?.detail || error.response?.data?.error || error.message
    console.error('[Kanban] Falha ao mover card:', status, detail)
    wo.status = originalStatus  // rollback
    if (status === 403) {
      alert('Sem permissão para mover este card.')
    } else if (status === 400) {
      alert(`Dados inválidos: ${detail}`)
    } else {
      alert(`Não foi possível mover o card. (${status || 'Erro de rede'})`)
    }
  }
}

// ─── Formatters ───────────────────────────────────────────
const machineName = (m) => {
  if (!m) return 'Sem máquina'
  if (m.manufacturer && m.model) return `${m.manufacturer} ${m.model}`
  return m.serial_number || '—'
}

const priorityLabel = (p) => {
  const map = { baixa: 'Baixa', media: 'Média', alta: 'Alta', critica: 'Crítica' }
  return map[p] || p || '—'
}

const priorityClass = (p) => {
  const map = {
    baixa:  'text-[var(--text-muted)] border-[var(--border-color)]',
    media:  'text-blue-500 border-blue-500/30 bg-blue-500/10',
    alta:   'text-[var(--color-vintage-mustard)] border-[var(--color-vintage-mustard)]/30 bg-[var(--color-vintage-mustard)]/10',
    critica:'text-white bg-[var(--color-vintage-rose)] border-transparent',
  }
  return map[p] || 'text-[var(--text-muted)] border-[var(--border-color)]'
}

const formatDate = (dt) => {
  if (!dt) return '—'
  return new Date(dt).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit' })
}

// ─── Permissions ──────────────────────────────────────────
const canEdit = (wo) => {
  if (!wo) return false
  if (authStore.user?.profile === 'administrador') return true
  if (authStore.user?.profile === 'gerente') return true
  if (authStore.user?.profile === 'visualizador') return false
  if (wo.opened_by === authStore.user?.id) return true
  if (wo.assigned_to === authStore.user?.id) return true
  if (wo.assigned_to === null) return true // Permite que técnicos editem OS não atribuídas (em aberto)
  return false
}

// ─── Data ─────────────────────────────────────────────────
const fetchData = async () => {
  loading.value = true
  try {
    const [mRes, stRes, woRes, uRes] = await Promise.all([
      api.get('/machines/'),
      getStatuses(),
      getWorkOrders({ params: { days: daysFilter.value } }),
      api.get('/users/'),
    ])

    machinesList.value = mRes.data.results || mRes.data
    columns.value = stRes.data.results || stRes.data
    workOrders.value = woRes.data.results || woRes.data
    usersList.value = uRes.data.results || uRes.data

    // default status to first column
    if (columns.value.length > 0 && !form.value.status) {
      form.value.status = columns.value[0].id
    }
  } catch (e) {
    console.error('Erro ao carregar dados do Kanban:', e)
  } finally {
    loading.value = false
  }
}

// ─── Modal Flows ──────────────────────────────────────────
const osTelemetryLoading = ref(false)
const osTelemetryOption = ref(null)

const fetchOSTelemetry = async (woId) => {
  osTelemetryLoading.value = true
  osTelemetryOption.value = null
  try {
    const res = await api.get(`/analytics/os-telemetry/${woId}/`)
    const data = res.data
    
    if (data && data.series && data.series.length > 0) {
      const seriesList = data.series.map(s => ({
        name: s.name,
        type: 'line',
        smooth: true,
        data: s.data
      }))
      
      const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text-main').trim() || '#e2e8f0'
      const mutedColor = getComputedStyle(document.documentElement).getPropertyValue('--text-muted').trim() || '#94a3b8'

      osTelemetryOption.value = {
        tooltip: { trigger: 'axis' },
        legend: { bottom: 0, textStyle: { color: textColor } },
        grid: { left: '3%', right: '5%', bottom: '15%', top: '5%', containLabel: true },
        xAxis: { type: 'category', boundaryGap: false, data: data.dates, axisLabel: { color: mutedColor } },
        yAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed', color: mutedColor + '40' } }, axisLabel: { color: mutedColor } },
        series: seriesList
      }
    }
  } catch (e) {
    console.error('Failed to load OS telemetry', e)
  } finally {
    osTelemetryLoading.value = false
  }
}

const openReadModal = (wo) => {
  selectedWO.value = wo
  showReadModal.value = true
  fetchOSTelemetry(wo.id)
}

const openEditModalFromRead = () => {
  showReadModal.value = false
  openEditModal(selectedWO.value)
}

const openCreateModal = () => {
  isEditing.value = false
  currentEditingId = null
  form.value = defaultForm()
  if (columns.value.length > 0) form.value.status = columns.value[0].id
  showEditModal.value = true
}

const openEditModal = (wo) => {
  isEditing.value = true
  currentEditingId = wo.id
  form.value = {
    order_type: wo.order_type,
    production_line: wo.production_line,
    machine: wo.machine,
    status: wo.status,
    priority: wo.priority,
    observation: wo.observation,
    assigned_to: wo.assigned_to,
  }
  showEditModal.value = true
}

const closeEditModal = () => { showEditModal.value = false }

const saveWorkOrder = async () => {
  loading.value = true
  try {
    if (isEditing.value) {
      await updateWorkOrder(currentEditingId, form.value)
    } else {
      await createWorkOrder(form.value)
    }
    window.dispatchEvent(new Event('refresh-notifications'))
    closeEditModal()
    const woRes = await getWorkOrders({ params: { days: daysFilter.value } })
    workOrders.value = woRes.data.results || woRes.data
  } catch (err) {
    console.error(err)
    alert('Erro ao salvar a OS. Confira os campos obrigatórios.')
  } finally {
    loading.value = false
  }
}

const deleteWO = async (id) => {
  if (!confirm('Excluir esta OS permanentemente?')) return
  loading.value = true
  try {
    await deleteWorkOrder(id)
    closeEditModal()
    const woRes = await getWorkOrders({ params: { days: daysFilter.value } })
    workOrders.value = woRes.data.results || woRes.data
  } catch (err) {
    console.error(err)
    alert('Falha ao deletar. Confira suas permissões.')
  } finally {
    loading.value = false
  }
}

// Polling background update
let pollInterval = null;

const fetchWorkOrdersOnly = async () => {
  try {
    const woRes = await getWorkOrders({ params: { days: daysFilter.value }, headers: { 'X-Silent': 'true' } })
    workOrders.value = woRes.data.results || woRes.data
  } catch (e) {
    console.error('Erro no auto-refresh do Kanban:', e)
  }
}

onMounted(() => { 
  fetchData() 
  pollInterval = setInterval(fetchWorkOrdersOnly, 10000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<style scoped>
.card-scrollbar::-webkit-scrollbar { width: 4px; }
.card-scrollbar::-webkit-scrollbar-track { background: transparent; }
.card-scrollbar::-webkit-scrollbar-thumb { background-color: var(--border-color); border-radius: 10px; }

.kanban-scrollbar::-webkit-scrollbar { height: 6px; }
.kanban-scrollbar::-webkit-scrollbar-track { background: transparent; }
.kanban-scrollbar::-webkit-scrollbar-thumb { background-color: var(--border-color); border-radius: 10px; }

.kanban-column {
  transition: border-color 0.15s;
}
.kanban-column.drag-over {
  border-color: var(--color-vintage-mint);
  box-shadow: 0 0 0 2px var(--color-vintage-mint);
}

.kanban-card[draggable='true']:active {
  opacity: 0.7;
  transform: scale(0.97) rotate(0.5deg);
  cursor: grabbing !important;
}

.kanban-card[draggable='true'] {
  user-select: none;
  -webkit-user-drag: element;
}

.chart {
  width: 100%;
  height: 100%;
}
</style>
