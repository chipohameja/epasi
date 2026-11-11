<template>
  <main v-if="guide" class="mx-auto w-full max-w-3xl px-4 py-8">
    <RouterLink
      :to="{ name: 'Guides' }"
      class="text-base text-ink-gray-6 underline-offset-4 hover:underline"
    >
      ← All guides
    </RouterLink>
    <p class="eyebrow mt-4">Guide for</p>
    <h1 class="mt-1 text-6xl font-bold">{{ guide.title }}</h1>
    <p class="mt-2 text-lg text-ink-gray-7">{{ guide.who }} {{ guide.summary }}</p>
    <nav class="panel mt-6" aria-label="Contents">
      <p class="eyebrow">In this guide</p>
      <ol class="mt-2 flex flex-col gap-1">
        <li v-for="(section, index) in guide.sections" :key="section.title">
          <a
            :href="`#step-${index + 1}`"
            class="text-ink-gray-8 underline-offset-4 hover:underline"
          >
            {{ index + 1 }}. {{ section.title }}
          </a>
        </li>
      </ol>
    </nav>
    <div class="mt-6 flex flex-col gap-5">
      <GuideSection
        v-for="(section, index) in guide.sections"
        :key="section.title"
        :section="section"
        :number="index + 1"
      />
    </div>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import GuideSection from '@/components/GuideSection.vue'
import { findGuide } from '@/data/guides'

const props = defineProps({ slug: { type: String, required: true } })
const guide = computed(() => findGuide(props.slug))
</script>
