<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  // Check user theme preference
  // Default to light mode unless explicitly set to dark
  if (localStorage.theme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
})
</script>

<template>
  <router-view />
  <!-- Toasts container will be placed here -->
</template>
