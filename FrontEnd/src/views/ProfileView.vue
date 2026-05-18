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
          <p class="text-2xl font-bold">5</p>
          <p class="text-sm text-gray-500">加入部落</p>
        </div>
        <div>
          <p class="text-2xl font-bold">12</p>
          <p class="text-sm text-gray-500">参与活动</p>
        </div>
        <div>
          <p class="text-2xl font-bold">3</p>
          <p class="text-sm text-gray-500">发起活动</p>
        </div>
      </div>
    </div>
    
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
import { computed } from 'vue';
import { User, Calendar, Settings, HelpCircle, ChevronRight } from 'lucide-vue-next';
import { authState } from '../stores/auth';

const displayEmail = computed(() => authState.user?.email || '未绑定邮箱');
const displayName = computed(() => {
  const email = authState.user?.email;
  if (!email) {
    return '匿名用户';
  }

  return email.split('@')[0];
});
</script>

<style scoped>
/* 自定义样式 */
</style>
