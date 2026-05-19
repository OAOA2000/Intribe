<template>
  <router-view v-if="hideShell" />

  <div v-else class="min-h-screen flex flex-col">
    <header class="glass-effect fixed top-0 left-0 right-0 z-50 py-3 px-4">
      <div class="container mx-auto flex items-center justify-between">
        <h1 class="text-xl font-bold text-primary">兴趣部落</h1>
        <div class="flex items-center gap-4">
          <div class="relative hidden md:block">
            <form class="flex items-center gap-2" @submit.prevent="submitSearch">
              <input
                v-model="searchKeyword"
                type="text"
                placeholder="搜索兴趣部落或活动..."
                class="w-64 px-4 py-2 rounded-full bg-white/80 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
              <button
                type="submit"
                class="px-4 py-2 rounded-full bg-primary text-white hover:bg-primary/90 active:scale-95 transition-all duration-200"
              >
                搜索
              </button>
            </form>
          </div>
          <div class="relative">
            <button
              type="button"
              class="p-2 rounded-full hover:bg-gray-100 transition-colors"
              @click="router.push('/messages')"
            >
              <Bell class="w-6 h-6" />
              <span
                v-if="unreadCount > 0"
                class="absolute top-1 right-1 min-h-2 min-w-2 rounded-full bg-red-500"
                :class="unreadCount > 9 ? 'px-1 text-[10px] leading-4 text-white' : 'h-2 w-2'"
              >
                {{ unreadCount > 9 ? '9+' : '' }}
              </span>
            </button>
          </div>
          <div class="hidden md:flex items-center gap-2 text-sm text-gray-600">
            <span class="truncate max-w-40">{{ userLabel }}</span>
            <button
              type="button"
              class="px-3 py-1.5 rounded-full bg-white border border-gray-200 hover:bg-gray-50 transition-colors"
              :disabled="isSigningOut"
              @click="handleSignOut"
            >
              退出
            </button>
          </div>
          <div class="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
            <User class="w-6 h-6 text-primary" />
          </div>
        </div>
      </div>
    </header>

    <main class="flex-1 pt-16 pb-20 md:pb-0 md:pl-64">
      <router-view />
    </main>

    <aside class="fixed top-16 left-0 bottom-0 w-64 glass-effect hidden md:block z-40">
      <nav class="py-6 px-4">
        <ul class="space-y-2">
          <li>
            <router-link to="/" class="nav-item" active-class="active">
              <Compass class="w-6 h-6 mb-1" />
              <span class="text-sm">发现</span>
            </router-link>
          </li>
          <li>
            <router-link to="/tribes" class="nav-item" active-class="active">
              <Users class="w-6 h-6 mb-1" />
              <span class="text-sm">部落</span>
            </router-link>
          </li>
          <li>
            <router-link to="/messages" class="nav-item relative" active-class="active">
              <MessageCircle class="w-6 h-6 mb-1" />
              <span v-if="unreadCount > 0" class="absolute right-4 top-1 h-2 w-2 rounded-full bg-red-500"></span>
              <span class="text-sm">消息</span>
            </router-link>
          </li>
          <li>
            <router-link to="/profile" class="nav-item" active-class="active">
              <User class="w-6 h-6 mb-1" />
              <span class="text-sm">个人</span>
            </router-link>
          </li>
          <li class="mt-8">
            <router-link to="/dashboard" class="nav-item" active-class="active">
              <BarChart2 class="w-6 h-6 mb-1" />
              <span class="text-sm">管理中台</span>
            </router-link>
          </li>
        </ul>
      </nav>
    </aside>

    <nav class="fixed bottom-0 left-0 right-0 glass-effect z-40 md:hidden">
      <div class="flex justify-around items-center py-3">
        <router-link to="/" class="nav-item" active-class="active">
          <Compass class="w-6 h-6" />
          <span class="text-xs mt-1">发现</span>
        </router-link>
        <router-link to="/tribes" class="nav-item" active-class="active">
          <Users class="w-6 h-6" />
          <span class="text-xs mt-1">部落</span>
        </router-link>
        <router-link to="/messages" class="nav-item relative" active-class="active">
          <MessageCircle class="w-6 h-6" />
          <span v-if="unreadCount > 0" class="absolute right-4 top-1 h-2 w-2 rounded-full bg-red-500"></span>
          <span class="text-xs mt-1">消息</span>
        </router-link>
        <router-link to="/profile" class="nav-item" active-class="active">
          <User class="w-6 h-6" />
          <span class="text-xs mt-1">个人</span>
        </router-link>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Bell, User, Compass, Users, MessageCircle, BarChart2 } from 'lucide-vue-next';
import { authState, signOutUser } from './stores/auth';
import { api } from './services/api';

const route = useRoute();
const router = useRouter();
const isSigningOut = ref(false);
const searchKeyword = ref('');
const unreadCount = ref(0);

const hideShell = computed(() => Boolean(route.meta.hideShell));
const userLabel = computed(() => authState.user?.email || '未登录');

watch(
  () => route.query.search,
  (value) => {
    searchKeyword.value = typeof value === 'string' ? value : '';
  },
  { immediate: true }
);

watch(
  () => [authState.user?.id, route.fullPath],
  () => {
    loadUnreadCount();
  },
  { immediate: true }
);

async function loadUnreadCount() {
  if (!authState.user || hideShell.value) {
    unreadCount.value = 0;
    return;
  }

  try {
    const data = await api.get('/messages/unread-count');
    unreadCount.value = data?.count || 0;
  } catch (_err) {
    unreadCount.value = 0;
  }
}

const handleMessagesUpdated = () => {
  loadUnreadCount();
};

onMounted(() => {
  window.addEventListener('messages-updated', handleMessagesUpdated);
});

onBeforeUnmount(() => {
  window.removeEventListener('messages-updated', handleMessagesUpdated);
});

const submitSearch = async () => {
  const keyword = searchKeyword.value.trim();
  await router.push({
    path: '/',
    query: keyword ? { search: keyword } : {}
  });
};

const handleSignOut = async () => {
  isSigningOut.value = true;

  try {
    await signOutUser();
  } finally {
    isSigningOut.value = false;
    await router.replace('/auth');
  }
};
</script>
