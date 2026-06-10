<template>
  <div class="h-full flex flex-col p-6 overflow-hidden">
    <!-- Header -->
    <header class="mb-8 flex justify-between items-center shrink-0">
      <div>
        <h1 class="text-3xl font-bold tracking-tighter text-[var(--text-main)]">Meu Perfil</h1>
        <p class="text-[var(--text-muted)] mt-1 font-medium">Atualize suas informações pessoais e credenciais de acesso</p>
      </div>
    </header>

    <!-- Content -->
    <div class="flex-1 overflow-auto bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] shadow-sm p-6 lg:p-10">
      
      <!-- Layout Principal em Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-16 max-w-5xl">
        
        <!-- Seção: Dados Pessoais -->
        <section class="space-y-6 mb-12 lg:mb-0">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 rounded-lg bg-[var(--color-vintage-blue)]/20 flex items-center justify-center text-[var(--color-vintage-blue)]">
              <User class="w-5 h-5" />
            </div>
            <h2 class="text-xl font-bold text-[var(--text-main)]">Dados Pessoais</h2>
          </div>

          <!-- Alert Messages para Perfil -->
          <Transition enter-active-class="transition duration-300 ease-out" enter-from-class="transform -translate-y-2 opacity-0" enter-to-class="transform translate-y-0 opacity-100" leave-active-class="transition duration-200 ease-in" leave-from-class="transform translate-y-0 opacity-100" leave-to-class="transform -translate-y-2 opacity-0">
            <div v-if="profileError" class="p-4 rounded-xl border border-[var(--color-vintage-rose)] bg-[var(--color-vintage-rose)]/10 flex items-start gap-3">
              <AlertCircle class="w-5 h-5 text-[var(--color-vintage-rose)] flex-shrink-0 mt-0.5" />
              <p class="text-sm text-[var(--color-vintage-rose)] font-semibold">{{ profileError }}</p>
            </div>
          </Transition>
          <Transition enter-active-class="transition duration-300 ease-out" enter-from-class="transform -translate-y-2 opacity-0" enter-to-class="transform translate-y-0 opacity-100" leave-active-class="transition duration-200 ease-in" leave-from-class="transform translate-y-0 opacity-100" leave-to-class="transform -translate-y-2 opacity-0">
            <div v-if="profileSuccess" class="p-4 rounded-xl border border-[var(--color-vintage-mint)] bg-[var(--color-vintage-mint)]/10 flex items-start gap-3">
              <CheckCircle class="w-5 h-5 text-[var(--color-vintage-mint)] flex-shrink-0 mt-0.5" />
              <p class="text-sm text-[var(--color-vintage-mint)] font-semibold">{{ profileSuccess }}</p>
            </div>
          </Transition>

          <form @submit.prevent="handleUpdateProfile" class="space-y-5">
            <!-- Email (Read-only) -->
            <div class="space-y-1.5">
              <label class="block text-xs font-bold uppercase tracking-wider text-[var(--text-muted)]">E-mail</label>
              <div class="relative flex items-center bg-[var(--bg-app)]/50 rounded-xl overflow-hidden border border-transparent">
                <Mail class="w-5 h-5 absolute left-3 text-[var(--text-muted)]" />
                <input
                  v-model="email"
                  type="email"
                  disabled
                  class="w-full bg-transparent border-none py-3 pl-10 pr-4 text-[var(--text-muted)] cursor-not-allowed focus:ring-0 focus:outline-none"
                />
              </div>
            </div>

            <!-- Tipo de Perfil (Read-only) -->
            <div class="space-y-1.5">
              <label class="block text-xs font-bold uppercase tracking-wider text-[var(--text-muted)]">Tipo de Acesso</label>
              <div class="relative flex items-center bg-[var(--bg-app)]/50 rounded-xl overflow-hidden border border-transparent">
                <Shield class="w-5 h-5 absolute left-3 text-[var(--text-muted)]" />
                <input
                  v-model="role"
                  type="text"
                  disabled
                  class="w-full bg-transparent border-none py-3 pl-10 pr-4 text-[var(--text-muted)] capitalize cursor-not-allowed focus:ring-0 focus:outline-none"
                />
              </div>
            </div>

            <!-- Name Input -->
            <div class="space-y-1.5 focus-within:border-[var(--color-vintage-blue)] border-b-2 border-transparent transition-colors">
              <label class="block text-xs font-bold uppercase tracking-wider text-[var(--text-muted)]">Nome Completo</label>
              <div class="relative flex items-center">
                <Type class="w-5 h-5 absolute left-0 text-[var(--text-muted)]" />
                <input
                  v-model="name"
                  type="text"
                  required
                  :disabled="isLoadingProfile"
                  class="w-full bg-transparent border-none py-2 pl-8 text-[var(--text-main)] placeholder:text-[var(--text-muted)]/50 focus:ring-0 focus:outline-none"
                  placeholder="Seu nome"
                />
              </div>
            </div>

            <!-- Submit Profile -->
            <div class="pt-2">
              <button
                type="submit"
                :disabled="isLoadingProfile || !hasProfileChanges"
                class="w-full sm:w-auto px-8 h-12 bg-[var(--color-vintage-blue)] text-white rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Loader2 v-if="isLoadingProfile" class="w-5 h-5 animate-spin" />
                <span v-else>Salvar Alterações</span>
              </button>
            </div>
          </form>
        </section>

        <!-- Seção: Alterar Senha -->
        <section class="space-y-6">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 rounded-lg bg-[var(--color-vintage-rose)]/20 flex items-center justify-center text-[var(--color-vintage-rose)]">
              <Lock class="w-5 h-5" />
            </div>
            <h2 class="text-xl font-bold text-[var(--text-main)]">Alterar Senha</h2>
          </div>

          <!-- Alert Messages para Senha -->
          <Transition enter-active-class="transition duration-300 ease-out" enter-from-class="transform -translate-y-2 opacity-0" enter-to-class="transform translate-y-0 opacity-100" leave-active-class="transition duration-200 ease-in" leave-from-class="transform translate-y-0 opacity-100" leave-to-class="transform -translate-y-2 opacity-0">
            <div v-if="passwordError" class="p-4 rounded-xl border border-[var(--color-vintage-rose)] bg-[var(--color-vintage-rose)]/10 flex items-start gap-3">
              <AlertCircle class="w-5 h-5 text-[var(--color-vintage-rose)] flex-shrink-0 mt-0.5" />
              <p class="text-sm text-[var(--color-vintage-rose)] font-semibold">{{ passwordError }}</p>
            </div>
          </Transition>
          <Transition enter-active-class="transition duration-300 ease-out" enter-from-class="transform -translate-y-2 opacity-0" enter-to-class="transform translate-y-0 opacity-100" leave-active-class="transition duration-200 ease-in" leave-from-class="transform translate-y-0 opacity-100" leave-to-class="transform -translate-y-2 opacity-0">
            <div v-if="passwordSuccess" class="p-4 rounded-xl border border-[var(--color-vintage-mint)] bg-[var(--color-vintage-mint)]/10 flex items-start gap-3">
              <CheckCircle class="w-5 h-5 text-[var(--color-vintage-mint)] flex-shrink-0 mt-0.5" />
              <p class="text-sm text-[var(--color-vintage-mint)] font-semibold">{{ passwordSuccess }}</p>
            </div>
          </Transition>

          <form @submit.prevent="handleChangePassword" class="space-y-5">
            <!-- Current Password -->
            <div class="space-y-1.5 focus-within:border-[var(--color-vintage-rose)] border-b-2 border-transparent transition-colors">
              <label class="block text-xs font-bold uppercase tracking-wider text-[var(--text-muted)]">Senha Atual</label>
              <div class="relative flex items-center">
                <Key class="w-5 h-5 absolute left-0 text-[var(--text-muted)]" />
                <input
                  v-model="passwords.current"
                  type="password"
                  required
                  :disabled="isLoadingPassword"
                  class="w-full bg-transparent border-none py-2 pl-8 text-[var(--text-main)] placeholder:text-[var(--text-muted)]/50 focus:ring-0 focus:outline-none"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <!-- New Password -->
            <div class="space-y-1.5 focus-within:border-[var(--color-vintage-rose)] border-b-2 border-transparent transition-colors">
              <label class="block text-xs font-bold uppercase tracking-wider text-[var(--text-muted)]">Nova Senha</label>
              <div class="relative flex items-center">
                <Lock class="w-5 h-5 absolute left-0 text-[var(--text-muted)]" />
                <input
                  v-model="passwords.new"
                  type="password"
                  required
                  :disabled="isLoadingPassword"
                  class="w-full bg-transparent border-none py-2 pl-8 text-[var(--text-main)] placeholder:text-[var(--text-muted)]/50 focus:ring-0 focus:outline-none"
                  placeholder="Mínimo 8 caracteres"
                />
              </div>
            </div>

            <!-- Confirm New Password -->
            <div class="space-y-1.5 focus-within:border-[var(--color-vintage-rose)] border-b-2 border-transparent transition-colors">
              <label class="block text-xs font-bold uppercase tracking-wider text-[var(--text-muted)]">Confirmar Nova Senha</label>
              <div class="relative flex items-center">
                <Check class="w-5 h-5 absolute left-0 text-[var(--text-muted)]" />
                <input
                  v-model="passwords.confirm"
                  type="password"
                  required
                  :disabled="isLoadingPassword"
                  class="w-full bg-transparent border-none py-2 pl-8 text-[var(--text-main)] placeholder:text-[var(--text-muted)]/50 focus:ring-0 focus:outline-none"
                  placeholder="Confirme a nova senha"
                />
              </div>
            </div>

            <!-- Submit Password -->
            <div class="pt-2">
              <button
                type="submit"
                :disabled="isLoadingPassword"
                class="w-full sm:w-auto px-8 h-12 bg-[var(--color-vintage-charcoal)] dark:bg-[var(--color-vintage-paper)] text-[var(--color-vintage-cream)] dark:text-[var(--color-vintage-charcoal)] rounded-xl font-bold flex items-center justify-center gap-2 hover:opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Loader2 v-if="isLoadingPassword" class="w-5 h-5 animate-spin" />
                <span v-else>Alterar Senha</span>
              </button>
            </div>
          </form>
        </section>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import {
  User, Lock, Mail, Shield, Type, Key, Check,
  AlertCircle, CheckCircle, Loader2
} from 'lucide-vue-next'

const authStore = useAuthStore()

// State for Profile
const name = ref('')
const email = ref('')
const role = ref('')

// State for Password
const passwords = ref({
  current: '',
  new: '',
  confirm: ''
})

// Loading & Messages
const isLoadingProfile = ref(false)
const profileError = ref('')
const profileSuccess = ref('')

const isLoadingPassword = ref(false)
const passwordError = ref('')
const passwordSuccess = ref('')

// Initialize data
onMounted(() => {
  if (authStore.user) {
    name.value = authStore.user.name || ''
    email.value = authStore.user.email || ''
    role.value = authStore.user.profile || ''
  }
})

// Computed to check if name changed
const hasProfileChanges = computed(() => {
  return name.value !== (authStore.user?.name || '')
})

// Handlers
const handleUpdateProfile = async () => {
  profileError.value = ''
  profileSuccess.value = ''
  isLoadingProfile.value = true

  try {
    const res = await api.patch('/users/me/', { name: name.value })
    authStore.updateUser(res.data)
    profileSuccess.value = 'Nome atualizado com sucesso!'
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      profileSuccess.value = ''
    }, 3000)
  } catch (error) {
    profileError.value = error.response?.data?.detail || error.response?.data?.name?.[0] || 'Erro ao atualizar perfil.'
  } finally {
    isLoadingProfile.value = false
  }
}

const handleChangePassword = async () => {
  passwordError.value = ''
  passwordSuccess.value = ''

  if (passwords.value.new.length < 8) {
    passwordError.value = 'A nova senha deve ter pelo menos 8 caracteres.'
    return
  }

  if (passwords.value.new !== passwords.value.confirm) {
    passwordError.value = 'A nova senha e a confirmação não conferem.'
    return
  }

  isLoadingPassword.value = true

  try {
    await api.post('/users/change-password/', {
      current_password: passwords.value.current,
      new_password: passwords.value.new,
      new_password_confirm: passwords.value.confirm
    })
    
    passwordSuccess.value = 'Senha alterada com sucesso!'
    
    // Clear form
    passwords.value = {
      current: '',
      new: '',
      confirm: ''
    }

    // Clear success message after 3 seconds
    setTimeout(() => {
      passwordSuccess.value = ''
    }, 3000)
  } catch (error) {
    passwordError.value = 
      error.response?.data?.detail || 
      error.response?.data?.non_field_errors?.[0] ||
      error.response?.data?.current_password?.[0] ||
      'Erro ao alterar a senha. Verifique sua senha atual.'
  } finally {
    isLoadingPassword.value = false
  }
}
</script>
