<template>
  <main class="mx-auto w-full max-w-3xl px-4 py-8">
    <ErrorMessage
      v-if="summary.error"
      :message="summary.error.message?.replace(/^\w+Error: /, '')"
    />
    <template v-else-if="agent">
      <p class="eyebrow">Partner</p>
      <div class="mt-1 flex items-baseline justify-between gap-3">
        <h1 class="text-6xl font-bold">{{ agent.full_name }}</h1>
        <a href="/logout" class="text-base text-ink-gray-6 underline-offset-4 hover:underline"
          >Sign out</a
        >
      </div>

      <section class="panel mt-6" aria-labelledby="link-heading">
        <h2 id="link-heading" class="text-2xl font-semibold">Your referral link</h2>
        <p class="mt-1 text-base text-ink-gray-6">
          Share it. People who apply with it are linked to you.
        </p>
        <div class="mt-3 flex flex-col gap-2 sm:flex-row">
          <code
            class="flex-1 truncate rounded-4 border border-night-line px-3 py-2.5 text-base text-gold-light"
          >
            {{ agent.referral_link }}
          </code>
          <button type="button" class="gold-button" @click="copyLink">
            {{ copied ? 'Copied' : 'Copy link' }}
          </button>
        </div>
      </section>

      <section class="mt-6 grid grid-cols-3 gap-3" aria-label="Commission totals">
        <div v-for="total in totals" :key="total.label" class="panel !p-4 text-center">
          <p class="text-xs uppercase tracking-wider text-ink-gray-6">
            {{ total.label }}
          </p>
          <p class="mt-1 text-2xl font-semibold text-gold-light sm:text-4xl">
            {{ formatMoney(total.value) }}
          </p>
        </div>
      </section>

      <section class="mt-8" aria-labelledby="referrals-heading">
        <h2 id="referrals-heading" class="text-3xl font-semibold">Your referrals</h2>
        <p v-if="!agent.referrals.length" class="panel mt-3 text-ink-gray-7">
          No referrals yet. Share your link to start.
        </p>
        <ul v-else class="mt-3 flex flex-col gap-2">
          <ReferralRow
            v-for="(referral, index) in agent.referrals"
            :key="index"
            :referral="referral"
          />
        </ul>
      </section>
    </template>
    <p v-else class="text-ink-gray-6">Loading…</p>
  </main>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ErrorMessage, useCall } from 'frappe-ui'
import ReferralRow from '@/components/ReferralRow.vue'
import { formatMoney } from '@/data/plans'

const summary = useCall({ url: '/api/v2/method/epasi.api.partner.get_partner_summary' })
const agent = computed(() => summary.data)
const copied = ref(false)

const totals = computed(() => [
  { label: 'Earned', value: agent.value.commission_earned },
  { label: 'Paid', value: agent.value.commission_paid },
  { label: 'Unpaid', value: agent.value.commission_unpaid },
])

async function copyLink() {
  await navigator.clipboard.writeText(agent.value.referral_link)
  copied.value = true
}
</script>
