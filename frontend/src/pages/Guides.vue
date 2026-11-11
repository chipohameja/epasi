<template>
  <main class="mx-auto w-full max-w-3xl px-4 py-8">
    <p class="eyebrow">Help</p>
    <h1 class="mt-1 text-6xl font-bold">User guide</h1>
    <p class="mt-2 text-lg text-ink-gray-7">Choose who you are to see your guide.</p>
    <ul class="mt-6 grid gap-4 sm:grid-cols-2">
      <li v-for="guide in guides" :key="guide.slug">
        <RouterLink
          :to="{ name: 'Guide', params: { slug: guide.slug } }"
          class="panel block h-full transition hover:border-gold-dark"
        >
          <span class="block text-3xl font-semibold text-gold-light">{{ guide.title }}</span>
          <span class="mt-1 block text-ink-gray-8">{{ guide.who }}</span>
          <span class="mt-2 block text-base text-ink-gray-6">{{ guide.summary }}</span>
        </RouterLink>
      </li>
    </ul>
  </main>
</template>

<script setup>
import { guides } from '@/data/guides'
</script>
