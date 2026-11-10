<template>
  <div class="rounded-6 border border-gold-dark bg-night p-4" aria-live="polite">
    <p class="eyebrow">You will repay</p>
    <p class="mt-1 font-serif text-6xl font-bold text-gold-light">{{ formatMoney(repayment.total) }}</p>
    <p class="mt-1 text-base text-ink-gray-7">
      by <strong class="text-ink-gray-9">{{ repayment.dueDate }}</strong>
    </p>
    <p class="mt-2 text-xs text-ink-gray-6">
      {{ formatMoney(amount) }} borrowed + {{ formatMoney(repayment.interest) }} interest ({{
        plan.interest_rate
      }}% flat). No hidden fees. Due date counts from the day you receive the money.
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatMoney, getRepayment } from '@/data/plans'

const props = defineProps({
  plan: { type: Object, required: true },
  amount: { type: Number, required: true },
})

const repayment = computed(() => getRepayment(props.plan, props.amount))
</script>
