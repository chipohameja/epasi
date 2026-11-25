import { createRouter, createWebHistory } from 'vue-router'
import { saveReferral } from '@/utils/referral'
import { isLoggedIn, loginUrl } from '@/utils/session'

const routes = [
  { path: '/', name: 'Home', component: () => import('@/pages/Home.vue') },
  { path: '/apply', name: 'Apply', component: () => import('@/pages/Apply.vue') },
  {
    path: '/thank-you/:application',
    name: 'ThankYou',
    component: () => import('@/pages/ThankYou.vue'),
    props: true,
  },
  {
    path: '/partner',
    name: 'Partner',
    component: () => import('@/pages/Partner.vue'),
    meta: { requiresLogin: true },
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory('/epasi'),
  routes,
  scrollBehavior: (to) => (to.hash ? { el: to.hash, top: 16 } : { top: 0 }),
})

router.beforeEach((to) => {
  saveReferral(to.query.ref)
  if (to.meta.requiresLogin && !isLoggedIn()) {
    window.location.href = loginUrl(`/epasi${to.fullPath}`)
    return false
  }
})

export default router
