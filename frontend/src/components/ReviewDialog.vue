<template>
  <Dialog v-model:open="open" title="Leave a review">
    <p v-if="sent.data" class="text-ink-gray-7">
      Thank you! Your review will show on our home page after we check it.
    </p>
    <form v-else class="flex flex-col gap-4" @submit.prevent="submit">
      <FormControl
        v-model="form.application"
        label="Application reference"
        placeholder="APP-00010"
        required
      />
      <FormControl
        v-model="form.whatsapp_number"
        type="tel"
        label="WhatsApp number used to apply"
        placeholder="0972 616 440"
        required
      />
      <div class="flex flex-col gap-1.5">
        <span class="text-xs text-ink-gray-5">Your rating</span>
        <Rating v-model="form.rating" size="lg" />
      </div>
      <FormControl
        v-model="form.comment"
        type="textarea"
        label="Your comment"
        :description="`${form.comment.length}/${MAXIMUM_COMMENT_LENGTH}`"
        :maxlength="MAXIMUM_COMMENT_LENGTH"
        required
      />
      <ErrorMessage :message="errorMessage" />
      <button type="submit" class="gold-button disabled:opacity-60" :disabled="sent.loading">
        {{ sent.loading ? 'Sending…' : 'Send review' }}
      </button>
    </form>
  </Dialog>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { Dialog, ErrorMessage, FormControl, Rating, useCall } from 'frappe-ui'

const MAXIMUM_COMMENT_LENGTH = 300
const open = defineModel('open', { type: Boolean })
const props = defineProps({ application: { type: String, default: '' } })
const form = reactive({
  application: props.application,
  whatsapp_number: '',
  rating: 0,
  comment: '',
})
const ratingError = ref('')

const sent = useCall({
  url: '/api/v2/method/epasi.api.public.submit_review',
  method: 'POST',
  immediate: false,
})

const errorMessage = computed(
  () => ratingError.value || sent.error?.message?.replace(/^\w+Error: /, ''),
)

function submit() {
  ratingError.value = form.rating ? '' : 'Choose a rating from 1 to 5 stars.'
  if (!ratingError.value) sent.submit({ ...form })
}
</script>
