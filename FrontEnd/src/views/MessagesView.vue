<template>
  <div class="container mx-auto px-4 py-6">
    <h2 class="text-3xl font-bold mb-6">消息中心</h2>
    <p v-if="loading" class="mb-4 text-sm text-gray-500">加载中...</p>
    <p v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</p>
    
    <!-- 消息列表 -->
    <div class="space-y-3">
      <button
        v-for="message in messages"
        :key="message.id"
        type="button"
        class="card p-4 flex items-center gap-4 w-full text-left"
        @click="markAsRead(message)"
      >
        <div class="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center relative">
          <component :is="getMessageIcon(message.type)" class="w-6 h-6 text-primary" />
          <span v-if="message.unread" class="absolute w-3 h-3 bg-red-500 rounded-full -bottom-1 -right-1"></span>
        </div>
        <div class="flex-1">
          <div class="flex justify-between items-center mb-1">
            <h4 class="font-semibold">{{ message.sender }}</h4>
            <span class="text-xs text-gray-500">{{ message.time }}</span>
          </div>
          <p class="text-sm text-gray-600 truncate">{{ message.content }}</p>
        </div>
      </button>
    </div>
    <p v-if="!loading && messages.length === 0" class="text-sm text-gray-500">暂无消息</p>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { Code, Activity, Guitar, Bell, Users } from 'lucide-vue-next';
import { api } from '../services/api';

// 获取消息图标
const getMessageIcon = (type) => {
  switch (type) {
    case 'programming':
      return Code;
    case 'sports':
      return Activity;
    case 'music':
      return Guitar;
    case 'system':
      return Bell;
    default:
      return Users;
  }
};

const messages = ref([]);
const loading = ref(false);
const error = ref('');

const formatTime = (value) => {
  if (!value) {
    return '';
  }
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value));
};

const normalizeMessage = (message) => ({
  ...message,
  sender: message.tribes?.name || message.events?.title || message.title || '系统通知',
  time: formatTime(message.created_at),
  unread: !message.is_read
});

const loadMessages = async () => {
  loading.value = true;
  error.value = '';

  try {
    const rows = await api.get('/messages');
    messages.value = rows.map(normalizeMessage);
  } catch (err) {
    error.value = err.message || '加载消息失败';
  } finally {
    loading.value = false;
  }
};

const markAsRead = async (message) => {
  if (!message.unread) {
    return;
  }

  try {
    const updated = await api.patch(`/messages/${message.id}/read`);
    const index = messages.value.findIndex((item) => item.id === message.id);
    if (index >= 0) {
      messages.value[index] = normalizeMessage(updated);
    }
  } catch (err) {
    error.value = err.message || '标记已读失败';
  }
};

onMounted(loadMessages);
</script>

<style scoped>
/* 自定义样式 */
</style>
