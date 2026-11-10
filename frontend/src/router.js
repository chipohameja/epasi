import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('@/pages/Home.vue') },
  { path: '/apply', name: 'Apply', component: () => import('@/pages/Apply.vue') },
  {
    path: '/thank-you/:application',
    name: 'ThankYou',
    component: () => import('@/pages/ThankYou.vue'),
    props: true,
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export default createRouter({
  history: createWebHistory('/epasi'),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})
