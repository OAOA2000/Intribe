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
  </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted, nextTick, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import CommentNode from '../components/business/CommentNode.vue';
import { api } from '../services/api';
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
const postEdit = reactive({
  title: '',
  content: ''
});

const currentUserId = computed(() => authState.user?.id || '');

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
