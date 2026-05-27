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
        @click="openCreateModal"
        class="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[var(--color-vintage-mint)] text-white font-bold shadow-md hover:-translate-y-0.5 transition-transform"
      >
        <Plus class="w-5 h-5" />
        Nova OS
      </button>
    </div>

    <!-- Toolbar Filters -->
    <div class="flex flex-col md:flex-row gap-4 items-center justify-between">
      <div class="flex items-center bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl px-2 shadow-sm">
         <Filter class="w-4 h-4 text-[var(--text-muted)] ml-2 shrink-0" />
         <select 
           v-model="myTasksFilter" 
           class="bg-transparent border-none focus:outline-none py-2.5 px-3 text-sm font-bold text-[var(--text-main)] cursor-pointer"
         >
           <option :value="false">Exibir todas as OS</option>
           <option :value="true">Abertas por mim</option>
         </select>
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
        @dragover.prevent="dragOverColumn = col.id"
        @dragleave="dragOverColumn = null"
        @drop="onDrop($event, col.id)"
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
            draggable="true"
            @dragstart="onDragStart($event, wo)"
            @dragend="dragOverColumn = null"
            @click="openReadModal(wo)"
            class="kanban-card bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl p-4 shadow-sm hover:border-[var(--color-vintage-mint)] hover:shadow-md transition-all cursor-pointer group relative"
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

            <!-- Observation snippet -->
            <p v-if="wo.observation" class="text-[11px] text-[var(--text-muted)] mb-3 line-clamp-2 italic">
              {{ wo.observation }}
            </p>

            <!-- Footer -->
            <div class="flex items-center justify-between text-[10px] text-[var(--text-muted)] pt-3 border-t border-[var(--border-color)]">
              <span class="font-bold uppercase flex items-center gap-1">
                <CalendarDays class="w-3 h-3" />
                {{ formatDate(wo.opening_date) }}
              </span>
              <span class="font-bold uppercase flex items-center gap-1 px-2 py-0.5 rounded border" :class="priorityClass(wo.priority)">
                {{ priorityLabel(wo.priority) }}
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

              <!-- Linha de Produção -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Linha de Produção *</label>
                <input 
                  v-model="form.production_line" type="text" required
                  placeholder="Ex: Linha A, Setor 3..."
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

              <!-- Temperatura -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Temperatura (°C)</label>
                <input 
                  v-model="form.temperature" type="number" step="0.01"
                  placeholder="Opcional"
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)]" 
                />
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

          <div class="p-6 space-y-5">
             <!-- Observação -->
             <div>
                <p class="text-[11px] font-bold uppercase text-[var(--text-muted)] mb-1">Observação / Relato</p>
                <div class="p-4 bg-[var(--bg-app)] rounded-xl border border-[var(--border-color)] text-sm text-[var(--text-main)] leading-relaxed min-h-[70px]">
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
                <!-- Linha de Produção -->
                <div class="p-4 bg-[var(--bg-app)] rounded-xl border border-[var(--border-color)] flex items-center gap-3">
                   <div class="p-2 bg-[var(--bg-card)] rounded-lg text-[var(--text-muted)]"><Settings class="w-5 h-5" /></div>
                   <div>
                     <p class="text-[10px] font-bold uppercase text-[var(--text-muted)]">Linha</p>
                     <p class="text-sm font-bold text-[var(--text-main)] truncate max-w-[130px]">{{ selectedWO.production_line || '—' }}</p>
                   </div>
                </div>
                <!-- Sensores da Máquina (Última Leitura) -->
                <div v-for="(sensor, idx) in selectedWO.latest_sensors" :key="'s-'+idx" class="p-4 bg-[var(--bg-app)] rounded-xl border border-[var(--border-color)] flex items-center gap-3">
                   <div class="p-2 bg-[var(--bg-card)] rounded-lg text-[var(--text-muted)]"><Activity class="w-5 h-5" /></div>
                   <div>
                     <p class="text-[10px] font-bold uppercase text-[var(--text-muted)]">{{ sensor.sensor_type }}</p>
                     <p class="text-sm font-bold text-[var(--text-main)]">{{ sensor.value !== null ? sensor.value + ' ' + sensor.unit : 'N/A' }}</p>
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
import { ref, onMounted, onUnmounted } from 'vue'
import { Plus, Filter, Edit3, Trash2, X, Save, Activity, CalendarDays, Settings, Thermometer } from 'lucide-vue-next'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { getWorkOrders, createWorkOrder, updateWorkOrder, deleteWorkOrder, getStatuses } from '@/services/work_orders'

const authStore = useAuthStore()

// Data
const workOrders = ref([])
const columns = ref([])
const machinesList = ref([])

// UI State
const loading = ref(true)
const myTasksFilter = ref(false)
const dragOverColumn = ref(null)

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
  temperature: null,
  observation: '',
})
const form = ref(defaultForm())

// ─── Kanban ───────────────────────────────────────────────
const getOrdersForColumn = (statusId) => {
  let list = workOrders.value.filter(w => w.status === statusId)
  if (myTasksFilter.value) {
    list = list.filter(w => w.opened_by === authStore.user?.id)
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
  e.dataTransfer.dropEffect = 'move'
  e.dataTransfer.effectAllowed = 'move'
  e.dataTransfer.setData('sourceId', wo.id.toString())
}

const onDrop = async (e, toStatusId) => {
  dragOverColumn.value = null
  const sourceId = e.dataTransfer.getData('sourceId')
  if (!sourceId) return

  const wo = workOrders.value.find(x => x.id === parseInt(sourceId))
  if (!wo || wo.status === toStatusId) return

  if (!canEdit(wo)) {
    alert('Você não tem permissão para alterar o status desta OS.')
    return
  }

  const originalStatus = wo.status
  wo.status = toStatusId  // optimistic update

  try {
    await updateWorkOrder(wo.id, { status: toStatusId })
    window.dispatchEvent(new Event('refresh-notifications'))
  } catch (error) {
    console.error('Drop update failed', error)
    wo.status = originalStatus
    alert('Não foi possível mover o card.')
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
  if (wo.opened_by === authStore.user?.id) return true
  return false
}

// ─── Data ─────────────────────────────────────────────────
const fetchData = async () => {
  loading.value = true
  try {
    const [mRes, stRes, woRes] = await Promise.all([
      api.get('/machines/'),
      getStatuses(),
      getWorkOrders(),
    ])

    machinesList.value = mRes.data.results || mRes.data
    columns.value = stRes.data.results || stRes.data
    workOrders.value = woRes.data.results || woRes.data

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
const openReadModal = (wo) => {
  selectedWO.value = wo
  showReadModal.value = true
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
    temperature: wo.temperature,
    observation: wo.observation,
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
    const woRes = await getWorkOrders()
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
    const woRes = await getWorkOrders()
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
    const woRes = await getWorkOrders()
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

.kanban-card:active {
  opacity: 0.8;
  transform: scale(0.98) rotate(1deg);
}
</style>
