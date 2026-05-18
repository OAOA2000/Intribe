<template>
  <div class="container mx-auto px-4 py-6">
    <h2 class="text-3xl font-bold mb-6">我的部落</h2>
    
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
        <button class="btn-primary">进入</button>
      </div>
    </div>
    
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
          <button class="w-full btn-primary text-sm py-1">加入</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Code, Activity, Guitar, Palette, Users } from 'lucide-vue-next';

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

// Mock 数据 - 我的部落
const myTribes = [
  {
    id: 1,
    name: '编程爱好者',
    members: 245,
    activities: 5,
    tag: 'programming'
  },
  {
    id: 2,
    name: '篮球社',
    members: 189,
    activities: 3,
    tag: 'sports'
  }
];

// Mock 数据 - 推荐部落
const recommendedTribes = [
  {
    id: 3,
    name: '吉他社',
    members: 123,
    tag: 'music'
  },
  {
    id: 4,
    name: '摄影社',
    members: 156,
    tag: 'art'
  },
  {
    id: 5,
    name: '舞蹈社',
    members: 112,
    tag: 'art'
  },
  {
    id: 6,
    name: '电影社',
    members: 87,
    tag: 'art'
  }
];
</script>

<style scoped>
/* 自定义样式 */
</style>