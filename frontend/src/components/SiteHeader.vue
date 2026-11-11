<template>
  <header class="border-b border-night-line">
    <div class="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
      <RouterLink to="/" class="flex items-center gap-3" aria-label="Epasi Money Solutions home">
        <img :src="iconUrl" alt="" class="size-10 rounded-4" />
        <span class="leading-tight">
          <span class="block font-serif text-3xl font-bold tracking-wide text-gold-light"
            >EPASI</span
          >
          <span class="block text-[10px] tracking-[0.2em] text-ink-gray-6">MONEY SOLUTIONS</span>
        </span>
      </RouterLink>
      <div class="flex items-center gap-3 whitespace-nowrap">
        <a
          :href="managerLoginUrl"
          class="text-xs text-ink-gray-6 underline-offset-4 hover:underline sm:text-sm"
        >
          Manager login
        </a>
        <RouterLink
          v-if="route.name !== 'Apply'"
          :to="{ name: 'Apply' }"
          class="gold-button !py-2 !text-base"
        >
          Apply now
        </RouterLink>
      </div>
    </div>
  </header>
</template>

<script setup>
import iconUrl from '@images/epasi-icon.png'
import { useRoute } from 'vue-router'
import { managerLoginUrl } from '@/data/business'

const route = useRoute()
</script>
