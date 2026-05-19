<template>
  <div class="container mx-auto px-4 py-6">
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 class="text-3xl font-bold">消息中心</h2>
        <p v-if="selectionMode" class="mt-1 text-sm text-gray-500">已选择 {{ selectedMessageIds.size }} 条消息</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <button
          v-if="!selectionMode"
          class="rounded-lg bg-gray-100 px-4 py-2 text-sm text-gray-700 hover:bg-gray-200"
          type="button"
          @click="selectionMode = true"
        >
          选择消息
        </button>
        <button
          v-if="!selectionMode && unreadMessages.length"
          class="btn-secondary text-sm"
          type="button"
          @click="markAllAsRead"
        >
          一键已读
        </button>
        <button
          v-if="selectionMode"
          class="rounded-lg bg-gray-100 px-4 py-2 text-sm text-gray-700 hover:bg-gray-200"
          type="button"
          @click="toggleSelectAll"
        >
          {{ allSelected ? '取消全选' : '全部选择' }}
        </button>
        <button
          v-if="selectionMode"
          class="rounded-lg bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700 disabled:opacity-60"
          type="button"
          :disabled="selectedMessageIds.size === 0"
          @click="deleteSelectedMessages"
        >
          删除已选
        </button>
        <button
          v-if="selectionMode"
          class="rounded-lg bg-gray-100 px-4 py-2 text-sm text-gray-700 hover:bg-gray-200"
          type="button"
          @click="exitSelectionMode"
        >
          退出选择
        </button>
      </div>
    </div>
    <p v-if="loading" class="mb-4 text-sm text-gray-500">加载中...</p>
    <p v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</p>
    
    <div class="space-y-6">
      <section v-for="group in groupedMessages" :key="group.key" class="rounded-2xl bg-white p-4 shadow-md">
        <div class="mb-3 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="flex h-10 w-10 items-center justify-center rounded-full bg-primary/15">
              <Users class="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 class="font-semibold">{{ group.name }}</h3>
              <p class="text-xs text-gray-500">{{ group.items.length }} 条消息</p>
            </div>
          </div>
          <span v-if="group.unreadCount" class="rounded-full bg-red-50 px-3 py-1 text-xs text-red-600">
            {{ group.unreadCount }} 条未读
          </span>
        </div>

        <div class="space-y-3">
          <article
            v-for="message in group.items"
            :key="message.id"
            class="rounded-xl border border-gray-100 p-4"
            :class="message.unread ? 'bg-primary/5' : 'bg-gray-50'"
          >
            <div class="flex items-start gap-4">
              <label v-if="selectionMode" class="mt-3 flex shrink-0 items-center">
                <input
                  class="h-5 w-5 rounded border-gray-300 text-primary focus:ring-primary"
                  type="checkbox"
                  :checked="selectedMessageIds.has(message.id)"
                  @change="toggleMessageSelection(message.id)"
                />
              </label>
              <div class="relative flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary/20">
                <component :is="getMessageIcon(message.type)" class="h-6 w-6 text-primary" />
                <span v-if="message.unread" class="absolute -bottom-1 -right-1 h-3 w-3 rounded-full bg-red-500"></span>
              </div>
              <div class="min-w-0 flex-1">
                <div class="mb-1 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                  <h4 class="font-semibold">{{ message.title || '部落消息' }}</h4>
                  <span class="text-xs text-gray-500">{{ message.time }}</span>
                </div>
                <p class="text-sm leading-6 text-gray-600">{{ message.content }}</p>
              </div>
              <div class="flex shrink-0 flex-col gap-2">
                <button
                  v-if="message.post_id && !selectionMode"
                  class="btn-primary px-3 py-1.5 text-sm"
                  type="button"
                  @click="goToMessage(message)"
                >
                  前往
                </button>
                <button
                  v-if="message.unread && !selectionMode"
                  class="rounded-lg bg-gray-100 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-200"
                  type="button"
                  @click="markAsRead(message)"
                >
                  已读
                </button>
                <button
                  v-if="!selectionMode"
                  class="rounded-lg bg-red-50 px-3 py-1.5 text-sm text-red-600 hover:bg-red-100"
                  type="button"
                  @click="deleteSingleMessage(message)"
                >
                  删除
                </button>
              </div>
            </div>
          </article>
        </div>
      </section>
    </div>
    <p v-if="!loading && messages.length === 0" class="text-sm text-gray-500">暂无消息</p>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { Code, Activity, Guitar, Bell, Users } from 'lucide-vue-next';
import { api } from '../services/api';

const router = useRouter();

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
const selectionMode = ref(false);
const selectedMessageIds = ref(new Set());

const unreadMessages = computed(() => messages.value.filter((message) => message.unread));
const allSelected = computed(() => messages.value.length > 0 && selectedMessageIds.value.size === messages.value.length);

const groupedMessages = computed(() => {
  const groups = new Map();
  messages.value.forEach((message) => {
    const key = message.tribe_id || 'system';
    if (!groups.has(key)) {
      groups.set(key, {
        key,
        name: message.tribes?.name || '系统通知',
        items: [],
        unreadCount: 0
      });
    }
    const group = groups.get(key);
    group.items.push(message);
    if (message.unread) {
      group.unreadCount += 1;
    }
  });
  return Array.from(groups.values());
});

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
  time: formatTime(message.created_at),
  unread: !message.is_read
});

const loadMessages = async () => {
  loading.value = true;
  error.value = '';

  try {
    const rows = await api.get('/messages');
    messages.value = rows.map(normalizeMessage);
    window.dispatchEvent(new CustomEvent('messages-updated'));
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
    await api.patch(`/messages/${message.id}/read`);
    const index = messages.value.findIndex((item) => item.id === message.id);
    if (index >= 0) {
      messages.value[index] = {
        ...messages.value[index],
        is_read: true,
        unread: false
      };
      window.dispatchEvent(new CustomEvent('messages-updated'));
    }
  } catch (err) {
    error.value = err.message || '标记已读失败';
  }
};

const markAllAsRead = async () => {
  if (!unreadMessages.value.length) {
    return;
  }

  error.value = '';
  try {
    await api.patch('/messages/read-all');
    messages.value = messages.value.map((message) => ({
      ...message,
      is_read: true,
      unread: false
    }));
    window.dispatchEvent(new CustomEvent('messages-updated'));
  } catch (err) {
    error.value = err.message || '一键已读失败';
  }
};

const removeMessagesLocally = (ids) => {
  const idSet = new Set(ids);
  messages.value = messages.value.filter((message) => !idSet.has(message.id));
  selectedMessageIds.value = new Set([...selectedMessageIds.value].filter((id) => !idSet.has(id)));
  window.dispatchEvent(new CustomEvent('messages-updated'));
};

const deleteSingleMessage = async (message) => {
  error.value = '';

  try {
    await api.delete(`/messages/${message.id}`);
    removeMessagesLocally([message.id]);
  } catch (err) {
    error.value = err.message || '删除消息失败';
  }
};

const toggleMessageSelection = (messageId) => {
  const next = new Set(selectedMessageIds.value);
  if (next.has(messageId)) {
    next.delete(messageId);
  } else {
    next.add(messageId);
  }
  selectedMessageIds.value = next;
};

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedMessageIds.value = new Set();
    return;
  }
  selectedMessageIds.value = new Set(messages.value.map((message) => message.id));
};

const exitSelectionMode = () => {
  selectionMode.value = false;
  selectedMessageIds.value = new Set();
};

const deleteSelectedMessages = async () => {
  const ids = [...selectedMessageIds.value];
  if (!ids.length) {
    return;
  }

  error.value = '';
  try {
    await api.post('/messages/bulk-delete', { message_ids: ids });
    removeMessagesLocally(ids);
    if (messages.value.length === 0) {
      exitSelectionMode();
    }
  } catch (err) {
    error.value = err.message || '删除已选消息失败';
  }
};

const goToMessage = async (message) => {
  if (message.unread) {
    await markAsRead(message);
  }
  const hash = message.comment_id ? `#comment-${message.comment_id}` : '';
  await router.push(`/posts/${message.post_id}${hash}`);
};

onMounted(loadMessages);
</script>

<style scoped>
/* 自定义样式 */
</style>
