import { mountVueIsland } from "@framework/ui/island";

import Page from "./user_guide.vue";

export const mount = (el, context) => mountVueIsland(el, { ...context, component: Page });
