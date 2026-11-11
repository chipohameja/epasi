<template>
  <main class="mx-auto w-full max-w-md px-4 py-12 text-center">
    <div
      class="gold-gradient mx-auto flex size-14 items-center justify-center rounded-full text-4xl text-night"
      aria-hidden="true"
    >
      ✓
    </div>
    <h1 class="mt-5 text-6xl font-bold">Application received</h1>
    <p class="mt-3 text-ink-gray-7">Your reference number is</p>
    <p class="mt-1 font-mono text-4xl font-semibold tracking-wider text-gold-light">
      {{ application }}
    </p>
    <p class="mt-4 text-ink-gray-7">
      A loan manager will contact you on WhatsApp soon. Keep your collateral ready.
    </p>
    <a :href="whatsappLink(manager.whatsapp, message)" class="gold-button mt-6 inline-block">
      Message us on WhatsApp
    </a>
    <RouterLink
      :to="{ name: 'Home', query: { review: 1, application } }"
      class="mt-4 block text-base text-gold-light underline-offset-4 hover:underline"
    >
      Leave a review
    </RouterLink>
    <RouterLink
      to="/"
      class="mt-2 block text-base text-ink-gray-6 underline-offset-4 hover:underline"
    >
      Back to home
    </RouterLink>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { contacts, whatsappLink } from '@/data/business'

const props = defineProps({ application: { type: String, required: true } })
const manager = contacts[0]
const message = computed(
  () => `Hello Epasi, my loan application reference is ${props.application}.`,
)
</script>
