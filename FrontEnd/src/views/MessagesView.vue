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
          <div class="flex flex-wrap items-center justify-end gap-2">
            <button
              v-if="group.key !== 'system' && !selectionMode"
              class="inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-primary/10 px-3 py-1.5 text-xs font-medium text-primary hover:bg-primary/15 disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              :disabled="digestLoading && activeDigestTribeId === group.key"
              @click="openTribeDigest(group)"
            >
              <Sparkles class="h-3.5 w-3.5" />
              {{ digestLoading && activeDigestTribeId === group.key ? '总结中...' : '总结今日动态' }}
            </button>
            <span v-if="group.unreadCount" class="rounded-full bg-red-50 px-3 py-1 text-xs text-red-600">
              {{ group.unreadCount }} 条未读
            </span>
          </div>
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

    <div
      v-if="digestDialogOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-gray-950/40 px-4 py-6 backdrop-blur-sm"
      @click.self="closeDigestDialog"
    >
      <section class="max-h-[86vh] w-full max-w-2xl overflow-hidden rounded-3xl border border-white/70 bg-white/90 shadow-2xl backdrop-blur">
        <header class="flex items-start justify-between gap-4 border-b border-gray-100 px-6 py-5">
          <div>
            <p class="text-xs font-medium uppercase tracking-wide text-primary">今日部落动态</p>
            <h3 class="mt-1 text-2xl font-bold text-gray-900">{{ digestTribeName || '兴趣部落' }}</h3>
          </div>
          <button
            class="rounded-full bg-gray-100 p-2 text-gray-500 hover:bg-gray-200"
            type="button"
            aria-label="关闭"
            @click="closeDigestDialog"
          >
            <X class="h-5 w-5" />
          </button>
        </header>

        <div class="max-h-[62vh] overflow-y-auto px-6 py-5">
          <div v-if="digestLoading" class="rounded-2xl bg-primary/5 p-5 text-sm text-primary">
            AI 正在整理今天的部落动态...
          </div>

          <div v-else-if="digestError" class="rounded-2xl bg-red-50 p-5 text-sm text-red-600">
            {{ digestError }}
          </div>

          <div v-else-if="digestEmpty" class="rounded-2xl bg-gray-50 p-5 text-sm text-gray-500">
            暂无明显动态，今天这个部落还比较安静。
          </div>

          <div v-else class="space-y-5" data-digest-content>
            <p class="rounded-2xl bg-primary/5 p-4 text-sm leading-7 text-gray-700">{{ digestResult.summary }}</p>

            <div v-if="digestResult.highlights?.length" class="space-y-3">
              <h4 class="text-sm font-semibold text-gray-900">重点动态</h4>
              <article
                v-for="(item, index) in digestResult.highlights"
                :key="`${item.type}-${item.target_id || index}`"
                class="rounded-2xl border border-gray-100 bg-white/80 p-4"
              >
                <div class="mb-2 flex items-center gap-2">
                  <span class="rounded-full bg-gray-100 px-2.5 py-1 text-xs text-gray-600">{{ highlightTypeLabel(item.type) }}</span>
                  <h5 class="font-semibold text-gray-900">{{ item.title }}</h5>
                </div>
                <p class="text-sm leading-6 text-gray-600">{{ item.description }}</p>
              </article>
            </div>

            <div v-if="digestResult.todos?.length" class="space-y-2 rounded-2xl bg-amber-50 p-4">
              <h4 class="text-sm font-semibold text-amber-900">待关注</h4>
              <ul class="space-y-2 text-sm text-amber-800">
                <li v-for="todo in digestResult.todos" :key="todo">- {{ todo }}</li>
              </ul>
            </div>

            <div class="space-y-2">
              <label class="text-sm font-semibold text-gray-900" for="digest-copy-text">复制文本</label>
              <textarea
                id="digest-copy-text"
                ref="digestCopyTextArea"
                class="h-28 w-full resize-none rounded-2xl border border-gray-100 bg-white/80 p-3 text-sm leading-6 text-gray-700 outline-none focus:border-primary/40 focus:ring-2 focus:ring-primary/10"
                readonly
                :value="digestText"
                @focus="$event.target.select()"
              ></textarea>
            </div>
          </div>
        </div>

        <footer class="flex flex-col gap-2 border-t border-gray-100 px-6 py-4 sm:flex-row sm:justify-end">
          <p
            v-if="digestCopyMessage"
            class="flex-1 rounded-xl px-3 py-2 text-sm"
            :class="digestCopied ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'"
          >
            {{ digestCopyMessage }}
          </p>
          <button
            class="inline-flex items-center justify-center gap-2 rounded-xl bg-gray-100 px-4 py-2 text-sm text-gray-700 hover:bg-gray-200 disabled:opacity-60"
            type="button"
            :disabled="digestLoading || !digestText"
            @click.stop.prevent="copyDigest"
          >
            <Check v-if="digestCopied" class="h-4 w-4" />
            <Copy v-else class="h-4 w-4" />
            {{ digestCopied ? '已复制' : '一键复制' }}
          </button>
          <button class="btn-primary px-4 py-2 text-sm" type="button" @click="closeDigestDialog">完成</button>
        </footer>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { Activity, Bell, Check, Code, Copy, Guitar, Sparkles, Users, X } from 'lucide-vue-next';
import { api } from '../services/api';
import { aiApi } from '../services/aiApi';

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
const digestDialogOpen = ref(false);
const digestLoading = ref(false);
const digestError = ref('');
const digestResult = ref(null);
const digestTribeName = ref('');
const activeDigestTribeId = ref('');
const digestCopied = ref(false);
const digestCopyMessage = ref('');
const digestCopyTextArea = ref(null);

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

const digestEmpty = computed(() => {
  if (!digestResult.value) {
    return false;
  }
  return !digestResult.value.highlights?.length && !digestResult.value.todos?.length;
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

const closeDigestDialog = () => {
  if (digestLoading.value) {
    return;
  }
  digestDialogOpen.value = false;
};

const openTribeDigest = async (group) => {
  digestDialogOpen.value = true;
  digestLoading.value = true;
  digestError.value = '';
  digestResult.value = null;
  digestCopied.value = false;
  digestCopyMessage.value = '';
  digestTribeName.value = group.name;
  activeDigestTribeId.value = group.key;

  try {
    digestResult.value = await aiApi.generateTribeDigest({
      tribe_id: group.key,
      time_range: 'today'
    });
  } catch (err) {
    digestError.value = err.message || 'AI 总结生成失败，请稍后重试';
  } finally {
    digestLoading.value = false;
    activeDigestTribeId.value = '';
  }
};

const highlightTypeLabel = (type) => {
  const labels = {
    post: '帖子',
    comment: '评论',
    event: '活动',
    todo: '待办'
  };
  return labels[type] || '动态';
};

const digestText = computed(() => {
  if (!digestResult.value) {
    return '';
  }
  const parts = [`${digestTribeName.value} 今日部落动态`, digestResult.value.summary || '暂无明显动态。'];
  if (digestResult.value.highlights?.length) {
    parts.push(
      '重点动态：',
      ...digestResult.value.highlights.map((item) => `- ${item.title}：${item.description}`)
    );
  }
  if (digestResult.value.todos?.length) {
    parts.push('待关注：', ...digestResult.value.todos.map((todo) => `- ${todo}`));
  }
  return parts.join('\n');
});

const selectCopyTextArea = () => {
  const textArea = digestCopyTextArea.value;
  if (!textArea) {
    return false;
  }
  textArea.focus({ preventScroll: true });
  textArea.select();
  textArea.setSelectionRange(0, textArea.value.length);
  return true;
};

const copySelectedDigestText = () => {
  if (!selectCopyTextArea()) {
    return false;
  }
  try {
    return document.execCommand('copy');
  } catch (err) {
    return false;
  }
};

const writeClipboardText = async (text) => {
  if (copySelectedDigestText()) {
    return true;
  }

  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return true;
  }

  throw new Error('copy command failed');
};

const showCopyMessage = (message, copied) => {
  digestCopied.value = copied;
  digestCopyMessage.value = message;
  window.setTimeout(() => {
    if (digestCopyMessage.value === message) {
      digestCopied.value = false;
      digestCopyMessage.value = '';
    }
  }, copied ? 1800 : 2600);
};

const copyDigest = async () => {
  const text = digestText.value;
  if (!text) {
    showCopyMessage('暂无可复制内容', false);
    return;
  }

  try {
    await writeClipboardText(text);
    showCopyMessage('已复制到剪贴板', true);
  } catch (err) {
    selectCopyTextArea();
    showCopyMessage('自动复制失败，已选中下方文本，可按 Ctrl/Cmd + C 复制', false);
  }
};

onMounted(loadMessages);
</script>

<style scoped>
/* 自定义样式 */
</style>
