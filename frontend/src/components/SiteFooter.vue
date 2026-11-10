<template>
  <footer class="mt-16 border-t border-night-line">
    <div class="mx-auto grid max-w-5xl gap-8 px-4 py-10 sm:grid-cols-2">
      <div>
        <p class="font-serif text-3xl italic text-gold-light">“{{ tagline }}”</p>
        <p class="mt-1 text-base text-ink-gray-6">{{ taglineMeaning }}</p>
        <p class="eyebrow mt-6">We lend · You grow · We succeed together</p>
        <a :href="managerLoginUrl" class="mt-6 inline-block text-base text-ink-gray-6 underline-offset-4 hover:underline">
          Loan manager login
        </a>
      </div>
      <div id="contact">
        <p class="eyebrow">Contact</p>
        <ul class="mt-3 flex flex-col gap-3">
          <li v-for="contact in contacts" :key="contact.name">
            <span class="font-serif text-2xl text-gold-light">{{ contact.name }}</span>
            <span v-if="contact.role" class="ml-2 text-xs uppercase tracking-wider text-gold">
              {{ contact.role }}
            </span>
            <a
              :href="whatsappLink(contact.whatsapp)"
              class="block text-lg text-ink-gray-8 underline-offset-4 hover:underline"
            >
              {{ contact.phone }} <span class="text-base text-ink-gray-6">· Call or WhatsApp</span>
            </a>
          </li>
        </ul>
        <p class="mt-4 text-base text-ink-gray-6">
          <a :href="`mailto:${email}`" class="hover:underline">{{ email }}</a> · {{ town }}
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { contacts, email, managerLoginUrl, tagline, taglineMeaning, town, whatsappLink } from '@/data/business'
</script>
