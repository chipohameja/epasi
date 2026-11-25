<script setup>
import { guides } from "./guides";

defineEmits(["open"]);
</script>

<template>
	<div class="mx-auto max-w-3xl">
		<p class="text-base text-ink-gray-7">Choose a type of user to see their guide.</p>
		<ul class="mt-4 grid gap-3 sm:grid-cols-2">
			<li v-for="guide in guides" :key="guide.slug">
				<button
					class="h-full w-full rounded-lg border border-outline-gray-2 p-4 text-left hover:bg-surface-gray-2"
					@click="$emit('open', guide.slug)"
				>
					<span class="block text-lg font-semibold text-ink-gray-9">{{
						guide.title
					}}</span>
					<span class="mt-1 block text-base text-ink-gray-8">{{ guide.who }}</span>
					<span class="mt-2 block text-sm text-ink-gray-6">{{ guide.summary }}</span>
				</button>
			</li>
		</ul>
	</div>
</template>
