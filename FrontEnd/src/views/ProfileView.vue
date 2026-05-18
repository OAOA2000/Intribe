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
        <li class="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
              <Calendar class="w-5 h-5 text-primary" />
            </div>
            <span>我的活动</span>
          </div>
          <ChevronRight class="w-5 h-5 text-gray-400" />
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
import { User, Calendar, Settings, HelpCircle, ChevronRight } from 'lucide-vue-next';
import { authState } from '../stores/auth';
import { api } from '../services/api';

const profile = ref(null);
const joinedCount = ref(0);
const registeredCount = ref(0);
const managedEventCount = ref(0);
const loading = ref(false);
const saving = ref(false);
const error = ref('');
const successMessage = ref('');
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

const fillForm = (data) => {
  profile.value = data;
  form.display_name = data?.display_name || '';
  form.major = data?.major || '';
  form.avatar_url = data?.avatar_url || '';
  form.bio = data?.bio || '';
};

const loadProfile = async () => {
  loading.value = true;
  error.value = '';

  try {
    const [profileData, myTribes, managedEvents, myRegistrations] = await Promise.all([
      api.get('/profile/me'),
      api.get('/tribes/my'),
      api.get('/dashboard/events'),
      api.get('/events/my-registrations')
    ]);
    fillForm(profileData);
    joinedCount.value = myTribes.length;
    managedEventCount.value = managedEvents.length;
    registeredCount.value = myRegistrations.length;
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

onMounted(loadProfile);
</script>

<style scoped>
/* 自定义样式 */
</style>
