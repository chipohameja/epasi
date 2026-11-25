<script setup>
import { screenshotUrl } from "./guides";

defineProps({
	section: { type: Object, required: true },
	number: { type: Number, required: true },
});
</script>

<template>
	<section class="flex flex-col gap-3 rounded-lg border border-outline-gray-2 p-4">
		<h2 class="text-lg font-semibold text-ink-gray-9">{{ number }}. {{ section.title }}</h2>
		<p v-if="section.text" class="text-base text-ink-gray-8">{{ section.text }}</p>
		<ol
			v-if="section.steps"
			class="flex list-decimal flex-col gap-1 pl-5 text-base text-ink-gray-8"
		>
			<li v-for="step in section.steps" :key="step">{{ step }}</li>
		</ol>
		<figure v-if="section.image" :class="section.image.phone ? 'mx-auto max-w-xs' : ''">
			<img
				:src="screenshotUrl(section.image.file)"
				:alt="section.image.alt"
				loading="lazy"
				class="w-full rounded border border-outline-gray-2"
			/>
			<figcaption class="mt-1 text-center text-sm text-ink-gray-6">
				{{ section.image.alt }}
			</figcaption>
		</figure>
		<div v-if="section.example" class="rounded bg-surface-gray-2 p-3">
			<p class="text-sm font-medium text-ink-gray-7">Example</p>
			<p v-for="line in section.example" :key="line" class="mt-1 text-base text-ink-gray-8">
				{{ line }}
			</p>
		</div>
		<p v-if="section.tip" class="rounded bg-surface-blue-1 p-3 text-base text-ink-gray-8">
			<strong>Tip:</strong> {{ section.tip }}
		</p>
	</section>
</template>
