<template>
  <section class="panel flex flex-col gap-4" :aria-labelledby="headingId">
    <h2 :id="headingId" class="text-3xl font-semibold">
      <span class="text-gold">{{ number }}.</span> {{ section.title }}
    </h2>
    <p v-if="section.text" class="text-lg text-ink-gray-8">{{ section.text }}</p>
    <ol v-if="section.steps" class="flex flex-col gap-2">
      <li v-for="(step, index) in section.steps" :key="step" class="flex gap-3 text-lg">
        <span
          class="gold-gradient flex size-6 shrink-0 items-center justify-center rounded-full text-sm font-bold text-night"
        >
          {{ index + 1 }}
        </span>
        <span class="text-ink-gray-8">{{ step }}</span>
      </li>
    </ol>
    <figure v-if="section.image" :class="section.image.phone ? 'mx-auto max-w-xs' : ''">
      <img
        :src="screenshotUrl(section.image.file)"
        :alt="section.image.alt"
        loading="lazy"
        class="w-full rounded-4 border border-night-line"
      />
      <figcaption class="mt-1 text-center text-sm text-ink-gray-6">
        {{ section.image.alt }}
      </figcaption>
    </figure>
    <div v-if="section.example" class="rounded-4 border border-gold-dark p-4">
      <p class="eyebrow">Example</p>
      <p v-for="line in section.example" :key="line" class="mt-1 text-ink-gray-8">{{ line }}</p>
    </div>
    <p v-if="section.tip" class="rounded-4 bg-night p-4 text-ink-gray-7">
      <strong class="text-gold-light">Tip:</strong> {{ section.tip }}
    </p>
  </section>
</template>

<script setup>
import { screenshotUrl } from '@/data/guides'

const props = defineProps({
  section: { type: Object, required: true },
  number: { type: Number, required: true },
})
const headingId = `step-${props.number}`
</script>
