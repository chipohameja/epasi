<template>
  <main class="mx-auto w-full max-w-5xl px-4">
    <section class="grid items-center gap-8 py-10 sm:grid-cols-[auto_1fr] sm:py-16">
      <img :src="logoUrl" alt="Epasi Money Solutions" class="mx-auto w-36 sm:w-48" />
      <div class="text-center sm:text-left">
        <h1 class="text-8xl font-bold italic leading-tight sm:text-10xl">
          Fast. Reliable. Trusted.
        </h1>
        <p class="mt-3 text-2xl text-ink-gray-7">Quick money. Real support. Better tomorrow.</p>
        <ul class="mt-4 flex flex-wrap justify-center gap-2 sm:justify-start">
          <li
            v-for="badge in badges"
            :key="badge"
            class="rounded-full border border-gold-dark px-3 py-1 text-xs font-semibold uppercase tracking-wider text-gold-light"
          >
            {{ badge }}
          </li>
        </ul>
        <RouterLink :to="{ name: 'Apply' }" class="gold-button mt-6 inline-block"
          >Apply now</RouterLink
        >
      </div>
    </section>

    <section aria-labelledby="rates-heading">
      <p id="rates-heading" class="eyebrow text-center">Our money rates</p>
      <div class="mt-4 grid grid-cols-2 gap-3 sm:gap-5">
        <RouterLink
          v-for="(plan, index) in plans.data || []"
          :key="plan.name"
          :to="{ name: 'Apply', query: { plan: plan.name } }"
          :aria-label="`Apply for the ${plan.name} plan`"
        >
          <RateCard
            :plan="plan"
            :featured="index % 2 === 1"
            class="h-full transition hover:brightness-110"
          />
        </RouterLink>
      </div>
      <p class="mt-4 text-center text-base text-ink-gray-7">
        Flexible terms. Clear rates. <strong class="text-ink-gray-9">No hidden fees.</strong>
      </p>
      <p class="eyebrow mx-auto mt-3 w-fit border-y border-gold-dark px-4 py-2">
        Collateral based strictly
      </p>
    </section>

    <section class="mt-12 grid gap-5 sm:grid-cols-2">
      <div class="panel">
        <h2 class="text-4xl font-semibold">Our services</h2>
        <ul class="mt-4 flex flex-col gap-2">
          <li
            v-for="service in services"
            :key="service"
            class="flex items-center gap-3 text-lg text-ink-gray-8"
          >
            <span class="size-2 rounded-full bg-gold" aria-hidden="true" />{{ service }}
          </li>
        </ul>
      </div>
      <div class="panel">
        <h2 class="text-4xl font-semibold">How it works</h2>
        <ol class="mt-4 flex flex-col gap-3">
          <li v-for="(step, index) in steps" :key="step.title" class="flex gap-3">
            <span
              class="gold-gradient flex size-7 shrink-0 items-center justify-center rounded-full text-base font-bold text-night"
            >
              {{ index + 1 }}
            </span>
            <span>
              <span class="block font-semibold text-ink-gray-9">{{ step.title }}</span>
              <span class="text-base text-ink-gray-6">{{ step.text }}</span>
            </span>
          </li>
        </ol>
      </div>
    </section>

    <section class="mt-12" aria-labelledby="reviews-heading">
      <h2 id="reviews-heading" class="text-center text-4xl font-semibold">What our clients say</h2>
      <div class="mt-5 grid gap-5 sm:grid-cols-3">
        <ReviewCard v-for="review in reviewSlots" :key="review.comment" :review="review" />
      </div>
      <button
        type="button"
        class="mx-auto mt-5 block rounded-full border border-gold-dark px-5 py-2 font-semibold text-gold-light transition hover:bg-night-raised"
        @click="reviewOpen = true"
      >
        Leave a review
      </button>
      <ReviewDialog v-model:open="reviewOpen" :application="route.query.application || ''" />
    </section>

    <section class="panel mt-12 text-center">
      <h2 class="text-4xl font-semibold">Ready when you are</h2>
      <p class="mt-2 text-ink-gray-7">
        It takes about five minutes. Keep photos of your collateral ready.
      </p>
      <RouterLink :to="{ name: 'Apply' }" class="gold-button mt-5 inline-block"
        >Start my application</RouterLink
      >
    </section>
  </main>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import logoUrl from '@images/epasi-logo.png'
import RateCard from '@/components/RateCard.vue'
import ReviewCard from '@/components/ReviewCard.vue'
import ReviewDialog from '@/components/ReviewDialog.vue'
import { services } from '@/data/business'
import { useLoanPlans } from '@/data/plans'
import { fillReviewSlots, useReviews } from '@/data/reviews'

const route = useRoute()
const plans = useLoanPlans()
const reviews = useReviews()
const reviewSlots = computed(() => fillReviewSlots(reviews.data))
const reviewOpen = ref(Boolean(route.query.review))
const badges = ['Same-day payout', 'Safe & confidential']
const steps = [
  {
    title: 'Apply online',
    text: 'Tell us how much you need and describe your collateral with photos.',
  },
  { title: 'We call you on WhatsApp', text: 'A loan manager checks your details and collateral.' },
  { title: 'Get your money', text: 'Bring your collateral and receive your cash the same day.' },
]
</script>
