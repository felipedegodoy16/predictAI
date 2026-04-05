<template>
  <div class="h-full flex flex-col gap-6 relative">
    
    <!-- HEADER -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tighter flex items-center gap-2">
          Gestão de Usuários e Acessos
        </h1>
        <p class="text-[var(--text-muted)] font-medium">Controle de perfis, hierarquias corporativas e permissões integradas.</p>
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
          <UserPlus class="w-5 h-5" />
          Novo Usuário
        </button>
      </div>
    </div>

    <!-- MAIN CONTENT AREA -->
    <div v-if="loading" class="flex-1 flex items-center justify-center min-h-[400px]">
      <div class="flex flex-col items-center gap-4">
        <Loader2 class="w-8 h-8 animate-spin text-[var(--color-vintage-mint)]" />
        <p class="text-[var(--text-muted)] font-bold animate-pulse">Consultando diretório central...</p>
      </div>
    </div>

    <div v-else-if="error" class="flex-1 flex items-center justify-center min-h-[400px]">
      <div class="bg-red-500/10 text-red-500 p-6 rounded-2xl border border-red-500/20 max-w-md text-center">
        <AlertTriangle class="w-10 h-10 mx-auto mb-3" />
        <h3 class="font-bold text-lg mb-1">Falha de Autorização/Rede</h3>
        <p class="text-sm opacity-90">{{ error }}</p>
        <button @click="fetchUsers" class="mt-4 px-4 py-2 bg-red-500 text-white rounded-lg font-bold hover:bg-red-600 transition-colors">
          Tentar Novamente
        </button>
      </div>
    </div>

    <div v-else-if="users.length === 0" class="flex-1 vintage-panel flex flex-col items-center justify-center p-12 text-center min-h-[400px]">
      <div class="w-20 h-20 bg-[var(--bg-app)] rounded-full flex items-center justify-center mb-6">
        <Users class="w-10 h-10 text-[var(--text-muted)]" />
      </div>
      <h2 class="text-2xl font-bold mb-2">Sem usuários na base</h2>
      <button @click="openCreateModal" class="px-6 py-3 rounded-lg border-2 border-[var(--color-vintage-mint)] text-[var(--color-vintage-mint)] font-bold hover:bg-[var(--color-vintage-mint)]/10 transition-colors">
        Adicionar O Primeiro
      </button>
    </div>

    <div v-else class="flex-1 flex flex-col min-h-0">
      
      <!-- GRID VIEW -->
      <div v-if="viewMode === 'grid'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-6 items-start">
        <div v-for="user in users" :key="user.id" class="vintage-panel group relative flex flex-col p-6 h-full hover:-translate-y-1 transition-all duration-300">
          
          <div class="flex justify-between items-start mb-4 relative z-10">
            <div class="w-12 h-12 rounded-xl bg-[var(--color-vintage-mint)]/20 flex items-center justify-center text-[var(--color-vintage-mint)]">
              <span class="font-bold text-xl uppercase">{{ user.name.substring(0,2) }}</span>
            </div>
            
            <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button @click="openEditModal(user)" title="Editar" class="p-1.5 rounded hover:bg-[var(--color-vintage-mustard)]/20 text-[var(--color-vintage-mustard)] transition-colors">
                <Edit3 class="w-4 h-4" />
              </button>
            </div>
            <!-- Indicator for Role -->
            <div class="absolute right-0 top-0 group-hover:hidden">
               <Shield v-if="user.system_role === 'ADMIN'" class="w-5 h-5 text-[var(--color-vintage-rose)]" title="Admin General" />
               <Key v-else-if="user.system_role === 'MANAGER'" class="w-4 h-4 text-[var(--color-vintage-mustard)]" title="Supervisor de Área" />
               <UserCheck v-else class="w-4 h-4 text-[var(--text-muted)]" title="Operação/Técnico" />
            </div>
          </div>

          <div class="mb-4 relative z-10 flex-1">
            <h3 class="text-lg font-bold tracking-tight text-[var(--text-main)] truncate" :title="user.name">{{ user.name }}</h3>
            <p class="text-sm font-medium text-[var(--text-muted)] truncate mt-1">{{ translateCompanyRole(user.company_role) }} • {{ user.department || 'Geral' }}</p>
          </div>

          <div class="space-y-3 mt-auto relative z-10 pt-4 border-t border-[var(--border-color)]">
             <div class="flex items-center gap-2 text-sm text-[var(--text-muted)]">
                <Mail class="w-4 h-4" />
                <span class="truncate">{{ user.email }}</span>
             </div>
             <div class="flex items-center gap-2 text-sm text-[var(--text-muted)]">
                <Phone class="w-4 h-4" />
                <span class="truncate">{{ user.phone || 'Nenhum' }}</span>
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
                <th class="p-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Identificação</th>
                <th class="p-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Cargo & Departamento</th>
                <th class="p-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Permissão (Tier)</th>
                <th class="p-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider text-right">Controles</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--border-color)]">
              <tr v-for="user in users" :key="user.id" class="hover:bg-[var(--bg-app)]/30 transition-colors group">
                <td class="p-4">
                  <div class="flex items-center gap-3">
                     <div class="w-10 h-10 rounded-lg bg-[var(--color-vintage-mint)]/10 flex items-center justify-center text-[var(--color-vintage-mint)] shrink-0 font-bold uppercase">
                      {{ user.name.substring(0,2) }}
                    </div>
                    <div>
                      <p class="font-bold text-sm text-[var(--text-main)]">{{ user.name }}</p>
                      <p class="text-xs text-[var(--text-muted)] font-medium">{{ user.email }}</p>
                    </div>
                  </div>
                </td>
                <td class="p-4">
                  <p class="font-bold text-sm text-[var(--text-main)]">{{ translateCompanyRole(user.company_role) }}</p>
                  <p class="text-xs text-[var(--text-muted)]">{{ user.department || 'Nenhum' }}</p>
                </td>
                <td class="p-4">
                   <div class="flex items-center gap-1.5 font-bold text-xs uppercase" :class="getSystemRoleClass(user.system_role)">
                      <Shield v-if="user.system_role === 'ADMIN'" class="w-3.5 h-3.5" />
                      <Key v-else-if="user.system_role === 'MANAGER'" class="w-3.5 h-3.5" />
                      <UserCheck v-else class="w-3.5 h-3.5" />
                      {{ user.system_role }}
                   </div>
                </td>
                <td class="p-4 text-right">
                  <div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button @click="openEditModal(user)" class="p-2 hover:bg-[var(--color-vintage-mustard)]/10 text-[var(--color-vintage-mustard)] rounded-lg transition-colors">
                      <Edit3 class="w-4 h-4" />
                    </button>
                    <!-- Somente exemplo visual ou funcional se API permitir deletar. Normalmente usuários são "desativados", mas para crud livre: -->
                    <button @click="deleteUser(user.id)" class="p-2 hover:bg-[var(--color-vintage-rose)]/10 text-[var(--color-vintage-rose)] rounded-lg transition-colors">
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
              <h2 class="text-xl font-bold tracking-tight text-[var(--text-main)]">{{ isEditing ? 'Editar Perfil de Acesso' : 'Admissão de Colaborador na Plataforma' }}</h2>
              <p class="text-xs text-[var(--text-muted)] font-bold mt-1">Insira os metadados pessoais e permissões operacionais estritas.</p>
            </div>
            <button @click="closeModal" class="p-2 hover:bg-[var(--bg-card)] rounded-lg transition-colors">
              <X class="w-5 h-5 text-[var(--text-muted)]" />
            </button>
          </div>

          <!-- Body Form -->
          <form @submit.prevent="saveUser" class="p-6 overflow-y-auto flex-1 space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              <!-- NOME -->
              <div class="col-span-1 md:col-span-2">
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Nome Completo do Funcionário*</label>
                <input 
                  v-model="form.name" type="text" required
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                  placeholder="Ex: Ana Luísa Moreira"
                />
              </div>
              
              <!-- CPF -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">CPF*</label>
                <input 
                  v-model="form.cpf" type="text" required maxlength="14"
                  @input="handleCpfInput"
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                  placeholder="000.000.000-00"
                />
              </div>

               <!-- E-MAIL -->
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Endereço de E-mail Corporativo*</label>
                <input 
                  v-model="form.email" type="email" required
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                  placeholder="ana.moreira@empresa.com"
                />
              </div>
              
              <!-- PASSWORD E CONFIRM (Apenas Criação ou Troca Forçada) -->
              <div v-if="!isEditing" class="col-span-1">
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Senha Inicial de Autenticação*</label>
                <input 
                  v-model="form.password" type="password" :required="!isEditing"
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                  placeholder="Mínimo de 8 caracteres"
                />
                <p class="text-xs text-[var(--text-muted)] mt-1 opacity-70">Sua senha deve ser segura.</p>
              </div>
              
              <div v-if="!isEditing" class="col-span-1">
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Confirmar Senha*</label>
                <input 
                  v-model="form.password_confirm" type="password" :required="!isEditing"
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-rose)] transition-colors" 
                  placeholder="Repita a senha"
                />
              </div>

              <!-- HIERARQUIA CORPORATIVA -->
              <div class="col-span-1 border-t border-[var(--border-color)] pt-4 mt-2">
                 <h4 class="text-sm font-bold text-[var(--text-main)] mb-4 flex items-center gap-2">
                    <Briefcase class="w-4 h-4 text-[var(--color-vintage-mustard)]" />
                    Papel Corporativo
                 </h4>
                 
                 <div class="space-y-4">
                     <div>
                        <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Setor / Departamento</label>
                        <input 
                        v-model="form.department" type="text"
                        class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mustard)] transition-colors" 
                        placeholder="Ex: Engenharia Reversa"
                        />
                     </div>
                     <div>
                        <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Cargo Nominal</label>
                        <select v-model="form.company_role" class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] font-bold focus:outline-none focus:border-[var(--color-vintage-mustard)] transition-colors">
                        <option value="OPERATOR">Operador(a)</option>
                        <option value="TECHNICIAN">Técnico(a) Manutenção</option>
                        <option value="ANALYST">Analista</option>
                        <option value="MANAGER">Gerente Setorial</option>
                        <option value="DIRECTOR">Conselho/Diretor</option>
                        <option value="INTERN">Estagiário(a)</option>
                        </select>
                     </div>
                 </div>
              </div>

              <!-- PERMISSÕES SISTÊMICAS -->
              <div class="col-span-1 border-t border-[var(--border-color)] pt-4 mt-2">
                 <h4 class="text-sm font-bold text-[var(--text-main)] mb-4 flex items-center gap-2">
                    <ShieldCheck class="w-4 h-4 text-[var(--color-vintage-mint)]" />
                    Permissão Sistêmica (PredictAI)
                 </h4>

                 <div class="space-y-4">
                     <div>
                        <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Nível de Acesso*</label>
                        <select v-model="form.system_role" required class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] font-bold focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors">
                           <option value="TECHNICIAN">Básico (Apenas Leitura & Alertas)</option>
                           <option value="MANAGER">Gestor (Adicionar Equipamentos)</option>
                           <option value="ADMIN">Administrador DBO (Full)</option>
                        </select>
                     </div>
                     <div>
                        <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Telefone / Rádio</label>
                        <input 
                        v-model="form.phone" type="text" maxlength="15"
                        @input="handlePhoneInput"
                        class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                        placeholder="(11) 90000-0000"
                        />
                     </div>
                 </div>
              </div>

            </div>

            <!-- Actions -->
            <div class="flex gap-4 pt-6 border-t border-[var(--border-color)]">
              <button type="button" @click="closeModal" class="flex-1 py-3 border-2 border-[var(--border-color)] text-[var(--text-muted)] font-bold text-sm rounded-xl hover:bg-[var(--bg-app)] hover:text-[var(--text-main)] transition-colors">
                Cancelar
              </button>
              <button type="submit" class="flex-1 py-3 bg-[var(--color-vintage-mint)] text-white font-bold text-sm rounded-xl shadow-md hover:opacity-90 active:scale-[0.98] transition-all flex justify-center items-center gap-2">
                <Save class="w-4 h-4" />
                {{ isEditing ? 'Aplicar Mudanças' : 'Registrar Usuário' }}
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
import { UserPlus, X, Loader2, Edit3, Trash2, AlertTriangle, Users, Save, Phone, Mail, LayoutGrid, List, Shield, Key, UserCheck, Briefcase, ShieldCheck } from 'lucide-vue-next'
import api from '../services/api'

const users = ref([])
const loading = ref(true)
const error = ref(null)
const showModal = ref(false)
const isEditing = ref(false)
const viewMode = ref('list')

const applyCpfMask = (value) => {
  let v = value.replace(/\D/g, '')
  if (v.length > 11) v = v.substring(0, 11)
  
  if (v.length <= 3) return v
  if (v.length <= 6) return `${v.substring(0, 3)}.${v.substring(3)}`
  if (v.length <= 9) return `${v.substring(0, 3)}.${v.substring(3, 6)}.${v.substring(6)}`
  return `${v.substring(0, 3)}.${v.substring(3, 6)}.${v.substring(6, 9)}-${v.substring(9)}`
}

const applyPhoneMask = (value) => {
  let v = value.replace(/\D/g, '')
  if (v.length > 11) v = v.substring(0, 11)
  
  if (v.length === 0) return ''
  if (v.length <= 2) return `(${v}`
  if (v.length <= 6) return `(${v.substring(0, 2)}) ${v.substring(2)}`
  if (v.length <= 10) return `(${v.substring(0, 2)}) ${v.substring(2, 6)}-${v.substring(6)}`
  return `(${v.substring(0, 2)}) ${v.substring(2, 7)}-${v.substring(7)}`
}

const handleCpfInput = (e) => {
  form.value.cpf = applyCpfMask(e.target.value)
}

const handlePhoneInput = (e) => {
  form.value.phone = applyPhoneMask(e.target.value)
}

const defaultForm = {
  id: null,
  name: '',
  cpf: '',
  email: '',
  password: '', 
  password_confirm: '',
  phone: '',
  department: '',
  system_role: 'TECHNICIAN',
  company_role: 'OPERATOR'
}

const form = ref({ ...defaultForm })

const fetchUsers = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await api.get('users/')
    users.value = response.data.results || response.data
  } catch (err) {
    if (err.response && err.response.status === 403) {
       error.value = 'Acesso Negado: Apenas supervisores e administradores podem listar o diretório completo de usuários.'
    } else {
       error.value = 'Incapaz de extrair as instâncias dos usuários. Verifique com a central.'
    }
  } finally {
    loading.value = false
  }
}

const translateCompanyRole = (role) => {
  const map = {
    'ADMIN': 'Administrador Geral',
    'MANAGER': 'Gerente Setorial',
    'ANALYST': 'Analista de Operações',
    'INTERN': 'Escalonador / Estagiário',
    'DIRECTOR': 'Corpo Diretor',
    'TECHNICIAN': 'Corpo Técnico Preditivo',
    'OPERATOR': 'Operador Fabril'
  }
  return map[role] || role
}

const getSystemRoleClass = (role) => {
   if (role === 'ADMIN') return 'text-[var(--color-vintage-rose)]'
   if (role === 'MANAGER') return 'text-[var(--color-vintage-mustard)]'
   return 'text-[var(--text-muted)]'
}

const openCreateModal = () => {
  isEditing.value = false
  form.value = { ...defaultForm }
  showModal.value = true
}

const openEditModal = (userPayload) => {
  isEditing.value = true
  // omitimos a senha aqui pro form não ficar maluco
  const { password, password_confirm, ...safeUser } = userPayload
  form.value = { ...defaultForm, ...safeUser }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const saveUser = async () => {
  try {
    const payload = { ...form.value }
    if (isEditing.value) {
       delete payload.password 
       delete payload.password_confirm
       await api.put(`users/${payload.id}/`, payload)
    } else {
       // Na criação envia todos
       if (payload.password !== payload.password_confirm) {
           alert("As senhas não conferem!")
           return
       }
       payload.username = payload.email
       await api.post('users/', payload)
    }
    
    closeModal()
    fetchUsers()
  } catch (err) {
    console.error(err)
    const errorMsg = err.response?.data?.detail || 
                     err.response?.data?.password_confirm?.[0] || 
                     err.response?.data?.username?.[0] ||
                     err.response?.data?.cpf?.[0] ||
                     err.response?.data?.email?.[0] ||
                     (err.response?.data ? JSON.stringify(err.response.data) : 'Erro desconhecido ao salvar os dados.')
    alert(`Erro ao salvar: ${errorMsg}`)
  }
}

const deleteUser = async (id) => {
  if (confirm('Ação destrutiva identificada! Expurgar esta credencial? Este colaborador não fará mais parte da arquitetura!')) {
    try {
      await api.delete(`users/${id}/`)
      fetchUsers()
    } catch (err) {
      alert('A exclusão falhou. Pode ser restrição de hierarquia.')
    }
  }
}

onMounted(() => {
  fetchUsers()
})
</script>
