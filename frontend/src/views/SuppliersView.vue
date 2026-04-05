<template>
  <div class="h-full flex flex-col gap-6 relative">
    
    <!-- HEADER -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tighter flex items-center gap-2">
          Gestão de Fornecedores
        </h1>
        <p class="text-[var(--text-muted)] font-medium">Controle de contatos, fabricantes e prestadores de suprimentos.</p>
      </div>
      
      <div class="flex items-center gap-3 w-full md:w-auto">
        <!-- View Toggle Controls -->
        <div class="bg-[var(--bg-card)] border border-[var(--border-color)] p-1 rounded-xl flex shadow-sm shrink-0">
          <button 
            @click="viewMode = 'grid'" 
            class="p-2 rounded-lg transition-all focus:outline-none"
            :class="viewMode === 'grid' ? 'bg-[var(--bg-app)] text-[var(--color-vintage-mint)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'"
            title="Visualização em Cards"
          >
            <LayoutGrid class="w-5 h-5" />
          </button>
          <button 
            @click="viewMode = 'list'" 
            class="p-2 rounded-lg transition-all focus:outline-none"
            :class="viewMode === 'list' ? 'bg-[var(--bg-app)] text-[var(--color-vintage-mint)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'"
            title="Visualização em Lista"
          >
            <List class="w-5 h-5" />
          </button>
        </div>

        <button 
          @click="openCreateModal"
          class="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-[var(--color-vintage-charcoal)] dark:bg-[var(--color-vintage-paper)] text-[var(--color-vintage-cream)] dark:text-[var(--color-vintage-charcoal)] font-bold shadow-md hover:-translate-y-0.5 transition-transform"
        >
          <Plus class="w-5 h-5" />
          Novo Fornecedor
        </button>
      </div>
    </div>

    <!-- MAIN CONTENT AREA -->
    <div v-if="loading" class="flex-1 flex items-center justify-center min-h-[400px]">
      <div class="flex flex-col items-center gap-4">
        <Loader2 class="w-8 h-8 animate-spin text-[var(--color-vintage-mint)]" />
        <p class="text-[var(--text-muted)] font-bold animate-pulse">Sincronizando contatos...</p>
      </div>
    </div>

    <div v-else-if="error" class="flex-1 flex items-center justify-center min-h-[400px]">
      <div class="bg-red-500/10 text-red-500 p-6 rounded-2xl border border-red-500/20 max-w-md text-center">
        <AlertTriangle class="w-10 h-10 mx-auto mb-3" />
        <h3 class="font-bold text-lg mb-1">Falha na Comunicação</h3>
        <p class="text-sm opacity-90">{{ error }}</p>
        <button @click="fetchSuppliers" class="mt-4 px-4 py-2 bg-red-500 text-white rounded-lg font-bold hover:bg-red-600 transition-colors">
          Tentar Novamente
        </button>
      </div>
    </div>

    <div v-else-if="suppliers.length === 0" class="flex-1 vintage-panel flex flex-col items-center justify-center p-12 text-center min-h-[400px]">
      <div class="w-20 h-20 bg-[var(--bg-app)] rounded-full flex items-center justify-center mb-6">
        <Truck class="w-10 h-10 text-[var(--text-muted)]" />
      </div>
      <h2 class="text-2xl font-bold mb-2">Nenhum fornecedor registrado</h2>
      <p class="text-[var(--text-muted)] mb-6 max-w-md">O banco de dados de suprimentos e serviços está vazio no momento.</p>
      <button @click="openCreateModal" class="px-6 py-3 rounded-lg border-2 border-[var(--color-vintage-mint)] text-[var(--color-vintage-mint)] font-bold hover:bg-[var(--color-vintage-mint)]/10 transition-colors">
        Cadastrar Primeiro Fornecedor
      </button>
    </div>

    <div v-else class="flex-1 flex flex-col min-h-0">
      
      <!-- GRID VIEW -->
      <div v-if="viewMode === 'grid'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-6 items-start">
        <div v-for="supplier in suppliers" :key="supplier.id" class="vintage-panel group relative flex flex-col p-6 h-full hover:-translate-y-1 transition-all duration-300">
          
          <div class="flex justify-between items-start mb-4 relative z-10">
            <div class="w-12 h-12 rounded-xl bg-[var(--color-vintage-mint)]/20 flex items-center justify-center text-[var(--color-vintage-mint)]">
              <Truck class="w-6 h-6" />
            </div>
            
            <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button @click="openEditModal(supplier)" title="Editar" class="p-1.5 rounded hover:bg-[var(--color-vintage-mustard)]/20 text-[var(--color-vintage-mustard)] transition-colors">
                <Edit3 class="w-4 h-4" />
              </button>
              <button @click="deleteSupplier(supplier.id)" title="Deletar" class="p-1.5 rounded hover:bg-[var(--color-vintage-rose)]/20 text-[var(--color-vintage-rose)] transition-colors">
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
            <!-- If not hovered but active state needed -->
            <div class="absolute right-0 top-0 group-hover:hidden">
               <span class="inline-flex w-3 h-3 rounded-full" :class="supplier.is_active ? 'bg-[var(--color-vintage-mint)]' : 'bg-[var(--text-muted)]'"></span>
            </div>
          </div>

          <div class="mb-4 relative z-10 flex-1">
            <h3 class="text-lg font-bold tracking-tight text-[var(--text-main)] truncate" :title="supplier.name">{{ supplier.name }}</h3>
            <p class="text-sm font-medium text-[var(--text-muted)] truncate mt-1">CNPJ: {{ supplier.cnpj }}</p>
          </div>

          <div class="space-y-3 mt-auto relative z-10 pt-4 border-t border-[var(--border-color)]">
             <div class="flex items-center gap-2 text-sm text-[var(--text-muted)]">
                <Mail class="w-4 h-4" />
                <span class="truncate">{{ supplier.email || 'Sem e-mail' }}</span>
             </div>
             <div class="flex items-center gap-2 text-sm text-[var(--text-muted)]">
                <Phone class="w-4 h-4" />
                <span class="truncate">{{ supplier.phone || 'Sem telefone' }}</span>
             </div>
             <div class="flex items-center gap-2 text-sm text-[var(--text-muted)]">
                <User class="w-4 h-4" />
                <span class="truncate">{{ supplier.contact_name || 'Sem contato' }}</span>
             </div>
          </div>
        </div>
      </div>

      <!-- LIST VIEW -->
      <div v-else class="vintage-panel flex-1 overflow-hidden flex flex-col">
        <div class="overflow-x-auto flex-1">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-[var(--border-color)] bg-[var(--bg-app)]/50">
                <th class="p-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Fornecedor</th>
                <th class="p-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Contato Principal</th>
                <th class="p-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Localidade</th>
                <th class="p-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Status</th>
                <th class="p-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider text-right">Ações</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--border-color)]">
              <tr v-for="supplier in suppliers" :key="supplier.id" class="hover:bg-[var(--bg-app)]/30 transition-colors group">
                <td class="p-4">
                  <div class="flex items-center gap-3">
                     <div class="w-10 h-10 rounded-lg bg-[var(--color-vintage-mint)]/10 flex items-center justify-center text-[var(--color-vintage-mint)] shrink-0">
                      <Truck class="w-5 h-5" />
                    </div>
                    <div>
                      <p class="font-bold text-sm text-[var(--text-main)]">{{ supplier.name }}</p>
                      <p class="text-xs text-[var(--text-muted)] font-medium">CNPJ: {{ supplier.cnpj }}</p>
                    </div>
                  </div>
                </td>
                <td class="p-4">
                  <p class="font-bold text-sm text-[var(--text-main)]">{{ supplier.contact_name || '-' }}</p>
                  <p class="text-xs text-[var(--text-muted)]">{{ supplier.email || '-' }}</p>
                </td>
                <td class="p-4">
                  <p class="text-sm font-medium text-[var(--text-main)]">{{ supplier.city || '-' }} / {{ supplier.state || '-' }}</p>
                </td>
                <td class="p-4">
                  <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider"
                        :class="supplier.is_active ? 'bg-[var(--color-vintage-mint)]/10 text-[var(--color-vintage-mint)]' : 'bg-[var(--text-muted)]/10 text-[var(--text-muted)]'">
                    <span class="w-1.5 h-1.5 rounded-full" :class="supplier.is_active ? 'bg-[var(--color-vintage-mint)]' : 'bg-[var(--text-muted)]'"></span>
                    {{ supplier.is_active ? 'Ativo' : 'Inativo' }}
                  </span>
                </td>
                <td class="p-4 text-right">
                  <div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button @click="openEditModal(supplier)" class="p-2 hover:bg-[var(--color-vintage-mustard)]/10 text-[var(--color-vintage-mustard)] rounded-lg transition-colors">
                      <Edit3 class="w-4 h-4" />
                    </button>
                    <button @click="deleteSupplier(supplier.id)" class="p-2 hover:bg-[var(--color-vintage-rose)]/10 text-[var(--color-vintage-rose)] rounded-lg transition-colors">
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
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
              <h2 class="text-xl font-bold tracking-tight text-[var(--text-main)]">{{ isEditing ? 'Editar Fornecedor' : 'Novo Fornecedor' }}</h2>
              <p class="text-xs text-[var(--text-muted)] font-bold mt-1">Insira os dados cadastrais da empresa e contatos associados.</p>
            </div>
            <button @click="closeModal" class="p-2 hover:bg-[var(--bg-card)] rounded-lg transition-colors">
              <X class="w-5 h-5 text-[var(--text-muted)]" />
            </button>
          </div>

          <!-- Body Form -->
          <form @submit.prevent="saveSupplier" class="p-6 overflow-y-auto flex-1 space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              <!-- NOME -->
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Razão Social / Nome Fantasia*</label>
                <input 
                  v-model="form.name" type="text" required
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                  placeholder="Ex: Indústrias Metalúrgicas S.A."
                />
              </div>
              
              <!-- CNPJ -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">CNPJ*</label>
                <input 
                  v-model="form.cnpj" type="text" required
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                  placeholder="00.000.000/0000-00"
                />
              </div>

              <!-- STATUS -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Atividade</label>
                <select v-model="form.is_active" class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] font-bold focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors">
                  <option :value="true">Ativo (Homologado)</option>
                  <option :value="false">Inativo (Bloqueado)</option>
                </select>
              </div>

               <!-- CONTATO RESPONSAVEL -->
              <div class="col-span-1 md:col-span-2 border-t border-[var(--border-color)] pt-4 mt-2">
                 <h4 class="text-sm font-bold text-[var(--text-main)] mb-4 flex items-center gap-2">
                    <User class="w-4 h-4 text-[var(--color-vintage-mint)]" />
                    Agente Relacional (Key Account)
                 </h4>
              </div>

              <!-- NOME CONTATO -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Nome do Contato</label>
                <input 
                  v-model="form.contact_name" type="text"
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                  placeholder="Ex: Carlos Silva"
                />
              </div>

               <!-- EMAIL CONTATO -->
               <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">E-mail Principal</label>
                <input 
                  v-model="form.email" type="email"
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                  placeholder="carlos@empresa.com"
                />
              </div>

              <!-- TELEFONE -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Telefone/WhatsApp</label>
                <input 
                  v-model="form.phone" type="text"
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                  placeholder="(11) 90000-0000"
                />
              </div>
              
              <!-- CIDADE/ESTADO -->
              <div class="flex gap-4">
                 <div class="flex-1">
                    <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Cidade</label>
                    <input 
                    v-model="form.city" type="text"
                    class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                    placeholder="Campinas"
                    />
                 </div>
                 <div class="w-1/3">
                    <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">UF</label>
                    <input 
                    v-model="form.state" type="text" maxlength="2"
                    class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors text-center uppercase" 
                    placeholder="SP"
                    />
                 </div>
              </div>

               <!-- DESC -->
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Anotações Relevantes / Acordos</label>
                <textarea 
                  v-model="form.description" rows="2"
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors resize-none" 
                  placeholder="Prazo médio de entrega, contratos atrelados, ressalvas..."
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
                {{ isEditing ? 'Salvar Mudanças' : 'Cadastrar Fornecedor' }}
              </button>
            </div>
          </form>

        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, X, Search, Loader2, Edit3, Trash2, AlertTriangle, Truck, Save, Phone, Mail, User, LayoutGrid, List } from 'lucide-vue-next'
import api from '../services/api'

const suppliers = ref([])
const loading = ref(true)
const error = ref(null)
const showModal = ref(false)
const isEditing = ref(false)
const viewMode = ref('list') // 'list' ou 'grid'

const defaultForm = {
  id: null,
  name: '',
  cnpj: '',
  email: '',
  phone: '',
  city: '',
  state: '',
  contact_name: '',
  description: '',
  is_active: true
}

const form = ref({ ...defaultForm })

const fetchSuppliers = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await api.get('suppliers/')
    suppliers.value = response.data.results || response.data
  } catch (err) {
    error.value = 'Houve um erro ao carregar o diretório de fornecedores. Verifique sua conexão.'
    console.error('Fetch error:', err)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  isEditing.value = false
  form.value = { ...defaultForm }
  showModal.value = true
}

const openEditModal = (supplier) => {
  isEditing.value = true
  form.value = { ...supplier }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const saveSupplier = async () => {
  try {
    if (isEditing.value) {
      await api.put(`suppliers/${form.value.id}/`, form.value)
    } else {
      await api.post('suppliers/', form.value)
    }
    closeModal()
    fetchSuppliers()
  } catch (err) {
    alert('Ops! Ocorreu um erro ao salvar os dados do fornecedor. Cheque os dados e tente novamente.')
    console.error('Save error:', err)
  }
}

const deleteSupplier = async (id) => {
  if (confirm('Tem absoluta certeza que deseja remover este fornecedor permanentemente do sistema?')) {
    try {
      await api.delete(`suppliers/${id}/`)
      fetchSuppliers()
    } catch (err) {
      alert('Erro ao excluir o fornecedor selecionado.')
      console.error('Delete error:', err)
    }
  }
}

onMounted(() => {
  fetchSuppliers()
})
</script>
