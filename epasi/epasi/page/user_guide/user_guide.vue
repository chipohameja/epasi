<script setup>
import { computed, watchEffect } from "vue";
import { useHost } from "@framework/ui/island";
import GuideList from "./guide_list.vue";
import GuideView from "./guide_view.vue";
import { findGuide } from "./guides";

const props = defineProps({
	route: { type: Array, default: () => [] },
	query: { type: Object, default: () => ({}) },
});
const emit = defineEmits(["title", "actions"]);
const host = useHost();

const guide = computed(() => findGuide(props.route[0]));
const open = (slug) => host.navigate?.(slug ? `user-guide/${slug}` : "user-guide");

watchEffect(() => {
	emit("title", guide.value ? `${guide.value.title} Guide` : "User Guide");
	emit("actions", guide.value ? [{ label: "All guides", onClick: () => open() }] : []);
});
</script>

<template>
	<div class="h-full overflow-y-auto p-5">
		<GuideView v-if="guide" :guide="guide" @back="open()" />
		<GuideList v-else @open="open" />
	</div>
</template>
