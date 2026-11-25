<script setup>
import { Button } from "frappe-ui";
import GuideSection from "./guide_section.vue";

defineProps({ guide: { type: Object, required: true } });
defineEmits(["back"]);
</script>

<template>
	<div class="mx-auto flex max-w-3xl flex-col gap-4">
		<Button class="self-start" variant="ghost" @click="$emit('back')"> All guides </Button>
		<p class="text-base text-ink-gray-7">{{ guide.who }} {{ guide.summary }}</p>
		<GuideSection
			v-for="(section, index) in guide.sections"
			:key="section.title"
			:section="section"
			:number="index + 1"
		/>
	</div>
</template>
