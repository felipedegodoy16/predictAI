<template>
  <transition name="fade-overlay">
    <div v-if="isLoading" class="fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-black/60 backdrop-blur-md">
      <!-- Animated Center Logo/Spinner -->
      <div class="relative flex items-center justify-center mb-6">
        <!-- Outer Glowing Ring -->
        <div class="absolute w-32 h-32 rounded-full border-[3px] border-[var(--color-vintage-mint)]/30 border-t-[var(--color-vintage-mint)] animate-spin" style="animation-duration: 2s;"></div>
        <!-- Inner Fast Ring -->
        <div class="absolute w-24 h-24 rounded-full border-[3px] border-[var(--color-vintage-mustard)]/20 border-b-[var(--color-vintage-mustard)] animate-spin-reverse" style="animation-duration: 1.5s;"></div>
        <!-- Center Icon -->
        <div class="w-16 h-16 bg-[var(--bg-card)] rounded-full flex items-center justify-center shadow-[0_0_30px_rgba(144,169,158,0.4)] z-10">
          <Activity class="w-8 h-8 text-[var(--color-vintage-mint)] animate-pulse" />
        </div>
      </div>
      
      <!-- Text -->
      <h3 class="text-2xl font-bold tracking-tight text-white mb-2 drop-shadow-md">
        Analisando Dados Predicionais
      </h3>
      <p class="text-[var(--color-vintage-mint)] font-medium text-sm animate-pulse">
        Por favor, aguarde um momento...
      </p>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Activity } from 'lucide-vue-next'

const isLoading = ref(false)

const handleLoadingEvent = (event) => {
  isLoading.value = event.detail
}

onMounted(() => {
  window.addEventListener('global-loading', handleLoadingEvent)
})

onUnmounted(() => {
  window.removeEventListener('global-loading', handleLoadingEvent)
})
</script>

<style scoped>
.animate-spin-reverse {
  animation: spin-reverse linear infinite;
}

@keyframes spin-reverse {
  from { transform: rotate(360deg); }
  to { transform: rotate(0deg); }
}

.fade-overlay-enter-active,
.fade-overlay-leave-active {
  transition: opacity 0.4s ease, backdrop-filter 0.4s ease;
}

.fade-overlay-enter-from,
.fade-overlay-leave-to {
  opacity: 0;
  backdrop-filter: blur(0px);
}
</style>
