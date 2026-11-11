<template>
  <figure class="panel flex h-full flex-col gap-3">
    <div role="img" :aria-label="`${review.rating} out of 5 stars`">
      <Rating :model-value="review.rating" disabled aria-hidden="true" />
    </div>
    <blockquote class="flex-1 text-lg text-ink-gray-8">“{{ review.comment }}”</blockquote>
    <figcaption class="font-semibold text-ink-gray-9">{{ review.display_name }}</figcaption>
  </figure>
</template>

<script setup>
import { Rating } from 'frappe-ui'

defineProps({ review: { type: Object, required: true } })
</script>
