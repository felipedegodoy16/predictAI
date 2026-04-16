<template>
  <div class="flex h-screen overflow-hidden">
    <!-- Sidebar -->
    <aside class="w-64 border-r border-[var(--border-color)] bg-[var(--bg-card)] flex flex-col relative z-30">
      <div class="p-6">
        <h1 class="text-2xl font-bold tracking-tighter text-[var(--color-vintage-charcoal)] dark:text-[var(--text-main)] flex items-center gap-2">
          <Activity class="w-6 h-6 text-[var(--color-vintage-mint)]" />
          PredictAI
        </h1>
      </div>
      <nav class="flex-1 px-4 space-y-2 mt-4">
        <!-- Dashboard -->
        <router-link to="/" exact-active-class="bg-[var(--color-vintage-mint)]/20 text-[var(--color-vintage-charcoal)] dark:text-[var(--text-main)] border-r-4 border-[var(--color-vintage-mint)] shadow-inner" class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-[var(--bg-app)] transition-colors text-[var(--text-muted)]">
          <LayoutDashboard class="w-5 h-5" />
          <span class="font-medium">Dashboard</span>
        </router-link>
        <!-- Machines -->
        <router-link to="/machines" exact-active-class="bg-[var(--color-vintage-mint)]/20 text-[var(--color-vintage-charcoal)] dark:text-[var(--text-main)] border-r-4 border-[var(--color-vintage-mint)] shadow-inner" class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-[var(--bg-app)] transition-colors text-[var(--text-muted)]">
          <Factory class="w-5 h-5" />
          <span class="font-medium">Máquinas</span>
        </router-link>
        <!-- Work Orders -->
        <router-link to="/work-orders" exact-active-class="bg-[var(--color-vintage-mint)]/20 text-[var(--color-vintage-charcoal)] dark:text-[var(--text-main)] border-r-4 border-[var(--color-vintage-mint)] shadow-inner" class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-[var(--bg-app)] transition-colors text-[var(--text-muted)]">
          <ClipboardList class="w-5 h-5" />
          <span class="font-medium">Ordens de Serviço</span>
        </router-link>
        <!-- Reports -->
        <router-link to="/reports" exact-active-class="bg-[var(--color-vintage-mint)]/20 text-[var(--color-vintage-charcoal)] dark:text-[var(--text-main)] border-r-4 border-[var(--color-vintage-mint)] shadow-inner" class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-[var(--bg-app)] transition-colors text-[var(--text-muted)]">
          <FileText class="w-5 h-5" />
          <span class="font-medium">Relatórios</span>
        </router-link>
        <!-- Users -->
        <router-link v-if="authStore.userRole === 'ADMIN'" to="/users" exact-active-class="bg-[var(--color-vintage-mint)]/20 text-[var(--color-vintage-charcoal)] dark:text-[var(--text-main)] border-r-4 border-[var(--color-vintage-mint)] shadow-inner" class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-[var(--bg-app)] transition-colors text-[var(--text-muted)]">
          <Users class="w-5 h-5" />
          <span class="font-medium">Usuários</span>
        </router-link>
        <!-- Logs -->
        <router-link v-if="authStore.userRole === 'ADMIN'" to="/logs" exact-active-class="bg-[var(--color-vintage-mint)]/20 text-[var(--color-vintage-charcoal)] dark:text-[var(--text-main)] border-r-4 border-[var(--color-vintage-mint)] shadow-inner" class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-[var(--bg-app)] transition-colors text-[var(--text-muted)]">
          <ShieldAlert class="w-5 h-5" />
          <span class="font-medium">Logs de Auditoria</span>
        </router-link>
      </nav>
      <div class="p-4 border-t border-[var(--border-color)]">
        <div class="mb-4">
          <p class="text-sm font-medium">Usuário Logado</p>
          <p class="text-xs text-[var(--text-muted)] truncate" :title="authStore.user?.email">{{ authStore.user?.email || 'Desconhecido' }}</p>
        </div>
        <button @click="handleLogout" class="text-sm text-[var(--color-vintage-rose)] hover:underline flex items-center gap-1 font-medium">
          <LogOut class="w-4 h-4" />
          Desconectar
        </button>
      </div>
    </aside>

    <!-- Invisible Overlay for closing Notification Dropdown -->
    <div v-if="showNotifications" @click="showNotifications = false" class="fixed inset-0 z-40 bg-transparent"></div>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden relative">
      <!-- Header -->
      <header class="h-16 border-b border-[var(--border-color)] bg-[var(--bg-card)] flex items-center justify-between px-6 z-50 relative shadow-sm">
        <h2 class="text-xl font-semibold tracking-tight">{{ currentRouteName }}</h2>
        <div class="flex items-center gap-4">
          <button @click="toggleTheme" class="p-2 rounded-full hover:bg-[var(--bg-app)] transition-colors border border-transparent hover:border-[var(--border-color)]" title="Alternar Tema">
            <Moon v-if="!isDark" class="w-5 h-5 text-[var(--text-muted)]" />
            <Sun v-else class="w-5 h-5 text-[var(--color-vintage-mustard)]" />
          </button>
          
          <div class="relative">
            <button @click="showNotifications = !showNotifications" class="p-2 rounded-full transition-colors border border-transparent hover:border-[var(--border-color)] relative" :class="showNotifications ? 'bg-[var(--bg-app)]' : 'hover:bg-[var(--bg-app)]'" title="Notificações">
              <Bell class="w-5 h-5 text-[var(--text-muted)]" />
              <!-- Badge -->
              <span v-if="hasUnread" class="absolute -top-1 -right-1 min-w-[18px] h-[18px] flex items-center justify-center bg-[var(--color-vintage-rose)] rounded-full border border-[var(--bg-card)] text-[9px] font-bold text-white px-1 shadow-sm">{{ unreadCount }}</span>
            </button>

            <!-- Notifications Dropdown -->
            <transition name="pop">
              <div v-if="showNotifications" class="absolute right-0 top-12 mt-1 w-80 sm:w-96 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl shadow-2xl flex flex-col overflow-hidden">
                <div class="p-4 border-b border-[var(--border-color)] bg-[var(--bg-app)]/50 flex justify-between items-center">
                  <h3 class="font-bold tracking-tight">Notificações Recentes</h3>
                  <span class="text-xs font-bold text-[var(--color-vintage-mint)] bg-[var(--color-vintage-mint)]/10 px-2 py-0.5 rounded-full">{{ unreadCount }} Novas</span>
                </div>
                
                <!-- Scrollable Body -->
                <div class="max-h-[350px] overflow-y-auto flex flex-col">
                  <!-- Empty State -->
                  <div v-if="notifications.length === 0" class="p-8 text-center text-[var(--text-muted)] text-sm font-medium">
                    <p>Nenhuma notificação no momento.</p>
                  </div>
                  
                  <!-- Items -->
                  <div v-else class="flex flex-col">
                    <div 
                      v-for="noty in notifications" 
                      :key="noty.id"
                      class="p-4 border-b border-[var(--border-color)] last:border-b-0 hover:bg-[var(--bg-app)] cursor-pointer transition-colors flex gap-3 items-start relative group"
                    >
                      <!-- Unread Indicator Pip -->
                      <div v-if="!noty.is_read" class="absolute left-1.5 top-5 w-1.5 h-1.5 rounded-full bg-[var(--color-vintage-mint)]"></div>
                      
                      <div class="p-2 rounded-full shrink-0" :class="{
                        'bg-[var(--color-vintage-rose)]/10 text-[var(--color-vintage-rose)]': noty.notification_type === 'CRITICAL',
                        'bg-[var(--color-vintage-mustard)]/10 text-[var(--color-vintage-mustard)]': noty.notification_type === 'WARNING',
                        'bg-blue-500/10 text-blue-500': noty.notification_type === 'INFO'
                      }">
                        <AlertTriangle v-if="noty.notification_type === 'CRITICAL'" class="w-4 h-4" />
                        <AlertCircle v-else-if="noty.notification_type === 'WARNING'" class="w-4 h-4" />
                        <Info v-else class="w-4 h-4" />
                      </div>
                      <div class="flex-1 min-w-0 pr-1">
                        <div class="flex justify-between items-start">
                          <p class="text-sm font-bold truncate pr-2" :class="!noty.is_read ? 'text-[var(--text-main)]' : 'text-[var(--text-muted)]'">{{ noty.title }}</p>
                          <button v-if="!noty.is_read" @click.stop="handleMarkAsRead(noty)" title="Marcar como visualizado" class="shrink-0 p-1 rounded hover:bg-[var(--color-vintage-mint)] hover:text-white text-[var(--color-vintage-mint)] opacity-0 group-hover:opacity-100 transition-all">
                            <Check class="w-3.5 h-3.5" />
                          </button>
                        </div>
                        <p class="text-xs text-[var(--text-muted)] mt-0.5 leading-relaxed truncate whitespace-normal line-clamp-2">{{ noty.message }}</p>
                        <span class="text-[10px] font-bold text-[var(--text-muted)] mt-2 block">{{ new Date(noty.created_at).toLocaleString() }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Footer Action -->
                <div class="p-3 border-t border-[var(--border-color)] bg-[var(--bg-app)]/50">
                  <router-link 
                    to="/alerts" 
                    @click="showNotifications = false"
                    class="block w-full py-2.5 text-center text-sm font-bold text-[var(--color-vintage-mint)] hover:bg-[var(--color-vintage-mint)]/10 rounded-xl transition-colors"
                  >
                    Visualizar todas as {{ totalNotifications }} notificações
                  </router-link>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </header>

      <!-- Content -->
      <main class="flex-1 overflow-auto p-6 relative z-10">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Activity, LayoutDashboard, Factory, Bell, FileText, Users, Moon, Sun, LogOut, AlertTriangle, AlertCircle, Info, Check, ShieldAlert, ClipboardList } from 'lucide-vue-next'
import { getNotifications, markAsRead } from '@/services/notifications'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const currentRouteName = computed(() => {
  const map = {
    'dashboard': 'Visão Geral',
    'machines': 'Máquinas Ativas',
    'alerts': 'Central de Alertas',
    'reports': 'Relatórios',
    'users': 'Gerenciar Acessos',
    'work-orders': 'Ordens de Serviço',
  }
  return map[route.name] || 'App'
})

// UI States
const isDark = ref(localStorage.theme === 'dark')
const showNotifications = ref(false)

// Notifications State
const notifications = ref([])

const totalNotifications = computed(() => notifications.value.length)
const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)
const hasUnread = computed(() => unreadCount.value > 0)

const fetchNotifications = async () => {
  try {
    const res = await getNotifications()
    notifications.value = res.data
  } catch (err) {
    console.error('Failed to fetch notifications', err)
  }
}

const handleMarkAsRead = async (noty) => {
  try {
    await markAsRead(noty.id)
    noty.is_read = true
  } catch (err) {
    console.error('Failed to mark as read', err)
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchNotifications()
    // Poll every 30 seconds
    setInterval(fetchNotifications, 30000)

    // Listen to forced refresh event
    window.addEventListener('refresh-notifications', fetchNotifications)
  }
})

const toggleTheme = () => {
  document.documentElement.classList.toggle('dark')
  isDark.value = !isDark.value
  localStorage.theme = isDark.value ? 'dark' : 'light'
}

const handleLogout = async () => {
  await authStore.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.pop-enter-active,
.pop-leave-active {
  transition: opacity 0.2s ease, transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  transform-origin: top right;
}

.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
