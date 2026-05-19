import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import { authState, initAuth } from '../stores/auth';

const routes = [
  {
    path: '/auth',
    name: 'auth',
    component: () => import('../views/AuthView.vue'),
    meta: { guestOnly: true, hideShell: true }
  },
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true }
  },
  {
    path: '/tribes',
    name: 'tribes',
    component: () => import('../views/TribesView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tribes/:id',
    name: 'tribe-detail',
    component: () => import('../views/TribeDetailView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/posts/:id',
    name: 'post-detail',
    component: () => import('../views/PostDetailView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/events/:id',
    name: 'event-detail',
    component: () => import('../views/EventDetailView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/messages',
    name: 'messages',
    component: () => import('../views/MessagesView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach(async (to) => {
  await initAuth();

  if (to.meta.requiresAuth && !authState.user) {
    return {
      name: 'auth',
      query: { redirect: to.fullPath }
    };
  }

  if (to.meta.guestOnly && authState.user) {
    return { path: '/' };
  }

  return true;
});

export default router;
