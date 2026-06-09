<template>
  <div class="h-full flex flex-col gap-6 relative">
    
    <!-- HEADER -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tighter flex items-center gap-2">
          Gestão de Usuários
        </h1>
        <p class="text-[var(--text-muted)] font-medium">Crie, edite e gerencie os acessos ao sistema PredictAI.</p>
      </div>
      <button 
        v-if="authStore.isAdmin"
        @click="openCreateModal"
        class="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[var(--color-vintage-mint)] text-white font-bold shadow-md hover:-translate-y-0.5 transition-transform"
      >
        <UserPlus class="w-5 h-5" />
        Novo Usuário
      </button>
    </div>

    <!-- Stats Bar -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div v-for="stat in statsCards" :key="stat.label" class="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-4 flex items-center gap-3">
        <div class="p-2 rounded-lg" :class="stat.iconBg">
          <component :is="stat.icon" class="w-5 h-5" :class="stat.iconColor" />
        </div>
        <div>
          <p class="text-2xl font-bold text-[var(--text-main)]">{{ stat.value }}</p>
          <p class="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">{{ stat.label }}</p>
        </div>
      </div>
    </div>

    <!-- Filters & Search Toolbar -->
    <div class="flex flex-col md:flex-row gap-4 items-center justify-between">
      
      <!-- Search Input -->
      <div class="flex-1 w-full relative">
        <label for="search" class="sr-only">Pesquisar</label>
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search class="w-5 h-5 text-[var(--text-muted)]" />
        </div>
        <input 
          id="search"
          v-model="searchQuery"
          type="text" 
          placeholder="Pesquisar por nome ou email..." 
          class="w-full max-w-md pl-10 pr-10 py-2.5 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl text-sm focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors text-[var(--text-main)] font-medium shadow-sm"
        />
        <button 
          v-if="searchQuery" 
          @click="searchQuery = ''"
          class="absolute inset-y-0 cursor-pointer right-0 pr-3 flex items-center text-[var(--text-muted)] hover:text-[var(--text-main)]"
        >
          <X class="w-4 h-4 ml-2" />
        </button>
      </div>

      <!-- Profile Filter + View Toggle -->
      <div class="flex items-center gap-3 w-full md:w-auto mt-2 md:mt-0">
        <!-- Profile filter -->
        <select 
          v-model="profileFilter"
          class="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl py-2.5 px-3 text-sm font-bold text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] shadow-sm"
        >
          <option value="">Todos os perfis</option>
          <option value="administrador">Administrador</option>
          <option value="gerente">Gerente</option>
          <option value="tecnico">Técnico</option>
          <option value="operador">Operador</option>
          <option value="visualizador">Visualizador</option>
        </select>

        <!-- View Toggle -->
        <div class="bg-[var(--bg-card)] border border-[var(--border-color)] p-1 rounded-xl flex items-center shadow-sm shrink-0">
          <button 
            @click="viewMode = 'list'" 
            class="w-8 h-8 rounded-lg transition-all focus:outline-none flex items-center justify-center"
            :class="viewMode === 'list' ? 'bg-[var(--bg-app)] text-[var(--color-vintage-mint)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'"
            title="Lista"
          >
            <List class="w-5 h-5" />
          </button>
          <button 
            @click="viewMode = 'grid'" 
            class="w-8 h-8 rounded-lg transition-all focus:outline-none flex items-center justify-center"
            :class="viewMode === 'grid' ? 'bg-[var(--bg-app)] text-[var(--color-vintage-mint)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'"
            title="Cards"
          >
            <LayoutGrid class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>

    <!-- MAIN CONTENT AREA -->
    <div v-if="loading" class="flex-1 flex items-center justify-center min-h-[300px]">
      <div class="flex flex-col items-center gap-4">
        <Loader2 class="w-8 h-8 animate-spin text-[var(--color-vintage-mint)]" />
        <p class="text-[var(--text-muted)] font-bold animate-pulse">Carregando usuários...</p>
      </div>
    </div>

    <div v-else-if="error" class="flex-1 flex items-center justify-center min-h-[300px]">
      <div class="bg-red-500/10 text-red-500 p-6 rounded-2xl border border-red-500/20 max-w-md text-center">
        <AlertTriangle class="w-10 h-10 mx-auto mb-3" />
        <h3 class="font-bold text-lg mb-1">Falha ao carregar</h3>
        <p class="text-sm opacity-90">{{ error }}</p>
        <button @click="fetchUsers" class="mt-4 px-4 py-2 bg-red-500 text-white rounded-lg font-bold hover:bg-red-600 transition-colors">
          Tentar Novamente
        </button>
      </div>
    </div>

    <div v-else-if="users.length === 0" class="flex-1 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl flex flex-col items-center justify-center p-12 text-center min-h-[300px]">
      <div class="w-20 h-20 bg-[var(--bg-app)] rounded-full flex items-center justify-center mb-6">
        <Users class="w-10 h-10 text-[var(--text-muted)]" />
      </div>
      <h2 class="text-2xl font-bold mb-2">Nenhum usuário cadastrado</h2>
      <button v-if="authStore.isAdmin" @click="openCreateModal" class="mt-4 px-6 py-3 rounded-xl border-2 border-[var(--color-vintage-mint)] text-[var(--color-vintage-mint)] font-bold hover:bg-[var(--color-vintage-mint)]/10 transition-colors">
        Criar o Primeiro Usuário
      </button>
    </div>

    <div v-else class="flex-1 flex flex-col min-h-0">

      <div v-if="filteredUsers.length === 0" class="flex-1 flex flex-col items-center justify-center p-8 text-[var(--text-muted)]">
        <p class="font-bold text-lg mb-1">Nenhum usuário encontrado</p>
        <p class="text-sm">Tente ajustar os filtros.</p>
        <button @click="searchQuery = ''; profileFilter = ''" class="mt-4 px-4 py-2 bg-[var(--bg-card)] hover:bg-[var(--border-color)] text-sm font-medium rounded-lg transition-colors border border-[var(--border-color)]">
          Limpar Filtros
        </button>
      </div>
      
      <!-- GRID VIEW -->
      <div v-else-if="viewMode === 'grid'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5 pb-6 items-start">
        <div 
          v-for="user in filteredUsers" 
          :key="user.id" 
          class="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl group relative flex flex-col p-5 hover:-translate-y-1 hover:shadow-lg hover:border-[var(--color-vintage-mint)]/40 transition-all duration-300"
          :class="{ 'opacity-60': !user.is_active }"
        >
          <!-- Status ativo/inativo -->
          <div class="absolute top-4 right-4">
            <span 
              class="w-2.5 h-2.5 rounded-full inline-block"
              :class="user.is_active ? 'bg-green-400' : 'bg-red-400'"
              :title="user.is_active ? 'Ativo' : 'Inativo'"
            ></span>
          </div>

          <!-- Avatar + Actions -->
          <div class="flex items-start gap-3 mb-4">
            <div class="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold text-lg uppercase shrink-0" :class="avatarBg(user.profile)">
              {{ user.name.substring(0, 2) }}
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="font-bold text-[var(--text-main)] truncate leading-tight">{{ user.name }}</h3>
              <p class="text-xs text-[var(--text-muted)] truncate mt-0.5">{{ user.email }}</p>
            </div>
          </div>

          <!-- Badge de perfil -->
          <div class="mb-4">
            <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold" :class="profileBadgeClass(user.profile)">
              <component :is="profileIcon(user.profile)" class="w-3.5 h-3.5" />
              {{ profileLabel(user.profile) }}
            </span>
          </div>

          <!-- Info extra -->
          <div class="text-xs text-[var(--text-muted)] space-y-1 mt-auto pt-3 border-t border-[var(--border-color)]">
            <div class="flex items-center gap-1.5">
              <CalendarDays class="w-3.5 h-3.5 shrink-0" />
              Desde {{ formatDate(user.created_at) }}
            </div>
          </div>

          <!-- Actions hover -->
          <div v-if="authStore.isAdmin" class="mt-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button @click="openEditModal(user)" class="flex-1 py-1.5 text-xs font-bold text-[var(--text-muted)] hover:text-[var(--color-vintage-mint)] bg-[var(--bg-app)] hover:bg-[var(--color-vintage-mint)]/10 border border-[var(--border-color)] rounded-lg transition-colors flex items-center justify-center gap-1">
              <Edit3 class="w-3.5 h-3.5" /> Editar
            </button>
            <button @click="toggleActive(user)" class="flex-1 py-1.5 text-xs font-bold rounded-lg border transition-colors flex items-center justify-center gap-1"
              :class="user.is_active 
                ? 'text-[var(--color-vintage-rose)] hover:bg-[var(--color-vintage-rose)]/10 border-[var(--color-vintage-rose)]/30'
                : 'text-green-500 hover:bg-green-500/10 border-green-500/30'"
            >
              <component :is="user.is_active ? UserX : UserCheck" class="w-3.5 h-3.5" />
              {{ user.is_active ? 'Desativar' : 'Ativar' }}
            </button>
          </div>
        </div>
      </div>

      <!-- LIST VIEW -->
      <div v-else class="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl flex-1 overflow-hidden flex flex-col">
        <div class="overflow-x-auto flex-1">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-[var(--border-color)] bg-[var(--bg-app)]/50">
                <th class="p-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Usuário</th>
                <th class="p-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Perfil</th>
                <th class="p-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Status</th>
                <th class="p-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Criado em</th>
                <th v-if="authStore.isAdmin" class="p-4 text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider text-right">Ações</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--border-color)]">
              <tr 
                v-for="user in filteredUsers" 
                :key="user.id" 
                class="hover:bg-[var(--bg-app)]/30 transition-colors group"
                :class="{ 'opacity-60': !user.is_active }"
              >
                <td class="p-4">
                  <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-lg flex items-center justify-center text-white font-bold text-sm uppercase shrink-0" :class="avatarBg(user.profile)">
                      {{ user.name.substring(0, 2) }}
                    </div>
                    <div>
                      <p class="font-bold text-sm text-[var(--text-main)]">{{ user.name }}</p>
                      <p class="text-xs text-[var(--text-muted)] font-medium">{{ user.email }}</p>
                    </div>
                  </div>
                </td>
                <td class="p-4">
                  <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold" :class="profileBadgeClass(user.profile)">
                    <component :is="profileIcon(user.profile)" class="w-3.5 h-3.5" />
                    {{ profileLabel(user.profile) }}
                  </span>
                </td>
                <td class="p-4">
                  <span class="inline-flex items-center gap-1.5 text-xs font-bold" :class="user.is_active ? 'text-green-500' : 'text-red-400'">
                    <span class="w-2 h-2 rounded-full" :class="user.is_active ? 'bg-green-400' : 'bg-red-400'"></span>
                    {{ user.is_active ? 'Ativo' : 'Inativo' }}
                  </span>
                </td>
                <td class="p-4 text-sm text-[var(--text-muted)] font-medium">{{ formatDate(user.created_at) }}</td>
                <td v-if="authStore.isAdmin" class="p-4 text-right">
                  <div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button @click="openEditModal(user)" class="p-2 hover:bg-[var(--color-vintage-mint)]/10 text-[var(--color-vintage-mint)] rounded-lg transition-colors" title="Editar">
                      <Edit3 class="w-4 h-4" />
                    </button>
                    <button @click="toggleActive(user)" class="p-2 rounded-lg transition-colors"
                      :class="user.is_active ? 'hover:bg-[var(--color-vintage-rose)]/10 text-[var(--color-vintage-rose)]' : 'hover:bg-green-500/10 text-green-500'"
                      :title="user.is_active ? 'Desativar usuário' : 'Reativar usuário'"
                    >
                      <component :is="user.is_active ? UserX : UserCheck" class="w-4 h-4" />
                    </button>
                    <button @click="deleteUser(user.id)" class="p-2 hover:bg-[var(--color-vintage-rose)]/10 text-[var(--color-vintage-rose)] rounded-lg transition-colors" title="Excluir">
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
        
        <div class="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-3xl w-full max-w-lg max-h-[90vh] flex flex-col relative z-[101] shadow-2xl overflow-hidden">
          
          <!-- Header -->
          <div class="p-6 border-b border-[var(--border-color)] flex justify-between items-center bg-[var(--bg-app)] shrink-0">
            <div>
              <h2 class="text-xl font-bold tracking-tight text-[var(--text-main)]">
                {{ isEditing ? 'Editar Usuário' : 'Criar Novo Usuário' }}
              </h2>
              <p class="text-xs text-[var(--text-muted)] font-bold mt-1">
                {{ isEditing ? 'Altere o perfil ou status do usuário.' : 'Preencha os dados para criar o acesso.' }}
              </p>
            </div>
            <button @click="closeModal" class="p-2 hover:bg-[var(--bg-card)] rounded-lg transition-colors">
              <X class="w-5 h-5 text-[var(--text-muted)]" />
            </button>
          </div>

          <!-- Body Form -->
          <form @submit.prevent="saveUser" class="p-6 overflow-y-auto flex-1 space-y-5">
            
            <!-- NOME -->
            <div>
              <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Nome Completo *</label>
              <input 
                v-model="form.name" type="text" required
                class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                placeholder="Ex: Ana Luísa Moreira"
              />
            </div>
            
            <!-- E-MAIL -->
            <div>
              <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">E-mail *</label>
              <input 
                v-model="form.email" type="email" required :disabled="isEditing"
                class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed" 
                placeholder="usuario@empresa.com"
              />
              <p v-if="isEditing" class="text-xs text-[var(--text-muted)] mt-1 opacity-70">O e-mail não pode ser alterado.</p>
            </div>

            <!-- SENHA (somente criação) -->
            <div v-if="!isEditing" class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Senha *</label>
                <input 
                  v-model="form.password" type="password" :required="!isEditing"
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                  placeholder="Mínimo 8 caracteres"
                />
              </div>
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Confirmar Senha *</label>
                <input 
                  v-model="form.password_confirm" type="password" :required="!isEditing"
                  class="w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-rose)] transition-colors" 
                  placeholder="Repita a senha"
                />
              </div>
            </div>

            <!-- PERFIL DO SISTEMA -->
            <div>
              <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Perfil de Acesso *</label>
              <div class="grid grid-cols-1 gap-2">
                <label 
                  v-for="opt in profileOptions" 
                  :key="opt.value"
                  class="flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all"
                  :class="form.profile === opt.value 
                    ? 'border-[var(--color-vintage-mint)] bg-[var(--color-vintage-mint)]/10' 
                    : 'border-[var(--border-color)] hover:border-[var(--color-vintage-mint)]/40'"
                >
                  <input type="radio" v-model="form.profile" :value="opt.value" class="hidden" />
                  <div class="p-1.5 rounded-lg" :class="opt.iconBg">
                    <component :is="opt.icon" class="w-4 h-4" :class="opt.iconColor" />
                  </div>
                  <div class="flex-1">
                    <p class="text-sm font-bold text-[var(--text-main)]">{{ opt.label }}</p>
                    <p class="text-xs text-[var(--text-muted)]">{{ opt.description }}</p>
                  </div>
                  <div class="w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0"
                    :class="form.profile === opt.value ? 'border-[var(--color-vintage-mint)]' : 'border-[var(--border-color)]'"
                  >
                    <div v-if="form.profile === opt.value" class="w-2 h-2 rounded-full bg-[var(--color-vintage-mint)]"></div>
                  </div>
                </label>
              </div>
            </div>

            <!-- STATUS (apenas edição) -->
            <div v-if="isEditing" class="flex items-center justify-between p-4 bg-[var(--bg-app)] rounded-xl border border-[var(--border-color)]">
              <div>
                <p class="text-sm font-bold text-[var(--text-main)]">Conta Ativa</p>
                <p class="text-xs text-[var(--text-muted)]">Usuários inativos não conseguem fazer login.</p>
              </div>
              <button 
                type="button"
                @click="form.is_active = !form.is_active"
                class="relative w-12 h-6 rounded-full transition-colors"
                :class="form.is_active ? 'bg-[var(--color-vintage-mint)]' : 'bg-[var(--border-color)]'"
              >
                <span 
                  class="absolute top-1 w-4 h-4 rounded-full bg-white shadow transition-transform"
                  :class="form.is_active ? 'left-7' : 'left-1'"
                ></span>
              </button>
            </div>

            <!-- Actions -->
            <div class="flex gap-4 pt-2 border-t border-[var(--border-color)]">
              <button type="button" @click="closeModal" class="flex-1 py-3 border-2 border-[var(--border-color)] text-[var(--text-muted)] font-bold text-sm rounded-xl hover:bg-[var(--bg-app)] hover:text-[var(--text-main)] transition-colors">
                Cancelar
              </button>
              <button type="submit" :disabled="saving" class="flex-1 py-3 bg-[var(--color-vintage-mint)] text-white font-bold text-sm rounded-xl shadow-md hover:opacity-90 active:scale-[0.98] transition-all flex justify-center items-center gap-2 disabled:opacity-70">
                <Loader2 v-if="saving" class="w-4 h-4 animate-spin" />
                <Save v-else class="w-4 h-4" />
                {{ isEditing ? 'Salvar Alterações' : 'Criar Usuário' }}
              </button>
            </div>
          </form>

        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, markRaw } from 'vue'
import { 
  UserPlus, Search, X, Loader2, Edit3, Trash2, AlertTriangle, Users, Save, 
  LayoutGrid, List, Shield, Key, UserCheck, UserX, CalendarDays,
  Eye, Settings, Wrench
} from 'lucide-vue-next'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const users = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const showModal = ref(false)
const isEditing = ref(false)
const viewMode = ref('list')
const searchQuery = ref('')
const profileFilter = ref('')

// ─── Profile helpers ──────────────────────────────────────
const profileOptions = [
  {
    value: 'administrador',
    label: 'Administrador',
    description: 'Acesso total ao sistema, incluindo usuários e configurações.',
    icon: markRaw(Shield),
    iconBg: 'bg-[var(--color-vintage-rose)]/20',
    iconColor: 'text-[var(--color-vintage-rose)]',
  },
  {
    value: 'gerente',
    label: 'Gerente',
    description: 'Vê todas as OS e relatórios. Pode gerenciar a equipe.',
    icon: markRaw(Key),
    iconBg: 'bg-[var(--color-vintage-mustard)]/20',
    iconColor: 'text-[var(--color-vintage-mustard)]',
  },
  {
    value: 'tecnico',
    label: 'Técnico',
    description: 'Vê e executa apenas as OS atribuídas ou abertas por ele.',
    icon: markRaw(Wrench),
    iconBg: 'bg-[var(--color-vintage-mint)]/20',
    iconColor: 'text-[var(--color-vintage-mint)]',
  },
  {
    value: 'operador',
    label: 'Operador',
    description: 'Acesso básico: pode abrir OS e ver suas próprias tarefas.',
    icon: markRaw(Settings),
    iconBg: 'bg-blue-500/20',
    iconColor: 'text-blue-500',
  },
  {
    value: 'visualizador',
    label: 'Visualizador',
    description: 'Apenas leitura. Não pode criar ou editar dados.',
    icon: markRaw(Eye),
    iconBg: 'bg-[var(--text-muted)]/20',
    iconColor: 'text-[var(--text-muted)]',
  },
]

const profileLabel = (p) => {
  const opt = profileOptions.find(o => o.value === p)
  return opt?.label || p || '—'
}

const profileIcon = (p) => {
  const opt = profileOptions.find(o => o.value === p)
  return opt?.icon || Eye
}

const profileBadgeClass = (p) => {
  const map = {
    administrador: 'text-[var(--color-vintage-rose)] bg-[var(--color-vintage-rose)]/15 border border-[var(--color-vintage-rose)]/20',
    gerente: 'text-[var(--color-vintage-mustard)] bg-[var(--color-vintage-mustard)]/15 border border-[var(--color-vintage-mustard)]/20',
    tecnico: 'text-[var(--color-vintage-mint)] bg-[var(--color-vintage-mint)]/15 border border-[var(--color-vintage-mint)]/20',
    operador: 'text-blue-500 bg-blue-500/15 border border-blue-500/20',
    visualizador: 'text-[var(--text-muted)] bg-[var(--text-muted)]/10 border border-[var(--border-color)]',
  }
  return map[p] || 'text-[var(--text-muted)] bg-[var(--text-muted)]/10 border border-[var(--border-color)]'
}

const avatarBg = (p) => {
  const map = {
    administrador: 'bg-[var(--color-vintage-rose)]',
    gerente: 'bg-[var(--color-vintage-mustard)]',
    tecnico: 'bg-[var(--color-vintage-mint)]',
    operador: 'bg-blue-500',
    visualizador: 'bg-slate-500',
  }
  return map[p] || 'bg-slate-500'
}

const formatDate = (dt) => {
  if (!dt) return '—'
  return new Date(dt).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit' })
}

// ─── Stats ────────────────────────────────────────────────
const statsCards = computed(() => [
  {
    label: 'Total',
    value: users.value.length,
    icon: markRaw(Users),
    iconBg: 'bg-[var(--color-vintage-mint)]/20',
    iconColor: 'text-[var(--color-vintage-mint)]',
  },
  {
    label: 'Ativos',
    value: users.value.filter(u => u.is_active).length,
    icon: markRaw(UserCheck),
    iconBg: 'bg-green-500/20',
    iconColor: 'text-green-500',
  },
  {
    label: 'Administradores',
    value: users.value.filter(u => u.profile === 'administrador').length,
    icon: markRaw(Shield),
    iconBg: 'bg-[var(--color-vintage-rose)]/20',
    iconColor: 'text-[var(--color-vintage-rose)]',
  },
  {
    label: 'Técnicos',
    value: users.value.filter(u => ['tecnico', 'operador'].includes(u.profile)).length,
    icon: markRaw(Wrench),
    iconBg: 'bg-[var(--color-vintage-mustard)]/20',
    iconColor: 'text-[var(--color-vintage-mustard)]',
  },
])

// ─── Filter ───────────────────────────────────────────────
const filteredUsers = computed(() => {
  let list = users.value
  if (profileFilter.value) {
    list = list.filter(u => u.profile === profileFilter.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(u =>
      (u.name && u.name.toLowerCase().includes(q)) ||
      (u.email && u.email.toLowerCase().includes(q))
    )
  }
  return list
})

// ─── Form ─────────────────────────────────────────────────
const defaultForm = {
  id: null,
  name: '',
  email: '',
  password: '',
  password_confirm: '',
  profile: 'tecnico',
  is_active: true,
}
const form = ref({ ...defaultForm })

// ─── CRUD ─────────────────────────────────────────────────
const fetchUsers = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await api.get('users/')
    users.value = response.data.results || response.data
  } catch (err) {
    if (err.response?.status === 403) {
      error.value = 'Acesso negado. Apenas administradores e gerentes podem listar usuários.'
    } else {
      error.value = 'Não foi possível carregar os usuários.'
    }
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  isEditing.value = false
  form.value = { ...defaultForm }
  showModal.value = true
}

const openEditModal = (userPayload) => {
  isEditing.value = true
  form.value = {
    id: userPayload.id,
    name: userPayload.name,
    email: userPayload.email,
    profile: userPayload.profile,
    is_active: userPayload.is_active,
    password: '',
    password_confirm: '',
  }
  showModal.value = true
}

const closeModal = () => { showModal.value = false }

const saveUser = async () => {
  saving.value = true
  try {
    if (isEditing.value) {
      await api.patch(`users/${form.value.id}/`, {
        name: form.value.name,
        profile: form.value.profile,
        is_active: form.value.is_active,
      })
    } else {
      if (form.value.password !== form.value.password_confirm) {
        alert('As senhas não conferem!')
        return
      }
      await api.post('users/', {
        name: form.value.name,
        email: form.value.email,
        password: form.value.password,
        password_confirm: form.value.password_confirm,
        profile: form.value.profile,
        username: form.value.email,
      })
    }
    closeModal()
    fetchUsers()
  } catch (err) {
    console.error(err)
    const data = err.response?.data
    const msg = data?.detail || data?.email?.[0] || data?.password?.[0] || data?.password_confirm?.[0] || JSON.stringify(data) || 'Erro desconhecido.'
    alert(`Erro ao salvar: ${msg}`)
  } finally {
    saving.value = false
  }
}

const toggleActive = async (user) => {
  const action = user.is_active ? 'desativar' : 'reativar'
  if (!confirm(`Tem certeza que deseja ${action} o usuário "${user.name}"?`)) return
  try {
    await api.patch(`users/${user.id}/`, { is_active: !user.is_active, name: user.name, profile: user.profile })
    user.is_active = !user.is_active
  } catch (err) {
    alert('Falha ao alterar status do usuário.')
  }
}

const deleteUser = async (id) => {
  if (!confirm('Excluir este usuário permanentemente? Esta ação não pode ser desfeita.')) return
  try {
    await api.delete(`users/${id}/`)
    fetchUsers()
  } catch (err) {
    const msg = err.response?.data?.detail || 'A exclusão falhou.'
    alert(msg)
  }
}

onMounted(() => { fetchUsers() })
</script>
