import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/esqueci-minha-senha',
      name: 'forgot-password',
      component: () => import('../views/ForgotPasswordView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      name: 'layout',
      component: () => import('../components/layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('../views/DashboardView.vue')
        },
        // Mapped views
        {
          path: 'machines',
          name: 'machines',
          component: () => import('../views/MachinesView.vue')
        },
        {
          path: 'alerts',
          name: 'alerts',
          component: () => import('../views/AlertsView.vue')
        },
        {
          path: 'suppliers',
          name: 'suppliers',
          component: () => import('../views/SuppliersView.vue'),
          meta: { roles: ['ADMIN', 'MANAGER'] } // Técnico não acessa
        },
        {
          path: 'reports',
          name: 'reports',
          component: () => import('../views/ReportsView.vue')
        },
        {
          path: 'users',
          name: 'users',
          component: () => import('../views/UsersView.vue'),
          meta: { roles: ['ADMIN'] }
        },
        {
          path: 'logs',
          name: 'logs',
          component: () => import('../views/LogsView.vue'),
          meta: { roles: ['ADMIN'] }
        }
      ]
    }
  ]
})

import { useAuthStore } from '../stores/auth'

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login' })
  } else if (to.name === 'login' && isAuthenticated) {
    next({ name: 'dashboard' })
  } else if (to.meta.roles && !to.meta.roles.includes(authStore.userRole)) {
    next({ name: 'dashboard' }) // Redireciona de volta em caso de falta de permissao
  } else {
    next()
  }
})

export default router
