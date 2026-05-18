<template>
  <div class="container mx-auto px-4 py-6">
    <h2 class="text-3xl font-bold mb-6">管理中台</h2>
    
    <!-- 数据瓷砖 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="card p-4">
        <p class="text-gray-500 text-sm">今日报名</p>
        <p class="text-2xl font-bold">23</p>
      </div>
      <div class="card p-4">
        <p class="text-gray-500 text-sm">新增留言</p>
        <p class="text-2xl font-bold">45</p>
      </div>
      <div class="card p-4">
        <p class="text-gray-500 text-sm">活跃度</p>
        <p class="text-2xl font-bold">87%</p>
      </div>
      <div class="card p-4">
        <p class="text-gray-500 text-sm">总成员</p>
        <p class="text-2xl font-bold">324</p>
      </div>
    </div>
    
    <!-- 快捷操作 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <button class="card p-6 flex items-center gap-4 btn-primary">
        <div class="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
          <Plus class="w-6 h-6 text-white" />
        </div>
        <span class="text-lg font-semibold">发布新活动</span>
      </button>
      <button class="card p-6 flex items-center gap-4 btn-secondary">
        <div class="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
          <Users class="w-6 h-6 text-white" />
        </div>
        <span class="text-lg font-semibold">成员审核</span>
      </button>
    </div>
    
    <!-- 活动管理 -->
    <div class="card p-4">
      <h3 class="font-semibold mb-4">活动管理</h3>
      <div class="space-y-3">
        <div v-for="activity in activities" :key="activity.id" class="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
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
            <button class="px-3 py-1 bg-gray-100 rounded-lg text-sm hover:bg-gray-200">编辑</button>
            <button class="px-3 py-1 bg-red-100 text-red-600 rounded-lg text-sm hover:bg-red-200">删除</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Plus, Users, Code, Activity, Guitar } from 'lucide-vue-next';

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

// Mock 数据 - 活动
const activities = [
  {
    id: 1,
    title: '编程马拉松',
    date: '2026-04-15 10:00',
    location: '科技楼 301 室',
    tag: 'programming'
  },
  {
    id: 2,
    title: '校园篮球友谊赛',
    date: '2026-04-10 14:00',
    location: '体育馆篮球场',
    tag: 'sports'
  },
  {
    id: 3,
    title: '吉他音乐会',
    date: '2026-04-08 19:00',
    location: '学生活动中心',
    tag: 'music'
  }
];
</script>

<style scoped>
/* 自定义样式 */
</style>