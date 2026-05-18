<template>
  <div class="container mx-auto px-4 py-6">
    <button class="mb-4 text-sm text-primary hover:underline" type="button" @click="router.back()">返回</button>

    <p v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</p>
    <p v-if="actionMessage" class="mb-4 text-sm text-primary">{{ actionMessage }}</p>
    <p v-if="loading" class="mb-4 text-sm text-gray-500">加载中...</p>

    <section v-if="tribe" class="mb-6 rounded-2xl bg-white p-5 shadow-md">
      <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div class="flex items-center gap-4">
          <div class="flex h-16 w-16 items-center justify-center rounded-full bg-primary/20">
            <component :is="getTribeIcon(tribe.category)" class="h-8 w-8 text-primary" />
          </div>
          <div>
            <h2 class="text-2xl font-bold">{{ tribe.name }}</h2>
            <p class="mt-1 text-sm text-gray-500">
              {{ tribe.category || '兴趣部落' }} · {{ tribe.member_count || 0 }} 成员 · {{ tribe.event_count || 0 }} 活动
            </p>
          </div>
        </div>
        <button class="btn-primary md:w-auto" type="button" @click="showPostForm = !showPostForm">
          {{ showPostForm ? '收起' : '发布帖子' }}
        </button>
      </div>
      <p class="mt-4 text-sm leading-6 text-gray-600">{{ tribe.description || '这个部落还没有简介。' }}</p>
    </section>

    <form v-if="showPostForm" class="mb-6 rounded-2xl bg-white p-5 shadow-md" @submit.prevent="createPost">
      <h3 class="mb-4 text-lg font-semibold">发布新帖子</h3>
      <div class="space-y-3">
        <input
          v-model="postForm.title"
          class="w-full rounded-lg border border-gray-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary/40"
          placeholder="帖子标题"
          type="text"
        />
        <textarea
          v-model="postForm.content"
          class="w-full rounded-lg border border-gray-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary/40"
          placeholder="分享想法、活动灵感或协作需求..."
          rows="5"
        />
        <button
          class="btn-secondary disabled:opacity-60"
          type="submit"
          :disabled="submitting || !postForm.title.trim() || !postForm.content.trim()"
        >
          {{ submitting ? '发布中...' : '发布' }}
        </button>
      </div>
    </form>

    <section>
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-xl font-semibold">部落讨论</h3>
        <span class="text-sm text-gray-500">{{ posts.length }} 篇帖子</span>
      </div>

      <div class="space-y-4">
        <article
          v-for="post in posts"
          :key="post.id"
          class="card cursor-pointer p-5"
          @click="router.push(`/posts/${post.id}`)"
        >
          <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
            <div>
              <h4 class="text-lg font-semibold">{{ post.title }}</h4>
              <p class="mt-1 text-xs text-gray-500">
                {{ post.author?.display_name || '校园同学' }} · {{ formatDate(post.created_at) }}
              </p>
            </div>
            <span class="rounded-full bg-accent/15 px-3 py-1 text-xs text-accent">
              {{ post.comment_count || 0 }} 条评论
            </span>
          </div>
          <p class="mt-3 line-clamp-3 whitespace-pre-line text-sm leading-6 text-gray-600">{{ post.content }}</p>
          <p v-if="post.last_comment_at" class="mt-3 text-xs text-gray-400">
            最近回复 {{ formatDate(post.last_comment_at) }}
          </p>
        </article>
      </div>

      <div v-if="!loading && posts.length === 0" class="rounded-2xl bg-white p-8 text-center text-sm text-gray-500 shadow-md">
        还没有帖子，来发起第一场讨论吧。
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Activity, Code, Guitar, Palette, Users } from 'lucide-vue-next';
import { api } from '../services/api';

const route = useRoute();
const router = useRouter();
const tribe = ref(null);
const posts = ref([]);
const loading = ref(false);
const submitting = ref(false);
const error = ref('');
const actionMessage = ref('');
const showPostForm = ref(false);
const postForm = reactive({
  title: '',
  content: ''
});

const getTribeIcon = (category = '') => {
  if (category.includes('科技')) {
    return Code;
  }
  if (category.includes('运动')) {
    return Activity;
  }
  if (category.includes('音乐')) {
    return Guitar;
  }
  if (category.includes('艺术')) {
    return Palette;
  }
  return Users;
};

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

const loadPage = async () => {
  loading.value = true;
  error.value = '';

  try {
    const tribeId = route.params.id;
    const [tribeRow, postRows] = await Promise.all([
      api.get(`/tribes/${tribeId}`),
      api.get(`/tribes/${tribeId}/posts`)
    ]);
    tribe.value = tribeRow;
    posts.value = postRows;
  } catch (err) {
    error.value = err.message || '加载部落讨论失败';
  } finally {
    loading.value = false;
  }
};

const createPost = async () => {
  submitting.value = true;
  error.value = '';
  actionMessage.value = '';

  try {
    await api.post(`/tribes/${route.params.id}/posts`, {
      title: postForm.title.trim(),
      content: postForm.content.trim()
    });
    postForm.title = '';
    postForm.content = '';
    showPostForm.value = false;
    actionMessage.value = '帖子已发布';
    await loadPage();
  } catch (err) {
    error.value = err.message || '发布帖子失败';
  } finally {
    submitting.value = false;
  }
};

onMounted(loadPage);
</script>
