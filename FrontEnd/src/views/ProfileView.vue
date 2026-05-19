<template>
  <div class="container mx-auto px-4 py-6">
    <h2 class="text-3xl font-bold mb-6">个人中心</h2>
    
    <!-- 个人信息 -->
    <div class="card p-6 mb-6">
      <div class="flex flex-col items-center mb-6">
        <div class="w-24 h-24 rounded-full bg-primary/20 flex items-center justify-center mb-4">
          <User class="w-16 h-16 text-primary" />
        </div>
        <h3 class="text-xl font-semibold">{{ displayName }}</h3>
        <p class="text-gray-500">{{ displayEmail }}</p>
      </div>
      
      <div class="grid grid-cols-3 gap-4 text-center">
        <div>
          <p class="text-2xl font-bold">{{ joinedCount }}</p>
          <p class="text-sm text-gray-500">加入部落</p>
        </div>
        <div>
          <p class="text-2xl font-bold">{{ registeredCount }}</p>
          <p class="text-sm text-gray-500">参与活动</p>
        </div>
        <div>
          <p class="text-2xl font-bold">{{ managedEventCount }}</p>
          <p class="text-sm text-gray-500">发起活动</p>
        </div>
      </div>
    </div>

    <form class="card p-6 mb-6" @submit.prevent="saveProfile">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold">个人资料</h3>
        <span v-if="loading" class="text-sm text-gray-500">加载中...</span>
      </div>
      <p v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</p>
      <p v-if="successMessage" class="mb-4 text-sm text-primary">{{ successMessage }}</p>
      <div class="grid md:grid-cols-2 gap-4">
        <label class="block">
          <span class="text-sm text-gray-500">昵称</span>
          <input v-model="form.display_name" class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/50" />
        </label>
        <label class="block">
          <span class="text-sm text-gray-500">专业</span>
          <input v-model="form.major" class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/50" />
        </label>
        <label class="block md:col-span-2">
          <span class="text-sm text-gray-500">头像 URL</span>
          <input v-model="form.avatar_url" class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/50" />
        </label>
        <label class="block md:col-span-2">
          <span class="text-sm text-gray-500">个人简介</span>
          <textarea v-model="form.bio" rows="3" class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/50"></textarea>
        </label>
      </div>
      <button class="btn-primary mt-4 disabled:opacity-60" :disabled="saving">
        {{ saving ? '保存中...' : '保存资料' }}
      </button>
    </form>

    <section class="card p-6 mb-6">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-4">
        <div>
          <p class="text-xs font-medium uppercase tracking-wide text-primary">AI 个性推荐</p>
          <h3 class="font-semibold">根据你的简介发现部落和活动</h3>
        </div>
      </div>

      <p v-if="isBioEmpty" class="mb-4 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-700">完善个人简介可提升推荐质量</p>

      <div class="grid lg:grid-cols-2 gap-5">
        <div class="rounded-lg border border-gray-100 p-4">
          <div class="mb-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div class="flex items-center gap-2">
              <Users class="w-5 h-5 text-primary" />
              <h4 class="font-semibold">推荐兴趣部落</h4>
            </div>
            <button class="btn-primary inline-flex items-center justify-center gap-2 disabled:opacity-60" :disabled="tribeRecommendationLoading" @click="loadTribeRecommendations">
              <Sparkles class="w-4 h-4" />
              {{ tribeRecommendationLoading ? '推荐中...' : '推荐兴趣部落' }}
            </button>
          </div>
          <p v-if="tribeRecommendationError" class="mb-3 text-sm text-red-600">{{ tribeRecommendationError }}</p>
          <p v-if="tribeRecommendationNotes" class="mb-3 text-sm text-gray-500">{{ tribeRecommendationNotes }}</p>
          <div v-if="tribeRecommendationLoading" class="rounded-lg bg-gray-50 p-4 text-sm text-gray-500">
            AI 正在结合你的资料匹配可见兴趣部落...
          </div>
          <div class="space-y-3">
            <button
              v-for="tribe in recommendedTribes"
              :key="tribe.tribe_id"
              class="w-full rounded-lg border border-gray-100 bg-white p-4 text-left transition hover:border-primary/40 hover:bg-primary/5"
              @click="goToTribe(tribe.tribe_id)"
            >
              <div class="flex items-start justify-between gap-3">
                <h5 class="font-semibold">{{ tribe.name }}</h5>
                <span class="shrink-0 rounded-full bg-primary/10 px-2 py-1 text-xs text-primary">{{ formatScore(tribe.score) }}</span>
              </div>
              <p class="mt-2 text-sm text-gray-600">{{ tribe.reason }}</p>
              <div v-if="tribe.match_tags?.length" class="mt-3 flex flex-wrap gap-2">
                <span v-for="tag in tribe.match_tags" :key="tag" class="rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-600">{{ tag }}</span>
              </div>
            </button>
            <p v-if="!tribeRecommendationLoading && recommendedTribes.length === 0" class="rounded-lg bg-gray-50 p-4 text-sm text-gray-500">
              点击“推荐兴趣部落”后，将在这里展示适合你的部落。
            </p>
          </div>
        </div>

        <div class="rounded-lg border border-gray-100 p-4">
          <div class="mb-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div class="flex items-center gap-2">
              <Calendar class="w-5 h-5 text-primary" />
              <h4 class="font-semibold">推荐活动</h4>
            </div>
            <button class="btn-secondary inline-flex items-center justify-center gap-2 disabled:opacity-60" :disabled="eventRecommendationLoading" @click="loadEventRecommendations">
              <Sparkles class="w-4 h-4" />
              {{ eventRecommendationLoading ? '推荐中...' : '推荐活动' }}
            </button>
          </div>
          <p v-if="eventRecommendationError" class="mb-3 text-sm text-red-600">{{ eventRecommendationError }}</p>
          <p v-if="eventRecommendationNotes" class="mb-3 text-sm text-gray-500">{{ eventRecommendationNotes }}</p>
          <div v-if="eventRecommendationLoading" class="rounded-lg bg-gray-50 p-4 text-sm text-gray-500">
            AI 正在结合你的资料匹配可见活动...
          </div>
          <div class="space-y-3">
            <button
              v-for="event in recommendedEvents"
              :key="event.event_id"
              class="w-full rounded-lg border border-gray-100 bg-white p-4 text-left transition hover:border-primary/40 hover:bg-primary/5"
              @click="goToEvent(event.event_id)"
            >
              <div class="flex items-start justify-between gap-3">
                <h5 class="font-semibold">{{ event.title }}</h5>
                <span class="shrink-0 rounded-full bg-accent/10 px-2 py-1 text-xs text-accent">{{ formatScore(event.score) }}</span>
              </div>
              <p class="mt-2 text-sm text-gray-600">{{ event.reason }}</p>
              <div v-if="event.match_tags?.length" class="mt-3 flex flex-wrap gap-2">
                <span v-for="tag in event.match_tags" :key="tag" class="rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-600">{{ tag }}</span>
              </div>
            </button>
            <p v-if="!eventRecommendationLoading && recommendedEvents.length === 0" class="rounded-lg bg-gray-50 p-4 text-sm text-gray-500">
              点击“推荐活动”后，将在这里展示适合你的近期活动。
            </p>
          </div>
        </div>
      </div>
    </section>
    
    <!-- 功能列表 -->
    <div class="card p-4">
      <h3 class="font-semibold mb-4">我的功能</h3>
      <ul class="space-y-3">
        <li class="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
              <User class="w-5 h-5 text-primary" />
            </div>
            <span>个人资料</span>
          </div>
          <ChevronRight class="w-5 h-5 text-gray-400" />
        </li>
        <li>
          <button class="w-full flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg text-left" @click="showMyActivities = !showMyActivities">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                <Calendar class="w-5 h-5 text-primary" />
              </div>
              <span>我的活动</span>
            </div>
            <ChevronRight :class="['w-5 h-5 text-gray-400 transition-transform', showMyActivities ? 'rotate-90' : '']" />
          </button>
          <div v-if="showMyActivities" class="mt-2 space-y-3 px-3 pb-3">
            <div v-for="registration in myRegistrations" :key="registration.id" class="rounded-lg bg-gray-50 p-3">
              <div class="flex items-center justify-between gap-3">
                <h4 class="font-semibold">{{ registration.events?.title || '未命名活动' }}</h4>
                <span class="text-xs px-2 py-1 bg-accent/20 text-accent rounded-full">{{ statusLabel(registration.status) }}</span>
              </div>
              <p class="mt-1 text-sm text-gray-500">
                {{ registration.events?.tribes?.name || '未知部落' }} · {{ formatDate(registration.events?.start_time) }}
              </p>
              <p class="mt-1 text-sm text-gray-500">{{ registration.events?.location || '地点待定' }}</p>
            </div>
            <p v-if="myRegistrations.length === 0" class="text-sm text-gray-500">暂无报名活动</p>
          </div>
        </li>
        <li class="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
              <Settings class="w-5 h-5 text-primary" />
            </div>
            <span>设置</span>
          </div>
          <ChevronRight class="w-5 h-5 text-gray-400" />
        </li>
        <li class="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
              <HelpCircle class="w-5 h-5 text-primary" />
            </div>
            <span>帮助与反馈</span>
          </div>
          <ChevronRight class="w-5 h-5 text-gray-400" />
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { User, Calendar, Settings, HelpCircle, ChevronRight, Sparkles, Users } from 'lucide-vue-next';
import { authState } from '../stores/auth';
import { api } from '../services/api';
import { aiApi } from '../services/aiApi';

const profile = ref(null);
const router = useRouter();
const joinedCount = ref(0);
const registeredCount = ref(0);
const managedEventCount = ref(0);
const myRegistrations = ref([]);
const showMyActivities = ref(false);
const loading = ref(false);
const saving = ref(false);
const error = ref('');
const successMessage = ref('');
const tribeRecommendationLoading = ref(false);
const tribeRecommendationError = ref('');
const tribeRecommendations = ref(null);
const eventRecommendationLoading = ref(false);
const eventRecommendationError = ref('');
const eventRecommendations = ref(null);
const form = reactive({
  display_name: '',
  major: '',
  avatar_url: '',
  bio: ''
});

const displayEmail = computed(() => authState.user?.email || '未绑定邮箱');
const displayName = computed(() => {
  if (profile.value?.display_name) {
    return profile.value.display_name;
  }
  const email = authState.user?.email;
  if (!email) {
    return '匿名用户';
  }

  return email.split('@')[0];
});
const isBioEmpty = computed(() => !String(form.bio || '').trim());
const recommendedTribes = computed(() => tribeRecommendations.value?.recommended_tribes || []);
const recommendedEvents = computed(() => eventRecommendations.value?.recommended_events || []);
const tribeRecommendationNotes = computed(() => tribeRecommendations.value?.profile_basis?.notes || '');
const eventRecommendationNotes = computed(() => eventRecommendations.value?.profile_basis?.notes || '');

const fillForm = (data) => {
  profile.value = data;
  form.display_name = data?.display_name || '';
  form.major = data?.major || '';
  form.avatar_url = data?.avatar_url || '';
  form.bio = data?.bio || '';
};

const statusLabel = (status) => {
  const map = {
    registered: '已报名',
    checked_in: '已签到',
    cancelled: '已取消'
  };
  return map[status] || status || '未知';
};

const formatDate = (value) => {
  if (!value) {
    return '时间待定';
  }
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value));
};

const loadProfile = async () => {
  loading.value = true;
  error.value = '';

  try {
    const [profileData, myTribes, managedEvents, registrationsData] = await Promise.all([
      api.get('/profile/me'),
      api.get('/tribes/my'),
      api.get('/dashboard/events'),
      api.get('/events/my-registrations')
    ]);
    fillForm(profileData);
    joinedCount.value = myTribes.length;
    managedEventCount.value = managedEvents.length;
    registeredCount.value = registrationsData.length;
    myRegistrations.value = registrationsData;
  } catch (err) {
    error.value = err.message || '加载个人资料失败';
  } finally {
    loading.value = false;
  }
};

const saveProfile = async () => {
  saving.value = true;
  error.value = '';
  successMessage.value = '';

  try {
    const updated = await api.patch('/profile/me', { ...form });
    fillForm(updated);
    successMessage.value = '资料已保存';
  } catch (err) {
    error.value = err.message || '保存个人资料失败';
  } finally {
    saving.value = false;
  }
};

const loadTribeRecommendations = async () => {
  tribeRecommendationLoading.value = true;
  tribeRecommendationError.value = '';

  try {
    tribeRecommendations.value = await aiApi.generateRecommendations({
      limit_tribes: 5,
      limit_events: 0
    });
  } catch (err) {
    tribeRecommendationError.value = err.message || 'AI 部落推荐生成失败，请稍后重试';
  } finally {
    tribeRecommendationLoading.value = false;
  }
};

const loadEventRecommendations = async () => {
  eventRecommendationLoading.value = true;
  eventRecommendationError.value = '';

  try {
    eventRecommendations.value = await aiApi.generateRecommendations({
      limit_tribes: 0,
      limit_events: 5
    });
  } catch (err) {
    eventRecommendationError.value = err.message || 'AI 活动推荐生成失败，请稍后重试';
  } finally {
    eventRecommendationLoading.value = false;
  }
};

const formatScore = (score) => {
  const value = Number(score);
  if (Number.isNaN(value)) {
    return '匹配';
  }
  return `${Math.round(value * 100)}%`;
};

const goToTribe = (tribeId) => {
  if (tribeId) {
    router.push(`/tribes/${tribeId}`);
  }
};

const goToEvent = (eventId) => {
  if (eventId) {
    router.push(`/events/${eventId}`);
  }
};

onMounted(loadProfile);
</script>

<style scoped>
/* 自定义样式 */
</style>
