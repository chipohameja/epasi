<template>
  <li class="panel flex items-center justify-between gap-3 !p-4">
    <div>
      <p class="text-lg font-semibold text-ink-gray-9">{{ referral.name }}</p>
      <p class="text-base text-ink-gray-6">
        {{ shortDate.format(new Date(referral.date)) }}
      </p>
    </div>
    <div class="text-right">
      <Badge :label="referral.status" :theme="themes[referral.status] || 'gray'" />
      <p v-if="referral.commission_status" class="mt-1 text-base text-ink-gray-8">
        {{ formatMoney(referral.commission) }} · {{ referral.commission_status }}
      </p>
    </div>
  </li>
</template>

<script setup>
import { Badge } from 'frappe-ui'
import { formatMoney } from '@/data/plans'

defineProps({ referral: { type: Object, required: true } })

const shortDate = new Intl.DateTimeFormat('en-GB', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
})
const themes = {
  Approved: 'blue',
  Active: 'blue',
  Pending: 'orange',
  Overdue: 'orange',
  Closed: 'green',
  Rejected: 'red',
  Defaulted: 'red',
}
</script>
