<template>
  <div class="container mx-auto px-4 py-6">
    <button class="mb-4 text-sm text-primary hover:underline" type="button" @click="goBack">返回部落</button>

    <p v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</p>
    <p v-if="actionMessage" class="mb-4 text-sm text-primary">{{ actionMessage }}</p>
    <p v-if="loading" class="mb-4 text-sm text-gray-500">加载中...</p>

    <article v-if="post" class="mb-6 rounded-2xl bg-white p-5 shadow-md">
      <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <p class="mb-2 text-sm text-primary">{{ post.tribes?.name || '部落讨论' }}</p>
          <h2 class="text-2xl font-bold">{{ post.title }}</h2>
          <p class="mt-2 text-xs text-gray-500">
            {{ post.author?.display_name || '校园同学' }} · {{ formatDate(post.created_at) }}
          </p>
        </div>
        <div v-if="post.can_edit || post.can_delete" class="flex gap-2">
          <button
            v-if="post.can_edit"
            class="rounded-lg bg-gray-100 px-4 py-2 text-sm text-gray-700 hover:bg-gray-200"
            @click="startEdit"
          >
            编辑
          </button>
          <button
            v-if="post.can_delete"
            class="rounded-lg bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700"
            @click="deletePost"
          >
            删除
          </button>
        </div>
      </div>

      <form v-if="editingPost" class="mt-5 space-y-3" @submit.prevent="updatePost">
        <input
          v-model="postEdit.title"
          class="w-full rounded-lg border border-gray-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary/40"
          type="text"
        />
        <textarea
          v-model="postEdit.content"
          class="w-full rounded-lg border border-gray-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary/40"
          rows="6"
        />
        <div class="flex gap-2">
          <button class="btn-primary" type="submit">保存</button>
          <button class="rounded-lg bg-gray-200 px-4 py-2 text-gray-700" type="button" @click="editingPost = false">
            取消
          </button>
        </div>
      </form>
      <p v-else class="mt-5 whitespace-pre-line text-sm leading-7 text-gray-700">{{ post.content }}</p>
    </article>

    <section v-if="post" class="mb-6 rounded-2xl border border-primary/10 bg-white p-5 shadow-md">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p class="text-xs font-medium uppercase tracking-wide text-primary">AI 总结</p>
          <h3 class="mt-1 text-lg font-semibold text-gray-900">讨论速览</h3>
        </div>
        <button
          class="inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-60"
          type="button"
          :disabled="summaryLoading"
          @click="openPostSummary"
        >
          <Sparkles class="h-4 w-4" />
          {{ summaryLoading ? '总结中...' : 'AI 总结讨论' }}
        </button>
      </div>
      <p class="mt-3 text-sm leading-6 text-gray-500">
        总结会基于当前帖子正文和可见评论临时生成，不会写入数据库。
      </p>
    </section>

    <section v-if="post" class="rounded-2xl bg-white p-5 shadow-md">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-xl font-semibold">评论</h3>
        <span class="text-sm text-gray-500">{{ post.comment_count || 0 }} 条</span>
      </div>

      <form class="mb-6 space-y-3" @submit.prevent="createComment()">
        <textarea
          v-model="commentContent"
          class="w-full rounded-lg border border-gray-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary/40"
          placeholder="写下你的评论..."
          rows="4"
        />
        <button class="btn-secondary disabled:opacity-60" type="submit" :disabled="commenting || !commentContent.trim()">
          {{ commenting ? '发布中...' : '发布评论' }}
        </button>
      </form>

      <div class="space-y-4">
        <CommentNode
          v-for="comment in post.comments"
          :key="comment.id"
          :comment="comment"
          :current-user-id="currentUserId"
          @reply="createComment"
          @delete="deleteComment"
          @update="updateComment"
        />
      </div>

      <p v-if="!loading && !post.comments?.length" class="text-sm text-gray-500">
        还没有评论，来补上第一句回应吧。
      </p>
    </section>

    <div
      v-if="summaryDialogOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-gray-950/40 px-4 py-6 backdrop-blur-sm"
      @click.self="closeSummaryDialog"
    >
      <section class="max-h-[86vh] w-full max-w-3xl overflow-hidden rounded-3xl border border-white/70 bg-white/95 shadow-2xl">
        <header class="flex items-start justify-between gap-4 border-b border-gray-100 px-6 py-5">
          <div>
            <p class="text-xs font-medium uppercase tracking-wide text-primary">AI 总结讨论</p>
            <h3 class="mt-1 text-2xl font-bold text-gray-900">{{ post?.title || '帖子讨论' }}</h3>
          </div>
          <button
            class="rounded-full bg-gray-100 p-2 text-gray-500 hover:bg-gray-200"
            type="button"
            aria-label="关闭"
            @click="closeSummaryDialog"
          >
            <X class="h-5 w-5" />
          </button>
        </header>

        <div class="max-h-[62vh] overflow-y-auto px-6 py-5">
          <div v-if="summaryLoading" class="rounded-2xl bg-primary/5 p-5 text-sm text-primary">
            AI 正在整理帖子正文和评论区讨论...
          </div>

          <div v-else-if="summaryError" class="rounded-2xl bg-red-50 p-5 text-sm text-red-600">
            {{ summaryError }}
          </div>

          <div v-else-if="summaryEmpty" class="rounded-2xl bg-gray-50 p-5 text-sm text-gray-500">
            这个帖子还没有评论，以下总结主要基于帖子正文生成。
          </div>

          <div v-if="summaryResult" class="space-y-5">
            <article class="rounded-2xl bg-primary/5 p-4">
              <h4 class="mb-2 text-sm font-semibold text-gray-900">总结</h4>
              <p class="text-sm leading-7 text-gray-700">{{ summaryResult.summary }}</p>
            </article>

            <div v-if="summaryResult.key_points?.length" class="rounded-2xl border border-gray-100 bg-white p-4">
              <h4 class="mb-3 text-sm font-semibold text-gray-900">关键要点</h4>
              <ul class="space-y-2 text-sm leading-6 text-gray-700">
                <li v-for="point in summaryResult.key_points" :key="point" class="flex gap-2">
                  <span class="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary"></span>
                  <span>{{ point }}</span>
                </li>
              </ul>
            </div>

            <div v-if="summaryResult.discussion_threads?.length" class="space-y-3">
              <h4 class="text-sm font-semibold text-gray-900">讨论脉络</h4>
              <article
                v-for="thread in summaryResult.discussion_threads"
                :key="thread.topic"
                class="rounded-2xl border border-gray-100 bg-white p-4"
              >
                <h5 class="font-semibold text-gray-900">{{ thread.topic }}</h5>
                <p class="mt-2 text-sm leading-6 text-gray-600">{{ thread.summary }}</p>
              </article>
            </div>

            <div class="grid gap-4 md:grid-cols-2">
              <div class="rounded-2xl bg-amber-50 p-4">
                <h4 class="mb-3 text-sm font-semibold text-amber-900">仍在讨论</h4>
                <ul v-if="summaryResult.open_questions?.length" class="space-y-2 text-sm leading-6 text-amber-800">
                  <li v-for="question in summaryResult.open_questions" :key="question">- {{ question }}</li>
                </ul>
                <p v-else class="text-sm text-amber-800">暂无明确未解决问题。</p>
              </div>
              <div class="rounded-2xl bg-emerald-50 p-4">
                <h4 class="mb-3 text-sm font-semibold text-emerald-900">后续行动</h4>
                <ul v-if="summaryResult.action_items?.length" class="space-y-2 text-sm leading-6 text-emerald-800">
                  <li v-for="item in summaryResult.action_items" :key="item">- {{ item }}</li>
                </ul>
                <p v-else class="text-sm text-emerald-800">暂无明确行动项。</p>
              </div>
            </div>

            <div class="space-y-2">
              <label class="text-sm font-semibold text-gray-900" for="post-summary-text">弹窗文本</label>
              <textarea
                id="post-summary-text"
                class="h-36 w-full resize-none rounded-2xl border border-gray-100 bg-gray-50 p-3 text-sm leading-6 text-gray-700 outline-none focus:border-primary/40 focus:ring-2 focus:ring-primary/10"
                readonly
                :value="summaryText"
                @focus="$event.target.select()"
              ></textarea>
            </div>
          </div>
        </div>

        <footer class="flex justify-end border-t border-gray-100 px-6 py-4">
          <button class="btn-primary px-4 py-2 text-sm" type="button" @click="closeSummaryDialog">完成</button>
        </footer>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted, nextTick, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Sparkles, X } from 'lucide-vue-next';
import CommentNode from '../components/business/CommentNode.vue';
import { api } from '../services/api';
import { aiApi } from '../services/aiApi';
import { authState } from '../stores/auth';

const route = useRoute();
const router = useRouter();
const post = ref(null);
const loading = ref(false);
const commenting = ref(false);
const editingPost = ref(false);
const error = ref('');
const actionMessage = ref('');
const commentContent = ref('');
const summaryDialogOpen = ref(false);
const summaryLoading = ref(false);
const summaryError = ref('');
const summaryResult = ref(null);
const postEdit = reactive({
  title: '',
  content: ''
});

const currentUserId = computed(() => authState.user?.id || '');
const summaryEmpty = computed(() => Boolean(summaryResult.value && !summaryResult.value.comment_count));

const summaryText = computed(() => {
  if (!summaryResult.value) {
    return '';
  }
  const result = summaryResult.value;
  const parts = [
    `《${result.post_title || post.value?.title || '帖子'}》讨论总结`,
    result.summary || '暂无总结。'
  ];
  if (result.key_points?.length) {
    parts.push('关键要点：', ...result.key_points.map((item) => `- ${item}`));
  }
  if (result.open_questions?.length) {
    parts.push('仍在讨论：', ...result.open_questions.map((item) => `- ${item}`));
  }
  if (result.action_items?.length) {
    parts.push('后续行动：', ...result.action_items.map((item) => `- ${item}`));
  }
  return parts.join('\n');
});

const formatDate = (value) => {
  if (!value) {
    return '刚刚';
  }
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value));
};

const loadPost = async () => {
  loading.value = true;
  error.value = '';

  try {
    post.value = await api.get(`/posts/${route.params.id}`);
    await scrollToCommentHash();
  } catch (err) {
    error.value = err.message || '加载帖子失败';
  } finally {
    loading.value = false;
  }
};

const scrollToCommentHash = async () => {
  if (!route.hash) {
    return;
  }
  await nextTick();
  const target = document.querySelector(route.hash);
  if (!target) {
    return;
  }
  target.scrollIntoView({ behavior: 'smooth', block: 'center' });
  target.classList.add('ring-2', 'ring-primary', 'ring-offset-2', 'rounded-xl');
  window.setTimeout(() => {
    target.classList.remove('ring-2', 'ring-primary', 'ring-offset-2', 'rounded-xl');
  }, 1800);
};

const goBack = () => {
  if (post.value?.tribe_id) {
    router.push(`/tribes/${post.value.tribe_id}`);
    return;
  }
  router.push('/tribes');
};

const startEdit = () => {
  postEdit.title = post.value.title;
  postEdit.content = post.value.content;
  editingPost.value = true;
};

const updatePost = async () => {
  error.value = '';
  actionMessage.value = '';

  try {
    await api.patch(`/posts/${post.value.id}`, {
      title: postEdit.title.trim(),
      content: postEdit.content.trim()
    });
    editingPost.value = false;
    actionMessage.value = '帖子已更新';
    await loadPost();
  } catch (err) {
    error.value = err.message || '更新帖子失败';
  }
};

const deletePost = async () => {
  error.value = '';

  try {
    const tribeId = post.value.tribe_id;
    await api.delete(`/posts/${post.value.id}`);
    await router.replace(tribeId ? `/tribes/${tribeId}` : '/tribes');
  } catch (err) {
    error.value = err.message || '删除帖子失败';
  }
};

const closeSummaryDialog = () => {
  if (summaryLoading.value) {
    return;
  }
  summaryDialogOpen.value = false;
};

const openPostSummary = async () => {
  if (!post.value?.id) {
    return;
  }
  summaryDialogOpen.value = true;
  summaryLoading.value = true;
  summaryError.value = '';
  summaryResult.value = null;

  try {
    summaryResult.value = await aiApi.generatePostSummary(post.value.id);
  } catch (err) {
    summaryError.value = err.message || 'AI 总结生成失败，请稍后重试';
  } finally {
    summaryLoading.value = false;
  }
};

const createComment = async (reply = null) => {
  const content = reply?.content || commentContent.value.trim();
  if (!content) {
    return;
  }

  commenting.value = true;
  error.value = '';
  actionMessage.value = '';

  try {
    await api.post(`/posts/${post.value.id}/comments`, {
      content,
      parent_id: reply?.parent_id
    });
    commentContent.value = '';
    actionMessage.value = '评论已发布';
    await loadPost();
  } catch (err) {
    error.value = err.message || '发布评论失败';
  } finally {
    commenting.value = false;
  }
};

const updateComment = async ({ comment, content }) => {
  error.value = '';
  actionMessage.value = '';

  try {
    await api.patch(`/comments/${comment.id}`, { content });
    actionMessage.value = '评论已更新';
    await loadPost();
  } catch (err) {
    error.value = err.message || '更新评论失败';
  }
};

const deleteComment = async (comment) => {
  error.value = '';
  actionMessage.value = '';

  try {
    await api.delete(`/comments/${comment.id}`);
    actionMessage.value = '评论已删除';
    await loadPost();
  } catch (err) {
    error.value = err.message || '删除评论失败';
  }
};

onMounted(loadPost);
watch(() => route.hash, scrollToCommentHash);
</script>
