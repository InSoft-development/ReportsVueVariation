import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/settings',
      name: 'settings',
      // route level code-splitting
      // this generates a separate chunk (Settings.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/SettingsView.vue')
    },
    {
      path: '/interval/:intervalsId',
      name: 'interval',
      // route level code-splitting
      // this generates a separate chunk (interval.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import(/* webpackChunkName: "interval" */ '../views/IntervalView.vue')
    },
    {
      path: '/addition',
      name: 'addition',
      // route level code-splitting
      // this generates a separate chunk (addition.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import(/* webpackChunkName: "addition" */ '../views/AdditionView.vue')
    }
  ]
})

export default router
