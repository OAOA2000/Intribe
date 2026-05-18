<template>
  <div class="container mx-auto px-4 py-6">
    <h2 class="text-3xl font-bold mb-6">我的部落</h2>
    <p v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</p>
    <p v-if="actionMessage" class="mb-4 text-sm text-primary">{{ actionMessage }}</p>
    <p v-if="loading" class="mb-4 text-sm text-gray-500">加载中...</p>
    
    <!-- 部落列表 -->
    <div class="space-y-4">
      <div v-for="tribe in myTribes" :key="tribe.id" class="card p-4 flex items-center gap-4">
        <div class="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
          <component :is="getTribeIcon(tribe.tag)" class="w-8 h-8 text-primary" />
        </div>
        <div class="flex-1">
          <h4 class="font-semibold text-lg">{{ tribe.name }}</h4>
          <p class="text-sm text-gray-500">{{ tribe.members }} 成员 · {{ tribe.activities }} 近期活动</p>
        </div>
        <div class="flex gap-2">
          <button class="btn-primary" @click="actionMessage = `已进入「${tribe.name}」`">进入</button>
          <button
            v-if="tribe.membershipRole === 'member'"
            class="px-4 py-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 active:scale-95 transition-all duration-200 disabled:opacity-60"
            :disabled="leavingId === tribe.id"
            @click="leaveTribe(tribe)"
          >
            {{ leavingId === tribe.id ? '退出中...' : '退出' }}
          </button>
        </div>
      </div>
    </div>
    <p v-if="!loading && myTribes.length === 0" class="text-sm text-gray-500">还没有加入部落，可以从推荐部落开始。</p>
    
    <!-- 推荐部落 -->
    <div class="mt-10">
      <h3 class="text-xl font-semibold mb-4">推荐部落</h3>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <div v-for="tribe in recommendedTribes" :key="tribe.id" class="card p-4">
          <div class="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center mb-3">
            <component :is="getTribeIcon(tribe.tag)" class="w-8 h-8 text-primary" />
          </div>
          <h4 class="font-semibold mb-1">{{ tribe.name }}</h4>
          <p class="text-sm text-gray-500 mb-3">{{ tribe.members }} 成员</p>
          <button
            class="w-full btn-primary text-sm py-1 disabled:opacity-60"
            :disabled="joiningId === tribe.id"
            @click="joinTribe(tribe)"
          >
            {{ joiningId === tribe.id ? '加入中...' : '加入' }}
          </button>
        </div>
      </div>
      <p v-if="!loading && recommendedTribes.length === 0" class="text-sm text-gray-500">所有部落都已经加入。</p>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { Code, Activity, Guitar, Palette, Users } from 'lucide-vue-next';
import { api } from '../services/api';

// 获取部落图标
const getTribeIcon = (tag) => {
  switch (tag) {
    case 'programming':
      return Code;
    case 'sports':
      return Activity;
    case 'music':
      return Guitar;
    case 'art':
      return Palette;
    default:
      return Users;
  }
};

const loading = ref(false);
const error = ref('');
const actionMessage = ref('');
const joiningId = ref(null);
const leavingId = ref(null);
const allTribes = ref([]);
const memberships = ref([]);

const categoryToTag = (category, name = '') => {
  if (name.includes('吉他') || name.includes('音乐')) {
    return 'music';
  }
  const map = {
    科技: 'programming',
    运动: 'sports',
    艺术: 'art'
  };
  return map[category] || 'all';
};

const normalizeTribe = (tribe) => ({
  ...tribe,
  tag: categoryToTag(tribe.category, tribe.name),
  members: tribe.member_count ?? (Array.isArray(tribe.tribe_members) ? tribe.tribe_members.length : 0),
  activities: tribe.event_count ?? (Array.isArray(tribe.events) ? tribe.events.length : 0)
});

const memberTribeIds = computed(() => new Set(memberships.value.map((item) => item.tribes?.id || item.tribe_id)));

const myTribes = computed(() =>
  memberships.value
    .filter((item) => item.tribes)
    .map((item) => ({
      ...normalizeTribe(item.tribes),
      membershipRole: item.role
    }))
);

const recommendedTribes = computed(() =>
  allTribes.value
    .filter((tribe) => !memberTribeIds.value.has(tribe.id))
    .map(normalizeTribe)
);

const loadTribes = async () => {
  loading.value = true;
  error.value = '';

  try {
    const [tribeRows, memberRows] = await Promise.all([
      api.get('/tribes'),
      api.get('/tribes/my')
    ]);
    allTribes.value = tribeRows;
    memberships.value = memberRows;
  } catch (err) {
    error.value = err.message || '加载部落失败';
  } finally {
    loading.value = false;
  }
};

const joinTribe = async (tribe) => {
  joiningId.value = tribe.id;
  actionMessage.value = '';
  error.value = '';

  try {
    await api.post(`/tribes/${tribe.id}/join`);
    actionMessage.value = `已加入「${tribe.name}」`;
    await loadTribes();
  } catch (err) {
    error.value = err.message || '加入部落失败';
  } finally {
    joiningId.value = null;
  }
};

const leaveTribe = async (tribe) => {
  leavingId.value = tribe.id;
  actionMessage.value = '';
  error.value = '';

  try {
    await api.delete(`/tribes/${tribe.id}/leave`);
    actionMessage.value = `已退出「${tribe.name}」`;
    await loadTribes();
  } catch (err) {
    error.value = err.message || '退出部落失败';
  } finally {
    leavingId.value = null;
  }
};

onMounted(loadTribes);
</script>

<style scoped>
/* 自定义样式 */
</style>
