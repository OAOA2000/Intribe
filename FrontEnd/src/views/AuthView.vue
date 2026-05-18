<template>
  <div class="min-h-screen bg-gradient-to-br from-sky-50 via-cyan-50 to-white flex items-center justify-center px-4 py-10">
    <div class="w-full max-w-md bg-white rounded-3xl shadow-xl border border-cyan-100 p-6 md:p-8">
      <div class="text-center mb-6">
        <h1 class="text-2xl font-bold text-gray-900">兴趣部落账号中心</h1>
        <p class="text-sm text-gray-500 mt-2">使用 Supabase 完成注册与登录</p>
      </div>

      <div class="grid grid-cols-2 bg-gray-100 rounded-xl p-1 mb-6">
        <button
          type="button"
          class="py-2 rounded-lg text-sm font-medium transition-colors"
          :class="mode === 'login' ? 'bg-white shadow text-primary' : 'text-gray-500 hover:text-gray-700'"
          @click="switchMode('login')"
        >
          登录
        </button>
        <button
          type="button"
          class="py-2 rounded-lg text-sm font-medium transition-colors"
          :class="mode === 'register' ? 'bg-white shadow text-primary' : 'text-gray-500 hover:text-gray-700'"
          @click="switchMode('register')"
        >
          注册
        </button>
      </div>

      <p v-if="authState.configError" class="mb-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">
        {{ authState.configError }}
      </p>

      <p v-if="errorMessage" class="mb-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">
        {{ errorMessage }}
      </p>

      <p v-if="successMessage" class="mb-4 text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg p-3">
        {{ successMessage }}
      </p>

      <form class="space-y-4" @submit.prevent="handleSubmit">
        <label class="block">
          <span class="text-sm font-medium text-gray-700">邮箱</span>
          <input
            v-model="email"
            type="email"
            required
            autocomplete="email"
            class="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary/40"
            placeholder="you@example.com"
          />
        </label>

        <label class="block">
          <span class="text-sm font-medium text-gray-700">密码</span>
          <input
            v-model="password"
            type="password"
            required
            minlength="6"
            autocomplete="current-password"
            class="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary/40"
            placeholder="至少 6 位"
          />
        </label>

        <label v-if="mode === 'register'" class="block">
          <span class="text-sm font-medium text-gray-700">确认密码</span>
          <input
            v-model="confirmPassword"
            type="password"
            required
            minlength="6"
            autocomplete="new-password"
            class="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary/40"
            placeholder="再次输入密码"
          />
        </label>

        <button
          type="submit"
          class="w-full btn-primary py-2.5 disabled:opacity-60 disabled:cursor-not-allowed"
          :disabled="isSubmitting || Boolean(authState.configError)"
        >
          {{ submitText }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { authState, signInWithEmail, signUpWithEmail } from '../stores/auth';

const router = useRouter();
const route = useRoute();

const mode = ref('login');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const errorMessage = ref('');
const successMessage = ref('');
const isSubmitting = ref(false);

const submitText = computed(() => {
  if (isSubmitting.value) {
    return mode.value === 'login' ? '登录中...' : '注册中...';
  }

  return mode.value === 'login' ? '立即登录' : '创建账号';
});

const redirectPath = computed(() => {
  const target = route.query.redirect;
  return typeof target === 'string' && target.startsWith('/') ? target : '/';
});

const switchMode = (nextMode) => {
  mode.value = nextMode;
  errorMessage.value = '';
  successMessage.value = '';
};

const handleSubmit = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  if (mode.value === 'register' && password.value !== confirmPassword.value) {
    errorMessage.value = '两次输入的密码不一致，请检查后重试';
    return;
  }

  isSubmitting.value = true;

  try {
    if (mode.value === 'login') {
      await signInWithEmail({ email: email.value, password: password.value });
      await router.replace(redirectPath.value);
      return;
    }

    const result = await signUpWithEmail({ email: email.value, password: password.value });

    if (result.needsEmailConfirm) {
      successMessage.value = '注册成功，请前往邮箱完成验证后再登录';
      mode.value = 'login';
      confirmPassword.value = '';
      return;
    }

    await router.replace(redirectPath.value);
  } catch (error) {
    errorMessage.value = error?.message || '操作失败，请稍后重试';
  } finally {
    isSubmitting.value = false;
  }
};
</script>
