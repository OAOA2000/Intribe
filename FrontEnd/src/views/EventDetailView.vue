<template>
  <div class="container mx-auto px-4 py-6">
    <button class="mb-4 text-sm text-primary hover:underline" @click="router.back()">返回</button>

    <div v-if="loading" class="card p-6 text-sm text-gray-500">活动加载中...</div>
    <div v-else-if="error" class="card p-6 text-sm text-red-600">{{ error }}</div>

    <article v-else-if="event" class="card p-6">
      <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p class="text-sm text-gray-500">{{ event.tribes?.name || '校园活动' }}</p>
          <h2 class="mt-1 text-3xl font-bold">{{ event.title }}</h2>
        </div>
        <span class="w-fit rounded-full bg-accent/20 px-3 py-1 text-sm text-accent">{{ statusLabel(event.status) }}</span>
      </div>

      <div class="mb-6 grid gap-3 md:grid-cols-2">
        <div class="rounded-lg bg-gray-50 p-4">
          <p class="text-xs text-gray-500">时间</p>
          <p class="mt-1 font-medium">{{ formatDate(event.start_time) }}</p>
        </div>
        <div class="rounded-lg bg-gray-50 p-4">
          <p class="text-xs text-gray-500">地点</p>
          <p class="mt-1 font-medium">{{ event.location || '地点待定' }}</p>
        </div>
      </div>

      <p class="whitespace-pre-line text-gray-700">{{ event.description || '暂无活动介绍' }}</p>
    </article>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { api } from '../services/api';

const route = useRoute();
const router = useRouter();
const loading = ref(false);
const error = ref('');
const event = ref(null);

const statusLabel = (status) => {
  const map = {
    recruiting: '招募中',
    ongoing: '进行中',
    finished: '已结束',
    cancelled: '已取消'
  };
  return map[status] || status || '待定';
};

const formatDate = (value) => {
  if (!value) {
    return '时间待定';
  }
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value));
};

const loadEvent = async () => {
  loading.value = true;
  error.value = '';

  try {
    event.value = await api.get(`/events/${route.params.id}`);
  } catch (err) {
    error.value = err.message || '加载活动详情失败';
  } finally {
    loading.value = false;
  }
};

onMounted(loadEvent);
</script>
