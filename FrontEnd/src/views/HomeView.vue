<template>
  <div class="container mx-auto px-4 py-6">
    <!-- 头部 Banner -->
    <div class="mb-8">
      <h2 class="text-3xl font-bold mb-4">发现你的兴趣部落</h2>
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
      <h3 class="text-xl font-semibold mb-4">热门部落</h3>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <div v-for="tribe in filteredTribes" :key="tribe.id" class="card p-4">
          <div class="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center mb-3">
            <component :is="getTribeIcon(tribe.tag)" class="w-8 h-8 text-primary" />
          </div>
          <h4 class="font-semibold mb-1">{{ tribe.name }}</h4>
          <p class="text-sm text-gray-500 mb-2">{{ tribe.members }} 成员</p>
          <span v-if="tribe.hot" class="text-xs px-2 py-1 bg-secondary/20 text-secondary rounded-full">热门</span>
        </div>
      </div>
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
            <button class="btn-secondary self-start mt-3">立即报名</button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { MapPin, Code, Activity, Guitar, Book, Palette, Users, Calendar } from 'lucide-vue-next';

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

// Mock 数据 - 部落
const tribes = [
  {
    id: 1,
    name: '编程爱好者',
    members: 245,
    hot: true,
    tag: 'programming'
  },
  {
    id: 2,
    name: '篮球社',
    members: 189,
    hot: true,
    tag: 'sports'
  },
  {
    id: 3,
    name: '吉他社',
    members: 123,
    hot: false,
    tag: 'music'
  },
  {
    id: 4,
    name: '学术研究会',
    members: 98,
    hot: false,
    tag: 'academic'
  },
  {
    id: 5,
    name: '摄影社',
    members: 156,
    hot: true,
    tag: 'art'
  },
  {
    id: 6,
    name: '舞蹈社',
    members: 112,
    hot: false,
    tag: 'art'
  },
  {
    id: 7,
    name: '电影社',
    members: 87,
    hot: false,
    tag: 'art'
  },
  {
    id: 8,
    name: '志愿者协会',
    members: 203,
    hot: true,
    tag: 'all'
  }
];

// Mock 数据 - 活动
const activities = [
  {
    id: 1,
    title: '编程马拉松',
    description: '24小时不间断编程挑战，与队友一起解决实际问题，赢取丰厚奖品。',
    date: '2026-04-15 10:00',
    location: '科技楼 301 室',
    status: '招募中',
    tag: 'programming'
  },
  {
    id: 2,
    title: '校园篮球友谊赛',
    description: '各院系之间的篮球对抗赛，展现团队合作精神和竞技风采。',
    date: '2026-04-10 14:00',
    location: '体育馆篮球场',
    status: '招募中',
    tag: 'sports'
  },
  {
    id: 3,
    title: '吉他音乐会',
    description: '校园吉他社年度音乐会，带来精彩的吉他演奏和歌曲演唱。',
    date: '2026-04-08 19:00',
    location: '学生活动中心',
    status: '进行中',
    tag: 'music'
  },
  {
    id: 4,
    title: '学术讲座：人工智能发展趋势',
    description: '邀请知名教授分享人工智能领域的最新研究成果和发展趋势。',
    date: '2026-04-12 16:00',
    location: '教学楼 201 室',
    status: '招募中',
    tag: 'academic'
  }
];

// 过滤后的部落
const filteredTribes = computed(() => {
  if (activeTag.value === 'all') {
    return tribes;
  }
  return tribes.filter(tribe => tribe.tag === activeTag.value);
});

// 过滤后的活动
const filteredActivities = computed(() => {
  if (activeTag.value === 'all') {
    return activities;
  }
  return activities.filter(activity => activity.tag === activeTag.value);
});
</script>

<style scoped>
/* 自定义样式 */
</style>