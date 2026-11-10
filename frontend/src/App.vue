<template>
  <FrappeUIProvider>
    <div class="flex min-h-screen flex-col">
      <SiteHeader />
      <RouterView class="flex-1" />
      <SiteFooter />
    </div>
  </FrappeUIProvider>
</template>

<script setup>
import { FrappeUIProvider } from 'frappe-ui'
import SiteFooter from '@/components/SiteFooter.vue'
import SiteHeader from '@/components/SiteHeader.vue'
</script>
