<template>
  <div
    class="flex flex-col items-center justify-center rounded-7 px-4 py-6 text-center"
    :class="featured ? 'gold-gradient text-night' : 'border border-gold-dark bg-night-raised text-gold-light'"
  >
    <span class="font-serif text-10xl font-bold">{{ plan.interest_rate }}%</span>
    <span class="mt-1 text-xs font-semibold uppercase tracking-[0.2em]">for {{ plan.name }}</span>
    <span class="mt-3 text-base" :class="featured ? 'text-night/80' : 'text-ink-gray-6'">
      {{ formatMoney(plan.minimum_amount) }} to {{ formatMoney(plan.maximum_amount) }}
    </span>
  </div>
</template>

<script setup>
import { formatMoney } from '@/data/plans'

defineProps({
  plan: { type: Object, required: true },
  featured: { type: Boolean, default: false },
})
</script>
