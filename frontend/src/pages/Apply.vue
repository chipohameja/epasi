<template>
  <main class="mx-auto w-full max-w-lg px-4 py-8">
    <h1 class="text-6xl font-bold">Apply for a loan</h1>
    <p class="mt-2 text-p-base text-ink-gray-7">
      Fill in your details. We will contact you on WhatsApp.
    </p>
    <form class="mt-6 flex flex-col gap-5" @submit.prevent="submit">
      <section class="panel flex flex-col gap-4">
        <h2 class="text-3xl font-semibold">About you</h2>
        <FormControl v-model="form.full_name" label="Full name" required />
        <FormControl
          v-model="form.whatsapp_number"
          type="tel"
          label="WhatsApp number"
          placeholder="0972 616 440"
          required
        />
        <FormControl v-model="form.nrc_number" label="NRC number" placeholder="123456/10/1" />
        <FormControl v-model="form.address" label="Address or town" />
      </section>

      <section class="panel flex flex-col gap-4">
        <h2 class="text-3xl font-semibold">Your loan</h2>
        <FormControl
          v-model="form.loan_plan"
          type="select"
          label="Loan plan"
          :options="planOptions"
          required
        />
        <FormControl
          v-model="form.amount"
          type="number"
          label="Amount (ZMW)"
          :description="amountHint"
          required
        />
        <FormControl v-model="form.purpose" type="select" label="Purpose" :options="purposes" />
        <RepaymentPreview v-if="showPreview" :plan="selectedPlan" :amount="Number(form.amount)" />
      </section>

      <section class="panel flex flex-col gap-4">
        <h2 class="text-3xl font-semibold">Your collateral</h2>
        <FormControl
          v-model="form.collateral_description"
          type="textarea"
          label="What are you offering as collateral?"
          placeholder="For example: Samsung 55 inch TV, 2 years old"
          required
        />
        <FormControl v-model="form.estimated_value" type="number" label="Estimated value (ZMW)" />
        <PhotoPicker v-model="form.photos" />
      </section>

      <ErrorMessage :message="errorMessage" />
      <button type="submit" class="gold-button disabled:opacity-60" :disabled="application.loading">
        {{ application.loading ? 'Sending…' : 'Submit application' }}
      </button>
    </form>
  </main>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ErrorMessage, FormControl, useCall } from 'frappe-ui'
import PhotoPicker from '@/components/PhotoPicker.vue'
import RepaymentPreview from '@/components/RepaymentPreview.vue'
import { formatMoney, useLoanPlans } from '@/data/plans'

const router = useRouter()
const purposes = ['Personal', 'Business', 'Asset Financing', 'Education']
const form = reactive({
  full_name: '',
  whatsapp_number: '',
  nrc_number: '',
  address: '',
  loan_plan: useRoute().query.plan || '',
  amount: null,
  purpose: '',
  collateral_description: '',
  estimated_value: null,
  photos: [],
})
const formError = ref('')

const plans = useLoanPlans()

const application = useCall({
  url: '/api/v2/method/epasi.api.public.submit_application',
  method: 'POST',
  immediate: false,
  onSuccess: (data) => router.push({ name: 'ThankYou', params: { application: data.name } }),
})

const planOptions = computed(() =>
  (plans.data || []).map((plan) => ({
    label: `${plan.name} at ${plan.interest_rate}%`,
    value: plan.name,
  })),
)

const selectedPlan = computed(() => (plans.data || []).find((plan) => plan.name === form.loan_plan))

const amountHint = computed(() => {
  const plan = selectedPlan.value
  return plan ? `Between ${formatMoney(plan.minimum_amount)} and ${formatMoney(plan.maximum_amount)}` : ''
})

const showPreview = computed(() => {
  const plan = selectedPlan.value
  const amount = Number(form.amount)
  return plan && amount >= plan.minimum_amount && amount <= plan.maximum_amount
})

const errorMessage = computed(
  () => formError.value || application.error?.message?.replace(/^\w+Error: /, ''),
)

function submit() {
  formError.value = form.photos.length ? '' : 'Add at least one photo of your collateral.'
  if (!formError.value) application.submit({ ...form })
}
</script>
