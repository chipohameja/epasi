<template>
  <div class="flex flex-col gap-1.5">
    <span class="text-xs text-ink-gray-5">
      Collateral photos <span class="text-ink-red-3">*</span>
    </span>
    <div class="flex flex-wrap gap-2">
      <div v-for="(photo, index) in photos" :key="index" class="relative">
        <img :src="photo.content" alt="Collateral photo" class="size-20 rounded object-cover" />
        <button
          type="button"
          class="absolute -right-1.5 -top-1.5 rounded-full bg-surface-gray-7 px-1.5 text-xs text-ink-white"
          :aria-label="`Remove photo ${index + 1}`"
          @click="remove(index)"
        >
          ×
        </button>
      </div>
      <label
        v-if="photos.length < maximum"
        class="flex size-20 cursor-pointer items-center justify-center rounded border border-dashed border-outline-gray-3 text-sm text-ink-gray-6"
      >
        + Add
        <input type="file" accept="image/*" multiple class="sr-only" @change="add" />
      </label>
    </div>
    <span class="text-xs text-ink-gray-5">Add 1 to {{ maximum }} clear photos.</span>
  </div>
</template>

<script setup>
import { resizeImage } from '@/utils/images'

const maximum = 5
const photos = defineModel({ type: Array, default: () => [] })

async function add(event) {
  const files = [...event.target.files].slice(0, maximum - photos.value.length)
  const contents = await Promise.all(files.map(resizeImage))
  photos.value = [...photos.value, ...contents.map((content) => ({ content }))]
  event.target.value = ''
}

function remove(index) {
  photos.value = photos.value.filter((_, position) => position !== index)
}
</script>
