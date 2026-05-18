<template>
  <div class="container mx-auto px-4 py-6">
    <h2 class="text-3xl font-bold mb-6">管理中台</h2>
    <p v-if="loading" class="mb-4 text-sm text-gray-500">加载中...</p>
    <p v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</p>
    <p v-if="actionMessage" class="mb-4 text-sm text-primary">{{ actionMessage }}</p>
    
    <!-- 数据瓷砖 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="card p-4">
        <p class="text-gray-500 text-sm">今日报名</p>
        <p class="text-2xl font-bold">{{ summary.today_registrations }}</p>
      </div>
      <div class="card p-4">
        <p class="text-gray-500 text-sm">新增留言</p>
        <p class="text-2xl font-bold">{{ summary.new_messages }}</p>
      </div>
      <div class="card p-4">
        <p class="text-gray-500 text-sm">活跃度</p>
        <p class="text-2xl font-bold">{{ Math.round(summary.activity_rate * 100) }}%</p>
      </div>
      <div class="card p-4">
        <p class="text-gray-500 text-sm">总成员</p>
        <p class="text-2xl font-bold">{{ summary.total_members }}</p>
      </div>
    </div>
    
    <!-- 快捷操作 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <button class="card p-6 flex items-center gap-4 btn-primary" @click="openCreateForm">
        <div class="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
          <Plus class="w-6 h-6 text-white" />
        </div>
        <span class="text-lg font-semibold">发布新活动</span>
      </button>
      <button class="card p-6 flex items-center gap-4 btn-secondary" @click="actionMessage = '成员审核入口已预留，当前加入部落会直接成为成员。'">
        <div class="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
          <Users class="w-6 h-6 text-white" />
        </div>
        <span class="text-lg font-semibold">成员审核</span>
      </button>
    </div>

    <form v-if="showEventForm" class="card p-4 mb-6" @submit.prevent="saveEvent">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold">{{ editingEventId ? '编辑活动' : '发布新活动' }}</h3>
        <button type="button" class="px-3 py-1 bg-gray-100 rounded-lg text-sm hover:bg-gray-200" @click="closeEventForm">取消</button>
      </div>
      <div class="grid md:grid-cols-2 gap-4">
        <label class="block">
          <span class="text-sm text-gray-500">所属部落</span>
          <select v-model="eventForm.tribe_id" class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/50" :disabled="Boolean(editingEventId)">
            <option value="">请选择部落</option>
            <option v-for="tribe in manageableTribes" :key="tribe.id" :value="tribe.id">{{ tribe.name }}</option>
          </select>
        </label>
        <label class="block">
          <span class="text-sm text-gray-500">活动标题</span>
          <input v-model="eventForm.title" class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/50" />
        </label>
        <label class="block">
          <span class="text-sm text-gray-500">地点</span>
          <input v-model="eventForm.location" class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/50" />
        </label>
        <label class="block">
          <span class="text-sm text-gray-500">开始时间</span>
          <input v-model="eventForm.start_time" type="datetime-local" class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/50" />
        </label>
        <label class="block">
          <span class="text-sm text-gray-500">状态</span>
          <select v-model="eventForm.status" class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/50">
            <option value="recruiting">招募中</option>
            <option value="ongoing">进行中</option>
            <option value="finished">已结束</option>
            <option value="cancelled">已取消</option>
          </select>
        </label>
        <label class="block">
          <span class="text-sm text-gray-500">图标</span>
          <input v-model="eventForm.cover_icon" class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/50" placeholder="Code / Trophy / Music" />
        </label>
        <label class="block md:col-span-2">
          <span class="text-sm text-gray-500">活动简介</span>
          <textarea v-model="eventForm.description" rows="3" class="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/50"></textarea>
        </label>
      </div>
      <button class="btn-primary mt-4 disabled:opacity-60" :disabled="savingEvent">
        {{ savingEvent ? '保存中...' : '保存活动' }}
      </button>
    </form>
    
    <!-- 活动管理 -->
    <div class="card p-4">
      <h3 class="font-semibold mb-4">活动管理</h3>
      <div class="space-y-3">
        <div v-for="activity in activities" :key="activity.id" class="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg gap-3">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
              <component :is="getActivityIcon(activity.tag)" class="w-6 h-6 text-primary" />
            </div>
            <div>
              <h4 class="font-semibold">{{ activity.title }}</h4>
              <p class="text-sm text-gray-500">{{ activity.date }} · {{ activity.location }}</p>
            </div>
          </div>
          <div class="flex gap-2">
            <button class="px-3 py-1 bg-gray-100 rounded-lg text-sm hover:bg-gray-200" @click="openEditForm(activity)">编辑</button>
            <button class="px-3 py-1 bg-red-100 text-red-600 rounded-lg text-sm hover:bg-red-200 disabled:opacity-60" :disabled="deletingId === activity.id" @click="deleteActivity(activity)">
              {{ deletingId === activity.id ? '删除中' : '删除' }}
            </button>
          </div>
        </div>
      </div>
      <p v-if="!loading && activities.length === 0" class="text-sm text-gray-500">暂无可管理活动。请确认当前用户是部落 owner/admin。</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue';
import { Plus, Users, Code, Activity, Guitar } from 'lucide-vue-next';
import { api } from '../services/api';

// 获取活动图标
const getActivityIcon = (tag) => {
  switch (tag) {
    case 'programming':
      return Code;
    case 'sports':
      return Activity;
    case 'music':
      return Guitar;
    default:
      return Users;
  }
};

const loading = ref(false);
const error = ref('');
const actionMessage = ref('');
const deletingId = ref(null);
const savingEvent = ref(false);
const showEventForm = ref(false);
const editingEventId = ref('');
const activities = ref([]);
const manageableTribes = ref([]);
const summary = reactive({
  today_registrations: 0,
  new_messages: 0,
  activity_rate: 0,
  total_members: 0
});
const eventForm = reactive({
  tribe_id: '',
  title: '',
  description: '',
  location: '',
  start_time: '',
  status: 'recruiting',
  cover_icon: ''
});

const categoryToTag = (category, title = '') => {
  if (title.includes('吉他') || title.includes('音乐')) {
    return 'music';
  }
  const map = {
    科技: 'programming',
    运动: 'sports'
  };
  return map[category] || 'all';
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

const normalizeActivity = (event) => ({
  ...event,
  date: formatDate(event.start_time),
  location: event.location || '地点待定',
  tag: categoryToTag(event.tribes?.category, event.title)
});

const toDatetimeLocal = (value) => {
  if (!value) {
    return '';
  }
  const date = new Date(value);
  const offset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
};

const resetEventForm = () => {
  Object.assign(eventForm, {
    tribe_id: '',
    title: '',
    description: '',
    location: '',
    start_time: '',
    status: 'recruiting',
    cover_icon: ''
  });
  editingEventId.value = '';
};

const openCreateForm = () => {
  resetEventForm();
  showEventForm.value = true;
  actionMessage.value = manageableTribes.value.length ? '' : '请先确认当前用户是某个部落的 owner/admin。';
};

const openEditForm = (activity) => {
  Object.assign(eventForm, {
    tribe_id: activity.tribe_id,
    title: activity.title || '',
    description: activity.description || '',
    location: activity.location || '',
    start_time: toDatetimeLocal(activity.start_time),
    status: activity.status || 'recruiting',
    cover_icon: activity.cover_icon || ''
  });
  editingEventId.value = activity.id;
  showEventForm.value = true;
  actionMessage.value = '';
};

const closeEventForm = () => {
  showEventForm.value = false;
  resetEventForm();
};

const loadDashboard = async () => {
  loading.value = true;
  error.value = '';

  try {
    const [summaryData, eventRows, myTribes] = await Promise.all([
      api.get('/dashboard/summary'),
      api.get('/dashboard/events'),
      api.get('/tribes/my')
    ]);
    Object.assign(summary, summaryData);
    activities.value = eventRows.map(normalizeActivity);
    manageableTribes.value = myTribes
      .filter((item) => ['owner', 'admin'].includes(item.role))
      .map((item) => item.tribes)
      .filter(Boolean);
  } catch (err) {
    error.value = err.message || '加载管理数据失败';
  } finally {
    loading.value = false;
  }
};

const saveEvent = async () => {
  if (!eventForm.title || (!editingEventId.value && !eventForm.tribe_id)) {
    error.value = '请填写所属部落和活动标题';
    return;
  }

  savingEvent.value = true;
  error.value = '';
  actionMessage.value = '';

  const payload = {
    title: eventForm.title,
    description: eventForm.description,
    location: eventForm.location,
    start_time: eventForm.start_time || null,
    status: eventForm.status,
    cover_icon: eventForm.cover_icon
  };

  try {
    if (editingEventId.value) {
      await api.patch(`/events/${editingEventId.value}`, payload);
      actionMessage.value = `已更新「${eventForm.title}」`;
    } else {
      await api.post('/events', { ...payload, tribe_id: eventForm.tribe_id });
      actionMessage.value = `已发布「${eventForm.title}」`;
    }
    closeEventForm();
    await loadDashboard();
  } catch (err) {
    error.value = err.message || '保存活动失败';
  } finally {
    savingEvent.value = false;
  }
};

const deleteActivity = async (activity) => {
  if (!window.confirm(`确定删除「${activity.title}」吗？`)) {
    return;
  }

  deletingId.value = activity.id;
  error.value = '';
  actionMessage.value = '';

  try {
    await api.delete(`/events/${activity.id}`);
    actionMessage.value = `已删除「${activity.title}」`;
    await loadDashboard();
  } catch (err) {
    error.value = err.message || '删除活动失败';
  } finally {
    deletingId.value = null;
  }
};

onMounted(loadDashboard);
</script>

<style scoped>
/* 自定义样式 */
</style>
