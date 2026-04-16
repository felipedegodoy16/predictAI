<template>
  <div class="h-full flex flex-col gap-6 relative pb-10">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tighter flex items-center gap-2">
          <ClipboardList class="w-8 h-8 text-[var(--color-vintage-charcoal)] dark:text-[var(--text-main)]" />
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
           @change="applyFilter"
           class="bg-transparent border-none focus:outline-none py-2.5 px-3 text-sm font-bold text-[var(--text-main)] cursor-pointer"
         >
           <option :value="false">Exibir Toda a Frota</option>
           <option :value="true">Apenas Minhas Tarefas</option>
         </select>
      </div>
    </div>

    <!-- Kanban Board -->
    <div class="flex-1 flex gap-6 overflow-x-auto overflow-y-hidden pb-4 vintage-scrollbar">
      <!-- Loading Overlay -->
      <div v-if="loading" class="absolute inset-0 z-10 bg-[var(--bg-card)]/50 backdrop-blur-sm flex items-center justify-center">
         <div class="w-10 h-10 border-4 border-[var(--color-vintage-mint)] border-t-transparent rounded-full animate-spin"></div>
      </div>

      <!-- Columns Dynamically Loaded -->
      <div 
        v-for="col in columns" 
        :key="col.id"
        class="flex-shrink-0 w-80 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl flex flex-col overflow-hidden shadow-sm"
        @dragover.prevent
        @dragenter.prevent
        @drop="onDrop($event, col.id)"
      >
        <!-- Column Header -->
        <div class="p-4 border-b border-[var(--border-color)] bg-[var(--bg-app)]/50 flex justify-between items-center">
          <h3 class="font-bold text-[var(--text-main)] tracking-tight">{{ col.name }}</h3>
          <span class="text-xs font-bold bg-[var(--text-main)]/10 text-[var(--text-main)] px-2 py-0.5 rounded-full">
            {{ getOrdersForColumn(col.id).length }}
          </span>
        </div>

        <!-- Column Body -->
        <div class="flex-1 overflow-y-auto p-3 space-y-3 custom-scrollbar">
          <!-- Empty State -->
          <div v-if="getOrdersForColumn(col.id).length === 0" class="h-full flex items-center justify-center text-center text-xs font-medium text-[var(--text-muted)] p-4 border-2 border-dashed border-[var(--border-color)] rounded-xl opacity-50">
            Nenhuma OS aqui
          </div>

          <!-- Kanban Card -->
          <div 
            v-for="wo in getOrdersForColumn(col.id)" 
            :key="wo.id"
            draggable="true"
            @dragstart="onDragStart($event, wo)"
            @click="openReadModal(wo)"
            class="bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl p-4 shadow-sm hover:border-[var(--color-vintage-mint)] hover:shadow-md transition-all cursor-pointer group relative"
          >
            <div class="flex justify-between items-start mb-2">
              <span class="px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider rounded border"
                :class="{
                  'text-[var(--text-muted)] border-[var(--border-color)]': wo.priority === 'LOW',
                  'text-blue-500 border-blue-500/30 bg-blue-500/10': wo.priority === 'MEDIUM',
                  'text-[var(--color-vintage-mustard)] border-[var(--color-vintage-mustard)]/30 bg-[var(--color-vintage-mustard)]/10': wo.priority === 'HIGH',
                  'text-white bg-[var(--color-vintage-rose)] border-transparent': wo.priority === 'CRITICAL',
                }"
              >
                {{ formatPriority(wo.priority) }}
              </span>

              <!-- Edit Pencil (Only show if allowed) -->
              <button 
                v-if="canEdit(wo)"
                @click.stop="openEditModal(wo)" 
                class="opacity-0 group-hover:opacity-100 p-1 rounded-md text-[var(--text-muted)] hover:text-[var(--color-vintage-mint)] hover:bg-[var(--color-vintage-mint)]/10 transition-all"
                title="Editar OS"
              >
                <Edit3 class="w-4 h-4" />
              </button>
            </div>

            <h4 class="font-bold text-sm text-[var(--text-main)] mb-1 leading-snug">{{ wo.title }}</h4>
            <p class="text-[11px] text-[var(--text-muted)] font-medium mb-3 line-clamp-2">
              {{ getMachineName(wo.machine) }}
            </p>

            <div class="flex items-center justify-between text-[10px] text-[var(--text-muted)] pt-3 border-t border-[var(--border-color)]">
              <span class="font-bold uppercase flex items-center gap-1">
                <AlertCircle class="w-3 h-3" />
                {{ getErrorTypeName(wo.error_type) }}
              </span>
              <div v-if="wo.assigned_to" class="w-6 h-6 rounded-full bg-[var(--color-vintage-mint)]/20 text-[var(--color-vintage-mint)] flex items-center justify-center font-bold text-[9px]" :title="getUserName(wo.assigned_to)">
                 {{ getUserInitials(wo.assigned_to) }}
              </div>
              <div v-else class="w-6 h-6 rounded-full border border-dashed border-[var(--text-muted)] flex items-center justify-center text-[var(--text-muted)]" title="Não atribuída">
                 <UserPlus class="w-3 h-3" />
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- CREATE/EDIT MODAL OVERLAY -->
    <Teleport to="body">
      <div v-if="showEditModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="closeEditModal"></div>
        
        <div class="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-3xl w-full max-w-2xl max-h-[90vh] flex flex-col relative z-[101] shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
          
          <div class="p-6 border-b border-[var(--border-color)] flex justify-between items-center bg-[var(--bg-app)] shrink-0">
            <div>
              <h2 class="text-xl font-bold tracking-tight text-[var(--text-main)]">{{ isEditing ? 'Editar OS / Mover' : 'Criar Nova OS' }}</h2>
              <p class="text-xs text-[var(--text-muted)] font-bold mt-1">Configure os paramêtros e tarefas.</p>
            </div>
            <button @click="closeEditModal" class="p-2 hover:bg-[var(--bg-card)] rounded-lg transition-colors">
              <X class="w-5 h-5 text-[var(--text-muted)]" />
            </button>
          </div>

          <form @submit.prevent="saveWorkOrder" class="p-6 overflow-y-auto flex-1 space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Título da Ordem*</label>
                <input 
                  v-model="form.title" type="text" required
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)]" 
                />
              </div>

              <div class="col-span-1 md:col-span-2">
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Descrição Técnica / Problema</label>
                <textarea 
                  v-model="form.description" rows="3"
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] resize-none" 
                ></textarea>
              </div>

              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Tipo de Erro / Razão</label>
                <select v-model="form.error_type" class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] font-bold focus:outline-none">
                  <option :value="null">Desconhecido / Em Análise</option>
                  <option v-for="e in errorTypes" :key="e.id" :value="e.id">{{ e.name }}</option>
                </select>
              </div>

              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Status Base</label>
                <select v-model="form.status" required class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] font-bold focus:outline-none">
                  <option v-for="s in columns" :key="s.id" :value="s.id">{{ s.name }}</option>
                </select>
              </div>

              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Máquina Relacionada</label>
                <select v-model="form.machine" class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] font-bold focus:outline-none">
                  <option :value="null">Geral (Nenhuma)</option>
                  <option v-for="m in machinesList" :key="m.id" :value="m.id">{{ m.name }}</option>
                </select>
              </div>

               <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Atribuir a Quem?</label>
                <select v-model="form.assigned_to" class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] font-bold focus:outline-none">
                  <option :value="null">Deixar em Aberto</option>
                  <option v-for="u in usersList" :key="u.id" :value="u.id">{{ u.name }}</option>
                </select>
              </div>

               <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Prioridade</label>
                <select v-model="form.priority" class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] font-bold focus:outline-none">
                  <option value="LOW">Baixa</option>
                  <option value="MEDIUM">Média</option>
                  <option value="HIGH">Alta</option>
                  <option value="CRITICAL">Crítica</option>
                </select>
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
        
        <div class="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-3xl w-full max-w-xl flex flex-col relative z-[101] shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
          <div class="p-6 border-b border-[var(--border-color)] bg-[var(--bg-app)] flex justify-between items-start">
             <div>
               <div class="flex items-center gap-2 mb-2">
                  <span class="px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider rounded border border-[var(--border-color)] text-[var(--text-muted)]">
                     {{ formatPriority(selectedWO.priority) }}
                  </span>
                  <span class="px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider rounded border border-[var(--color-vintage-mint)]/30 bg-[var(--color-vintage-mint)]/10 text-[var(--color-vintage-mint)]">
                     {{ selectedWO.status_detail?.name || 'Desconhecido' }}
                  </span>
               </div>
               <h2 class="text-2xl font-bold tracking-tight text-[var(--text-main)]">{{ selectedWO.title }}</h2>
             </div>
             <button @click="showReadModal = false" class="p-2 hover:bg-[var(--bg-card)] rounded-lg transition-colors border border-transparent hover:border-[var(--border-color)]">
                <X class="w-5 h-5 text-[var(--text-muted)]" />
             </button>
          </div>

          <div class="p-6 space-y-6">
             <div>
                <p class="text-[11px] font-bold uppercase text-[var(--text-muted)] mb-1">Problema / Relato</p>
                <div class="p-4 bg-[var(--bg-app)] rounded-xl border border-[var(--border-color)] text-sm text-[var(--text-main)] leading-relaxed min-h-[80px]">
                   {{ selectedWO.description || 'Sem descrição detalhada.' }}
                </div>
             </div>

             <div class="grid grid-cols-2 gap-4">
                <div class="p-4 bg-[var(--bg-app)] rounded-xl border border-[var(--border-color)] flex items-center gap-3">
                   <div class="p-2 bg-[var(--bg-card)] rounded-lg text-[var(--text-muted)]"><Activity class="w-5 h-5" /></div>
                   <div>
                     <p class="text-[10px] font-bold uppercase text-[var(--text-muted)]">Máquina</p>
                     <p class="text-sm font-bold text-[var(--text-main)] truncate max-w-[150px]">{{ getMachineName(selectedWO.machine) }}</p>
                   </div>
                </div>
                <div class="p-4 bg-[var(--bg-app)] rounded-xl border border-[var(--border-color)] flex items-center gap-3">
                   <div class="p-2 bg-[var(--bg-card)] rounded-lg text-[var(--text-muted)]"><AlertCircle class="w-5 h-5" /></div>
                   <div>
                     <p class="text-[10px] font-bold uppercase text-[var(--text-muted)]">Causa / Erro</p>
                     <p class="text-sm font-bold text-[var(--text-main)] truncate max-w-[150px]">{{ getErrorTypeName(selectedWO.error_type) }}</p>
                   </div>
                </div>
                <div class="p-4 bg-[var(--bg-app)] rounded-xl border border-[var(--border-color)] flex items-center gap-3">
                   <div class="p-2 bg-[var(--bg-card)] rounded-lg text-[var(--text-muted)]"><User class="w-5 h-5" /></div>
                   <div>
                     <p class="text-[10px] font-bold uppercase text-[var(--text-muted)]">Atribuído a</p>
                     <p class="text-sm font-bold text-[var(--text-main)] truncate max-w-[150px]">{{ getUserName(selectedWO.assigned_to) || 'Todos (Em Aberto)' }}</p>
                   </div>
                </div>
                <div class="p-4 bg-[var(--bg-app)] rounded-xl border border-[var(--border-color)] flex items-center gap-3">
                   <div class="p-2 bg-[var(--bg-card)] rounded-lg text-[var(--text-muted)]"><Calendar class="w-5 h-5" /></div>
                   <div>
                     <p class="text-[10px] font-bold uppercase text-[var(--text-muted)]">Abertura</p>
                     <p class="text-xs font-bold text-[var(--text-main)] truncate max-w-[150px]">{{ new Date(selectedWO.created_at).toLocaleDateString() }}</p>
                   </div>
                </div>
             </div>
          </div>
          
          <div class="p-4 border-t border-[var(--border-color)] flex justify-between items-center bg-[var(--bg-app)]">
            <span class="text-xs text-[var(--text-muted)] font-medium">
               Criado por {{ getUserName(selectedWO.created_by) || 'Sistema/Sensor' }}
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
import { ref, onMounted, computed } from 'vue'
import { ClipboardList, Plus, Filter, Edit3, Trash2, X, Save, AlertCircle, UserPlus, Activity, User, Calendar } from 'lucide-vue-next'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { getWorkOrders, createWorkOrder, updateWorkOrder, deleteWorkOrder, getStatuses, getErrorTypes } from '@/services/work_orders'

const authStore = useAuthStore()

// Datasets
const workOrders = ref([])
const columns = ref([])
const errorTypes = ref([])
const machinesList = ref([])
const usersList = ref([])

// UI State
const loading = ref(true)
const myTasksFilter = ref(false)

// Modals
const showEditModal = ref(false)
const isEditing = ref(false)
let currentEditingId = null

const showReadModal = ref(false)
const selectedWO = ref({})

// Form base
const emptyForm = {
  title: '',
  description: '',
  machine: null,
  assigned_to: null,
  status: null, // Initialized via mount to the first column
  error_type: null,
  priority: 'MEDIUM',
}
const form = ref({ ...emptyForm })

// --- Kanban Column Logic ---
const getOrdersForColumn = (statusId) => {
  let filtered = workOrders.value.filter(w => w.status === statusId)
  if (myTasksFilter.value) {
    filtered = filtered.filter(w => w.assigned_to === authStore.user?.id)
  }
  return filtered
}

// --- Drag and Drop ---
const onDragStart = (e, wo) => {
  if (!canEdit(wo)) {
    // If user cannot edit, prevent dragging, but visually we allow dragstart, so let's simply reset it.
    // Or we can just let UI drag but it will fail on drop. Let's send it anyway.
  }
  e.dataTransfer.dropEffect = 'move'
  e.dataTransfer.effectAllowed = 'move'
  e.dataTransfer.setData('sourceId', wo.id.toString())
}

const onDrop = async (e, toStatusId) => {
  const sourceId = e.dataTransfer.getData('sourceId')
  if (!sourceId) return

  const wo = workOrders.value.find(x => x.id === parseInt(sourceId))
  if (!wo || wo.status === toStatusId) return

  // Permission Guard
  if (!canEdit(wo)) {
    alert("Você não tem permissão para alterar o status desta Ordem de Serviço.")
    return
  }

  // Optimistic UI Update
  const originalStatus = wo.status
  wo.status = toStatusId

  try {
    await updateWorkOrder(wo.id, { status: toStatusId })
    // Sucesso, podemos forçar atualização da aba do sino via evento
    window.dispatchEvent(new Event('refresh-notifications'))
  } catch (error) {
    console.error('Dragdrop update failed', error)
    wo.status = originalStatus // Revert
    alert("Não foi possível mover o card. Confira suas permissões.")
  }
}


// --- Formatters ---
const formatPriority = (priority) => {
  const map = { 'LOW': 'Baixa', 'MEDIUM': 'Média', 'HIGH': 'Alta', 'CRITICAL': 'Crítica' }
  return map[priority] || priority
}

const getMachineName = (id) => {
  if (!id) return 'Sem Vínculo Específico'
  const m = machinesList.value.find(x => x.id === id)
  return m ? m.name : id
}

const getUserName = (id) => {
  if (!id) return ''
  const u = usersList.value.find(x => x.id === id)
  return u ? u.name : id
}

const getUserInitials = (id) => {
  const name = getUserName(id)
  return name ? name.substring(0, 2).toUpperCase() : '?'
}

const getErrorTypeName = (id) => {
  if (!id) return 'Geral / Desconhecido'
  const e = errorTypes.value.find(x => x.id === id)
  return e ? e.name : 'Outro'
}

// --- Permissions ---
const canEdit = (wo) => {
  if (authStore.userRole === 'ADMIN') return true
  if (wo.created_by === authStore.user?.id) return true
  if (wo.assigned_to === authStore.user?.id) return true
  return false
}

// --- Data Hydration ---
const fetchData = async () => {
  loading.value = true
  try {
    const [mRes, uRes, stRes, errRes, woRes] = await Promise.all([
      api.get('/machines/'),
      api.get('/users/'),
      getStatuses(),
      getErrorTypes(),
      getWorkOrders()
    ])
    
    machinesList.value = mRes.data.results || mRes.data
    usersList.value = uRes.data.results || uRes.data
    columns.value = stRes.data.results || stRes.data
    errorTypes.value = errRes.data.results || errRes.data
    workOrders.value = woRes.data.results || woRes.data

    if (columns.value.length > 0) {
      emptyForm.status = columns.value[0].id
    }
  } catch (e) {
    console.error('Error fetching dashboard data:', e)
  } finally {
    loading.value = false
  }
}

const applyFilter = () => {
  // Re-calculated via computed `getOrdersForColumn` seamlessly.
}

// --- Editing & Modal Flows ---
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
  form.value = { ...emptyForm }
  showEditModal.value = true
}

const openEditModal = (wo) => {
  isEditing.value = true
  currentEditingId = wo.id
  form.value = {
    title: wo.title,
    description: wo.description,
    machine: wo.machine,
    assigned_to: wo.assigned_to,
    status: wo.status,
    error_type: wo.error_type,
    priority: wo.priority,
  }
  showEditModal.value = true
}

const closeEditModal = () => showEditModal.value = false

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
    
    // Quick refresh of the array to get new data including `created_by` mapping
    const woRes = await getWorkOrders()
    workOrders.value = woRes.data.results || woRes.data

  } catch (err) {
    console.error(err)
    alert('Erro ao salvar a OS. Você possui permissões?')
  } finally {
    loading.value = false
  }
}

const deleteWO = async (id) => {
  if (confirm('Aviso: Excluir OS permanentemente?')) {
    loading.value = true
    try {
      await deleteWorkOrder(id)
      closeEditModal()
      const woRes = await getWorkOrders()
      workOrders.value = woRes.data.results || woRes.data
    } catch (err) {
      console.error(err)
      alert("Falha ao deletar. Confira regras.")
    } finally {
      loading.value = false
    }
  }
}

onMounted(() => {
  fetchData()
})

</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: var(--border-color);
  border-radius: 10px;
}
</style>
