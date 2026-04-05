<template>
  <div class="h-full flex flex-col gap-6 relative pb-10">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tighter flex items-center gap-2">
          Frota Operacional
        </h1>
        <p class="text-[var(--text-muted)] font-medium">Gestão, status e cadastramento de equipamentos ativos.</p>
      </div>
      
      <button 
        @click="openCreateModal"
        class="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[var(--color-vintage-mint)] text-white font-bold shadow-md hover:-translate-y-0.5 transition-transform"
      >
        <Plus class="w-5 h-5" />
        Cadastrar Máquina
      </button>
    </div>

    <!-- Filters & Search Toolbar -->
    <div class="flex flex-col md:flex-row gap-4 items-center justify-between">
      <div class="flex-1 w-full relative">
        <label for="search" class="sr-only">Pesquisar</label>
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search class="w-5 h-5 text-[var(--text-muted)]" />
        </div>
        <input 
          id="search"
          v-model="searchQuery"
          @keyup.enter="handleSearch"
          type="text" 
          placeholder="Pesquisar por ID, Nome, Fabricante..." 
          class="w-full max-w-md pl-10 pr-4 py-2.5 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl text-sm focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors text-[var(--text-main)] font-medium shadow-sm"
        />
        <button 
          v-if="searchQuery" 
          @click="clearSearch"
          class="absolute inset-y-0 left-[26rem] flex items-center text-[var(--text-muted)] hover:text-[var(--text-main)]"
        >
          <X class="w-4 h-4 ml-2" />
        </button>
      </div>

      <div class="flex gap-4 w-full md:w-auto mt-2 md:mt-0">
        <!-- View Mode Toggle -->
        <div class="hidden sm:flex items-center bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-1 shadow-sm">
           <button 
             @click="viewMode = 'table'"
             :class="['p-1.5 rounded-lg transition-colors', viewMode === 'table' ? 'bg-[var(--bg-app)] text-[var(--color-vintage-mint)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]']"
             title="Visualização em Lista"
           >
             <List class="w-4 h-4" />
           </button>
           <button 
             @click="viewMode = 'grid'"
             :class="['p-1.5 rounded-lg transition-colors', viewMode === 'grid' ? 'bg-[var(--bg-app)] text-[var(--color-vintage-mint)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]']"
             title="Visualização em Cards"
           >
             <LayoutGrid class="w-4 h-4" />
           </button>
        </div>

        <!-- Status Filter -->
        <div class="flex items-center bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl px-2 shadow-sm">
           <Filter class="w-4 h-4 text-[var(--text-muted)] ml-2 shrink-0" />
           <select 
             v-model="statusFilter" 
             @change="fetchMachines"
             class="bg-transparent border-none focus:outline-none py-2.5 px-3 text-sm font-bold text-[var(--text-main)] cursor-pointer"
           >
             <option value="">Status: Todos</option>
             <option value="ACTIVE">Status: Ativa</option>
             <option value="MAINTENANCE">Status: Em Manutenção</option>
             <option value="INACTIVE">Status: Inativa</option>
           </select>
        </div>

        <!-- Page Size Selector -->
        <div class="flex items-center bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl px-2 shadow-sm">
           <Layers class="w-4 h-4 text-[var(--text-muted)] ml-2 shrink-0" />
           <select 
             v-model="pageSize" 
             @change="resetPagination"
             class="bg-transparent border-none focus:outline-none py-2.5 px-3 text-sm font-bold text-[var(--text-main)] cursor-pointer"
           >
             <option :value="10">Exibir 10</option>
             <option :value="20">Exibir 20</option>
             <option :value="30">Exibir 30</option>
             <option :value="50">Exibir 50</option>
           </select>
        </div>
      </div>
    </div>

    <!-- Data Table -->
    <div class="vintage-panel flex-1 flex flex-col overflow-hidden relative shadow-md">
      
      <!-- Loading Overlay -->
      <div v-if="loading" class="absolute inset-0 z-10 bg-[var(--bg-card)]/50 backdrop-blur-sm flex items-center justify-center">
         <div class="w-10 h-10 border-4 border-[var(--color-vintage-mint)] border-t-transparent rounded-full animate-spin"></div>
      </div>

      <div v-if="viewMode === 'table'" class="overflow-x-auto">
        <table class="w-full text-left text-sm whitespace-nowrap">
          <thead class="bg-[var(--bg-app)] border-b border-[var(--border-color)] text-[10px] uppercase tracking-wider font-extrabold text-[var(--text-muted)]">
            <tr>
              <th scope="col" class="px-6 py-4">Nome / ID Base</th>
              <th scope="col" class="px-6 py-4">Status</th>
              <th scope="col" class="px-6 py-4">Fabricante & Modelo</th>
              <th scope="col" class="px-6 py-4">Localização (Setor)</th>
              <th scope="col" class="px-6 py-4 text-center">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[var(--border-color)] font-medium">
            <tr v-if="machines.length === 0 && !loading">
              <td colspan="5" class="px-6 py-12 text-center text-[var(--text-muted)]">
                Nenhum equipamento foi encontrado de acordo com os filtros selecionados.
              </td>
            </tr>
            <tr 
              v-for="mach in machines" 
              :key="mach.id" 
              class="hover:bg-[var(--bg-app)]/50 transition-colors group cursor-pointer"
            >
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                   <div class="w-10 h-10 rounded-xl bg-[var(--bg-app)] border border-[var(--border-color)] flex items-center justify-center text-[var(--color-vintage-charcoal)] dark:text-[var(--text-main)] shadow-sm">
                      <Cpu class="w-5 h-5 text-[var(--text-muted)]" />
                   </div>
                   <div>
                     <p class="font-bold text-[var(--text-main)] text-[15px] group-hover:text-[var(--color-vintage-mint)] transition-colors">{{ mach.name }}</p>
                     <p class="text-xs text-[var(--text-muted)] uppercase tracking-wider">{{ mach.serial_number }}</p>
                   </div>
                </div>
              </td>
              <td class="px-6 py-4">
                 <span class="px-3 py-1 text-[11px] uppercase tracking-wider font-bold rounded-full border"
                  :class="{
                    'bg-[var(--color-vintage-mint)]/10 text-[var(--color-vintage-mint)] border-[var(--color-vintage-mint)]/20': mach.status === 'ACTIVE',
                    'bg-[var(--color-vintage-mustard)]/10 text-[var(--color-vintage-mustard)] border-[var(--color-vintage-mustard)]/20': mach.status === 'MAINTENANCE',
                    'bg-[var(--color-vintage-rose)]/10 text-[var(--color-vintage-rose)] border-[var(--color-vintage-rose)]/20': mach.status === 'INACTIVE',
                  }"
                 >
                   {{ formatStatus(mach.status) }}
                 </span>
              </td>
              <td class="px-6 py-4">
                <p class="text-sm font-bold text-[var(--text-main)]">{{ mach.manufacturer || 'Não catalogado' }}</p>
                <p class="text-xs text-[var(--text-muted)] truncate max-w-[150px]">{{ mach.model || 'Sem especificação' }}</p>
              </td>
              <td class="px-6 py-4 text-sm text-[var(--text-muted)] font-bold">
                {{ mach.location || 'Sem Definição' }}
              </td>
              <td class="px-6 py-4 text-center">
                <div class="flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                   <button @click.stop="openEditModal(mach)" title="Editar" class="p-1.5 rounded hover:bg-[var(--color-vintage-mint)]/20 text-[var(--color-vintage-mint)] transition-colors">
                     <Edit3 class="w-4 h-4" />
                   </button>
                   <button @click.stop="deleteMachine(mach.id)" title="Deletar Máquina" class="p-1.5 rounded hover:bg-[var(--color-vintage-rose)]/20 text-[var(--color-vintage-rose)] transition-colors">
                     <Trash2 class="w-4 h-4" />
                   </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Grid View (Cards) -->
      <div v-else-if="viewMode === 'grid'" class="p-6 overflow-y-auto w-full h-[calc(100vh-280px)]">
        <div v-if="machines.length === 0 && !loading" class="text-center text-[var(--text-muted)] py-12">
           Nenhum equipamento foi encontrado de acordo com os filtros selecionados.
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 content-start pb-8">
           <div 
             v-for="mach in machines" 
             :key="mach.id"
             class="bg-[var(--bg-app)] border border-[var(--border-color)] rounded-2xl p-5 hover:border-[var(--color-vintage-mint)] transition-all group flex flex-col gap-4 shadow-sm"
           >
              <div class="flex justify-between items-start">
                 <div class="flex items-center gap-3">
                    <div class="w-12 h-12 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] flex items-center justify-center text-[var(--color-vintage-charcoal)] dark:text-[var(--text-main)] shadow-sm">
                       <Cpu class="w-6 h-6 text-[var(--text-muted)] group-hover:text-[var(--color-vintage-mint)] transition-colors" />
                    </div>
                    <div>
                      <p class="font-bold text-[var(--text-main)] text-[16px]">{{ mach.name }}</p>
                      <p class="text-xs text-[var(--text-muted)] uppercase tracking-wider">{{ mach.serial_number }}</p>
                    </div>
                 </div>
                 <span class="px-2.5 py-1 text-[10px] uppercase tracking-wider font-bold rounded-full border shrink-0"
                  :class="{
                    'bg-[var(--color-vintage-mint)]/10 text-[var(--color-vintage-mint)] border-[var(--color-vintage-mint)]/20': mach.status === 'ACTIVE',
                    'bg-[var(--color-vintage-mustard)]/10 text-[var(--color-vintage-mustard)] border-[var(--color-vintage-mustard)]/20': mach.status === 'MAINTENANCE',
                    'bg-[var(--color-vintage-rose)]/10 text-[var(--color-vintage-rose)] border-[var(--color-vintage-rose)]/20': mach.status === 'INACTIVE',
                  }"
                 >
                   {{ formatStatus(mach.status) }}
                 </span>
              </div>
              
              <div class="space-y-2 mt-2">
                 <div class="flex justify-between items-center text-sm">
                    <span class="text-[var(--text-muted)] text-[11px] uppercase font-bold tracking-wider">Fabricante</span>
                    <span class="font-bold text-[var(--text-main)] truncate max-w-[150px] text-right">{{ mach.manufacturer || 'Não catalogado' }}</span>
                 </div>
                 <div class="flex justify-between items-center text-sm">
                    <span class="text-[var(--text-muted)] text-[11px] uppercase font-bold tracking-wider">Modelo</span>
                    <span class="font-bold text-[var(--text-main)] truncate max-w-[150px] text-right">{{ mach.model || 'Sem especificação' }}</span>
                 </div>
                 <div class="flex justify-between items-center text-sm">
                    <span class="text-[var(--text-muted)] text-[11px] uppercase font-bold tracking-wider">Localização</span>
                    <span class="font-bold text-[var(--color-vintage-teal)] dark:text-[var(--color-vintage-mint)] truncate max-w-[150px] text-right">{{ mach.location || 'Sem Definição' }}</span>
                 </div>
              </div>

              <div class="mt-auto pt-4 border-t border-[var(--border-color)] flex gap-2">
                 <button @click.stop="openEditModal(mach)" class="flex-1 flex justify-center items-center gap-1.5 py-2 rounded-lg bg-[var(--bg-card)] hover:bg-[var(--color-vintage-mint)] hover:text-white text-[var(--text-main)] text-xs font-bold transition-colors border border-[var(--border-color)] hover:border-transparent">
                   <Edit3 class="w-3.5 h-3.5" /> Editar
                 </button>
                 <button @click.stop="deleteMachine(mach.id)" class="py-2 px-3 rounded-lg bg-[var(--bg-card)] hover:bg-[var(--color-vintage-rose)]/10 text-[var(--text-muted)] hover:text-[var(--color-vintage-rose)] transition-colors border border-[var(--border-color)] hover:border-[var(--color-vintage-rose)]/30">
                   <Trash2 class="w-4 h-4" />
                 </button>
              </div>
           </div>
        </div>
      </div>


      <!-- Pagination Block -->
      <div class="mt-auto border-t border-[var(--border-color)] bg-[var(--bg-app)]/50 p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p class="text-xs font-bold text-[var(--text-muted)]">
          Mostrando de <span class="text-[var(--text-main)]">{{ paginationStart }}</span> até <span class="text-[var(--text-main)]">{{ paginationEnd }}</span> de <span class="text-[var(--text-main)]">{{ totalItems }}</span> registros
        </p>
        <div class="flex items-center gap-2">
          <button 
            @click="prevPage" 
            :disabled="currentPage === 1"
            class="p-2 border border-[var(--border-color)] rounded-lg text-[var(--text-muted)] hover:bg-[var(--bg-card)] hover:text-[var(--text-main)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
             <ChevronLeft class="w-4 h-4" />
          </button>
          
          <span class="text-xs font-bold px-4 tracking-widest text-[var(--text-main)] border border-transparent">
             {{ currentPage }} / {{ totalPages }}
          </span>

          <button 
            @click="nextPage" 
            :disabled="currentPage === totalPages"
            class="p-2 border border-[var(--border-color)] rounded-lg text-[var(--text-muted)] hover:bg-[var(--bg-card)] hover:text-[var(--text-main)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
             <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- CREATE/EDIT MODAL OVERLAY -->
    <Teleport to="body">
      <div v-if="showModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="closeModal"></div>
        
        <div class="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-3xl w-full max-w-2xl max-h-[90vh] flex flex-col relative z-[101] shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
          
          <!-- Header -->
          <div class="p-6 border-b border-[var(--border-color)] flex justify-between items-center bg-[var(--bg-app)] shrink-0">
            <div>
              <h2 class="text-xl font-bold tracking-tight text-[var(--text-main)]">{{ isEditing ? 'Editar Especificações' : 'Nova Máquina na Planta' }}</h2>
              <p class="text-xs text-[var(--text-muted)] font-bold mt-1">Preencha os dados do equipamento de operação.</p>
            </div>
            <button @click="closeModal" class="p-2 hover:bg-[var(--bg-card)] rounded-lg transition-colors">
              <X class="w-5 h-5 text-[var(--text-muted)]" />
            </button>
          </div>

          <!-- Body Form -->
          <form @submit.prevent="saveMachine" class="p-6 overflow-y-auto flex-1 space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- NOME -->
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Identificação Principal (Nome)*</label>
                <input 
                  v-model="form.name" type="text" required
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                  placeholder="Ex: Torno CNC D-400"
                />
              </div>
              
              <!-- SERIAL -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Nº de Série*</label>
                <input 
                  v-model="form.serial_number" type="text" required
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                  placeholder="ABC-12345"
                />
              </div>

              <!-- STATUS -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Status Operacional</label>
                <select v-model="form.status" class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] font-bold focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors">
                  <option value="ACTIVE">Ativa (Operando)</option>
                  <option value="MAINTENANCE">Manutenção Pendente</option>
                  <option value="INACTIVE">Inativa (Desligada)</option>
                </select>
              </div>

              <!-- MANUFACTURER -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Fabricante</label>
                <input 
                  v-model="form.manufacturer" type="text"
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                  placeholder="Siemens, Bosch, etc."
                />
              </div>

              <!-- MODEL -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Modelo Técnico</label>
                <input 
                  v-model="form.model" type="text"
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                  placeholder="R-X500v2"
                />
              </div>

              <!-- LOCATION -->
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Localização (Setor)</label>
                <input 
                  v-model="form.location" type="text"
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                  placeholder="Setor de Usinagem, Linha de Montagem A"
                />
              </div>

               <!-- DESC -->
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Descrição Adicional / Observações</label>
                <textarea 
                  v-model="form.description" rows="3"
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors resize-none" 
                  placeholder="Observações mecânicas cruciais para o monitoramento..."
                ></textarea>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex gap-4 pt-4 border-t border-[var(--border-color)]">
              <button type="button" @click="closeModal" class="flex-1 py-3 border-2 border-[var(--border-color)] text-[var(--text-muted)] font-bold text-sm rounded-xl hover:bg-[var(--bg-app)] hover:text-[var(--text-main)] transition-colors">
                Cancelar
              </button>
              <button type="submit" class="flex-1 py-3 bg-[var(--color-vintage-mint)] text-white font-bold text-sm rounded-xl shadow-md hover:opacity-90 active:scale-[0.98] transition-all flex justify-center items-center gap-2">
                <Save class="w-4 h-4" />
                {{ isEditing ? 'Salvar Mudanças' : 'Cadastrar Equipamento' }}
              </button>
            </div>
          </form>

        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Search, Plus, Filter, Edit3, Trash2, X, ChevronLeft, ChevronRight, Layers, Cpu, Save, LayoutGrid, List } from 'lucide-vue-next'
import api from '@/services/api'

// ======= STATE =======
const viewMode = ref('table') // 'table' or 'grid'
const machines = ref([])
const totalItems = ref(0)
const loading = ref(true)

// Filters
const searchQuery = ref('')
const statusFilter = ref('')

// Pagination
const currentPage = ref(1)
const pageSize = ref(10)

const totalPages = computed(() => {
  const pages = Math.ceil(totalItems.value / pageSize.value)
  return pages > 0 ? pages : 1
})

const paginationStart = computed(() => ((currentPage.value - 1) * pageSize.value) + (totalItems.value > 0 ? 1 : 0))
const paginationEnd = computed(() => Math.min(currentPage.value * pageSize.value, totalItems.value))

// Modal Form
const showModal = ref(false)
const isEditing = ref(false)
let currentEditingId = null

const emptyForm = {
  name: '',
  serial_number: '',
  model: '',
  manufacturer: '',
  location: '',
  description: '',
  status: 'ACTIVE'
}

const form = ref({ ...emptyForm })


// ======= METHODS =======
const formatStatus = (status) => {
  const map = {
    'ACTIVE': 'Ativa',
    'MAINTENANCE': 'Em Manutenção',
    'INACTIVE': 'Inativa'
  }
  return map[status] || status
}

// Data Fetching
const fetchMachines = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
    }
    
    // Add optional filters
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (statusFilter.value) params.status = statusFilter.value

    const response = await api.get('/machines/', { params })
    
    // Django DRF paginated response format handling
    if (response.data.results) {
      machines.value = response.data.results
      totalItems.value = response.data.count
    } else {
      // Fallback if pagination is globally missing
      machines.value = response.data
      totalItems.value = response.data.length
    }
  } catch (error) {
    console.error('Failed to fetch machines:', error)
    // Fallback UI mock just in case DB is entirely empty or API fails, but we want real connection
  } finally {
    loading.value = false
  }
}

// Actions
const handleSearch = () => {
  currentPage.value = 1
  fetchMachines()
}

const clearSearch = () => {
  searchQuery.value = ''
  handleSearch()
}

const resetPagination = () => {
  currentPage.value = 1
  fetchMachines()
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchMachines()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchMachines()
  }
}

// Modal Logic
const openCreateModal = () => {
  isEditing.value = false
  currentEditingId = null
  form.value = { ...emptyForm }
  showModal.value = true
}

const openEditModal = (machine) => {
  isEditing.value = true
  currentEditingId = machine.id
  form.value = { 
    name: machine.name,
    serial_number: machine.serial_number,
    model: machine.model,
    manufacturer: machine.manufacturer,
    location: machine.location,
    description: machine.description,
    status: machine.status
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

// CRUD Save
const saveMachine = async () => {
  try {
    loading.value = true
    if (isEditing.value) {
      await api.put(`/machines/${currentEditingId}/`, form.value)
    } else {
      await api.post('/machines/', form.value)
    }
    closeModal()
    fetchMachines() // Refresh data intelligently
  } catch (error) {
    console.error('Error saving machine:', error)
    alert('Ocorreu um erro ao salvar o registro desta máquina.') // Simples alert for now
  } finally {
    loading.value = false
  }
}

const deleteMachine = async (id) => {
  if (confirm('Aviso Crítico: Deseja realmente excluir este equipamento do painel corporativo?')) {
    try {
      loading.value = true
      await api.delete(`/machines/${id}/`)
      
       // Smart pagination correction on delete
      if (machines.value.length === 1 && currentPage.value > 1) {
         currentPage.value--
      }
      
      fetchMachines()
    } catch (error) {
      console.error('Error deleting machine:', error)
    } finally {
      loading.value = false
    }
  }
}

// Initial Load
onMounted(() => {
  fetchMachines()
})

</script>
