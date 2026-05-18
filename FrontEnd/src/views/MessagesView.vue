<template>
  <div class="container mx-auto px-4 py-6">
    <h2 class="text-3xl font-bold mb-6">消息中心</h2>
    
    <!-- 消息列表 -->
    <div class="space-y-3">
      <div v-for="message in messages" :key="message.id" class="card p-4 flex items-center gap-4">
        <div class="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center relative">
          <component :is="getMessageIcon(message.type)" class="w-6 h-6 text-primary" />
          <span v-if="message.unread" class="absolute w-3 h-3 bg-red-500 rounded-full -bottom-1 -right-1"></span>
        </div>
        <div class="flex-1">
          <div class="flex justify-between items-center mb-1">
            <h4 class="font-semibold">{{ message.sender }}</h4>
            <span class="text-xs text-gray-500">{{ message.time }}</span>
          </div>
          <p class="text-sm text-gray-600 truncate">{{ message.content }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Code, Activity, Guitar, Bell, Users } from 'lucide-vue-next';

// 获取消息图标
const getMessageIcon = (type) => {
  switch (type) {
    case 'programming':
      return Code;
    case 'sports':
      return Activity;
    case 'music':
      return Guitar;
    case 'system':
      return Bell;
    default:
      return Users;
  }
};

// Mock 数据 - 消息
const messages = [
  {
    id: 1,
    sender: '编程爱好者部落',
    content: '编程马拉松活动即将开始，快来报名参加吧！',
    time: '10分钟前',
    unread: true,
    type: 'programming'
  },
  {
    id: 2,
    sender: '篮球社',
    content: '本周六下午有友谊赛，记得准时参加训练。',
    time: '1小时前',
    unread: true,
    type: 'sports'
  },
  {
    id: 3,
    sender: '系统通知',
    content: '您已成功加入摄影社。',
    time: '昨天',
    unread: false,
    type: 'system'
  },
  {
    id: 4,
    sender: '吉他社',
    content: '下周三晚有吉他练习，地点在音乐教室。',
    time: '2天前',
    unread: false,
    type: 'music'
  }
];
</script>

<style scoped>
/* 自定义样式 */
</style>