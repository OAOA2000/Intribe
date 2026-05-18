<template>
  <div class="container mx-auto px-4 py-6">
    <!-- 头部 Banner -->
    <div class="mb-8">
      <h2 class="text-3xl font-bold mb-4">发现你的兴趣部落</h2>
      <form class="mb-4 flex flex-col sm:flex-row gap-2" @submit.prevent="submitSearch">
        <input
          v-model="localSearchKeyword"
          type="text"
          placeholder="搜索兴趣部落或活动..."
          class="w-full sm:max-w-md px-4 py-2 rounded-lg bg-white border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/50"
        />
        <button class="btn-primary sm:w-auto" type="submit">搜索</button>
      </form>
      <div v-if="searchKeyword" class="mb-4 flex items-center gap-3">
        <span class="text-sm text-gray-500">搜索：{{ searchKeyword }}</span>
        <button class="text-sm text-primary hover:underline" @click="clearSearch">清除</button>
      </div>
      <!-- 标签筛选 -->
      <div class="flex flex-wrap gap-2">
        <button 
          v-for="tag in tags" 
          :key="tag.id"
          :class="[
            'px-4 py-2 rounded-full transition-colors',
            activeTag === tag.id ? 'bg-primary text-white' : 'bg-gray-100 hover:bg-gray-200'
          ]"
          @click="switchTag(tag.id)"
        >
          {{ tag.name }}
        </button>
      </div>
    </div>

    <!-- 部落卡片流 -->
    <section class="mb-10">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-xl font-semibold">热门部落</h3>
        <span v-if="loading" class="text-sm text-gray-500">加载中...</span>
      </div>
      <p v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</p>
      <p v-if="actionMessage" class="mb-4 text-sm text-primary">{{ actionMessage }}</p>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <div
          v-for="tribe in filteredTribes"
          :key="tribe.id"
          class="card cursor-pointer p-4"
          @click="router.push(`/tribes/${tribe.id}`)"
        >
          <div class="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center mb-3">
            <component :is="getTribeIcon(tribe.tag)" class="w-8 h-8 text-primary" />
          </div>
          <h4 class="font-semibold mb-1">{{ tribe.name }}</h4>
          <p class="text-sm text-gray-500 mb-2">{{ tribe.members }} 成员</p>
          <span v-if="tribe.hot" class="text-xs px-2 py-1 bg-secondary/20 text-secondary rounded-full">热门</span>
        </div>
      </div>
      <p v-if="!loading && filteredTribes.length === 0" class="text-sm text-gray-500">暂无匹配部落</p>
    </section>

    <!-- 活动列表 -->
    <section>
      <h3 class="text-xl font-semibold mb-4">近期活动</h3>
      <div class="space-y-4">
        <div v-for="activity in filteredActivities" :key="activity.id" class="card p-4 md:flex gap-4">
          <div class="md:w-1/4 mb-3 md:mb-0">
            <div class="w-full h-40 bg-primary/10 rounded-xl flex items-center justify-center">
              <component :is="getActivityIcon(activity.tag)" class="w-12 h-12 text-primary" />
            </div>
          </div>
          <div class="md:w-3/4 flex flex-col justify-between">
            <div>
              <div class="flex items-center gap-2 mb-2">
                <span class="text-xs px-2 py-1 bg-accent/20 text-accent rounded-full">{{ activity.status }}</span>
                <span class="text-xs text-gray-500">{{ activity.date }}</span>
              </div>
              <h4 class="font-semibold text-lg mb-2">{{ activity.title }}</h4>
              <p class="text-sm text-gray-600 mb-3">{{ activity.description }}</p>
              <div class="flex items-center text-sm text-gray-500">
                <MapPin class="w-4 h-4 mr-1" />
                {{ activity.location }}
              </div>
            </div>
            <div class="flex flex-wrap gap-2 mt-3">
              <button
                v-if="!isRegistered(activity.id)"
                class="btn-secondary disabled:opacity-60"
                :disabled="registeringId === activity.id"
                @click="registerActivity(activity)"
              >
                {{ registeringId === activity.id ? '报名中...' : '立即报名' }}
              </button>
              <button
                v-else
                class="px-4 py-2 rounded-lg bg-gray-200 text-gray-900 cursor-not-allowed"
                disabled
              >
                已参加
              </button>
              <button
                v-if="isRegistered(activity.id)"
                class="px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 active:scale-95 transition-all duration-200 disabled:opacity-60"
                :disabled="cancellingId === activity.id"
                @click="cancelRegistration(activity)"
              >
                {{ cancellingId === activity.id ? '退出中...' : '退出报名' }}
              </button>
            </div>
          </div>
        </div>
      </div>
      <p v-if="!loading && filteredActivities.length === 0" class="text-sm text-gray-500">暂无匹配活动</p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { MapPin, Code, Activity, Guitar, Book, Palette, Users, Calendar } from 'lucide-vue-next';
import { api } from '../services/api';

// 标签数据
const tags = [
  { id: 'all', name: '全部' },
  { id: 'programming', name: '编程' },
  { id: 'sports', name: '运动' },
  { id: 'music', name: '音乐' },
  { id: 'academic', name: '学术' },
  { id: 'art', name: '艺术' }
];

// 当前选中的标签
const activeTag = ref('all');
const route = useRoute();
const router = useRouter();
const loading = ref(false);
const error = ref('');
const actionMessage = ref('');
const registeringId = ref(null);
const cancellingId = ref(null);
const tribes = ref([]);
const activities = ref([]);
const registrations = ref([]);
const registeredEventIds = ref(new Set());
const searchKeyword = computed(() => (typeof route.query.search === 'string' ? route.query.search.trim() : ''));
const localSearchKeyword = ref(searchKeyword.value);

// 切换标签
const switchTag = (tagId) => {
  activeTag.value = tagId;
};

// 获取部落图标
const getTribeIcon = (tag) => {
  switch (tag) {
    case 'programming':
      return Code;
    case 'sports':
      return Activity;
    case 'music':
      return Guitar;
    case 'academic':
      return Book;
    case 'art':
      return Palette;
    default:
      return Users;
  }
};

// 获取活动图标
const getActivityIcon = (tag) => {
  switch (tag) {
    case 'programming':
      return Code;
    case 'sports':
      return Activity;
    case 'music':
      return Guitar;
    case 'academic':
      return Book;
    case 'art':
      return Palette;
    default:
      return Calendar;
  }
};

const categoryToTag = (category, name = '') => {
  if (name.includes('吉他') || name.includes('音乐')) {
    return 'music';
  }
  const map = {
    科技: 'programming',
    运动: 'sports',
    学术: 'academic',
    艺术: 'art'
  };
  return map[category] || 'all';
};

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
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value));
};

const normalizeTribe = (tribe) => {
  const members = tribe.member_count ?? (Array.isArray(tribe.tribe_members) ? tribe.tribe_members.length : 0);
  return {
    ...tribe,
    tag: categoryToTag(tribe.category, tribe.name),
    members,
    hot: members >= 3 || ['编程爱好者', '篮球社', '摄影社', '志愿者协会'].includes(tribe.name)
  };
};

const normalizeActivity = (event) => ({
  ...event,
  tag: categoryToTag(event.tribes?.category, event.title),
  date: formatDate(event.start_time),
  status: statusLabel(event.status),
  location: event.location || '地点待定'
});

const getRegistrationEventId = (registration) => registration.event_id || registration.events?.id;

const setRegistrations = (rows) => {
  registrations.value = rows;
  registeredEventIds.value = new Set(rows.map(getRegistrationEventId).filter(Boolean));
};

const isRegistered = (eventId) => registeredEventIds.value.has(eventId);

const loadRegistrations = async () => {
  setRegistrations(await api.get('/events/my-registrations'));
};

const loadPageData = async () => {
  loading.value = true;
  error.value = '';

  try {
    const [tribeRows, eventRows, registrationRows] = await Promise.all([
      api.get('/tribes', { search: searchKeyword.value }),
      api.get('/events', { search: searchKeyword.value }),
      api.get('/events/my-registrations')
    ]);
    tribes.value = tribeRows.map(normalizeTribe);
    activities.value = eventRows.map(normalizeActivity);
    setRegistrations(registrationRows);
  } catch (err) {
    error.value = err.message || '加载数据失败，请确认后端已启动并完成 Supabase 初始化';
  } finally {
    loading.value = false;
  }
};

const submitSearch = async () => {
  const keyword = localSearchKeyword.value.trim();
  await router.push({
    path: '/',
    query: keyword ? { search: keyword } : {}
  });
};

const clearSearch = async () => {
  localSearchKeyword.value = '';
  await router.push({ path: '/' });
};

const registerActivity = async (activity) => {
  registeringId.value = activity.id;
  actionMessage.value = '';
  error.value = '';

  try {
    await api.post(`/events/${activity.id}/register`);
    registeredEventIds.value = new Set([...registeredEventIds.value, activity.id]);
    await loadRegistrations();
    actionMessage.value = `已报名「${activity.title}」`;
  } catch (err) {
    error.value = err.message || '报名失败';
  } finally {
    registeringId.value = null;
  }
};

const cancelRegistration = async (activity) => {
  cancellingId.value = activity.id;
  actionMessage.value = '';
  error.value = '';

  try {
    await api.delete(`/events/${activity.id}/register`);
    const nextIds = new Set(registeredEventIds.value);
    nextIds.delete(activity.id);
    registeredEventIds.value = nextIds;
    await loadRegistrations();
    actionMessage.value = `已退出「${activity.title}」报名`;
  } catch (err) {
    error.value = err.message || '退出报名失败';
  } finally {
    cancellingId.value = null;
  }
};

// 过滤后的部落
const filteredTribes = computed(() => {
  if (activeTag.value === 'all') {
    return tribes.value;
  }
  return tribes.value.filter(tribe => tribe.tag === activeTag.value);
});

// 过滤后的活动
const filteredActivities = computed(() => {
  if (activeTag.value === 'all') {
    return activities.value;
  }
  return activities.value.filter(activity => activity.tag === activeTag.value);
});

onMounted(loadPageData);
watch(searchKeyword, loadPageData);
watch(searchKeyword, (value) => {
  localSearchKeyword.value = value;
});
</script>

<style scoped>
/* 自定义样式 */
</style>
