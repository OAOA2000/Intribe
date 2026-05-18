import { reactive } from 'vue';
import { hasSupabaseConfig, supabase, supabaseConfigError } from '../lib/supabase';

export const authState = reactive({
  initialized: false,
  loading: false,
  session: null,
  user: null,
  error: '',
  configError: supabaseConfigError
});

let authInitPromise = null;
let authSubscription = null;

const getErrorMessage = (error, fallback) => error?.message || fallback;

export const initAuth = async () => {
  if (authInitPromise) {
    return authInitPromise;
  }

  authInitPromise = (async () => {
    if (!hasSupabaseConfig || !supabase) {
      authState.initialized = true;
      return;
    }

    authState.loading = true;

    const { data, error } = await supabase.auth.getSession();

    if (error) {
      authState.error = getErrorMessage(error, '读取登录状态失败，请稍后重试');
    }

    authState.session = data?.session ?? null;
    authState.user = data?.session?.user ?? null;
    authState.initialized = true;
    authState.loading = false;

    if (!authSubscription) {
      const { data: authListener } = supabase.auth.onAuthStateChange((_event, session) => {
        authState.session = session;
        authState.user = session?.user ?? null;
      });

      authSubscription = authListener?.subscription ?? null;
    }
  })();

  return authInitPromise;
};

export const signUpWithEmail = async ({ email, password }) => {
  if (!supabase) {
    throw new Error(supabaseConfigError);
  }

  authState.loading = true;
  authState.error = '';

  const { data, error } = await supabase.auth.signUp({ email, password });

  authState.loading = false;

  if (error) {
    throw new Error(getErrorMessage(error, '注册失败，请稍后重试'));
  }

  return {
    needsEmailConfirm: !data?.session,
    user: data?.user ?? null
  };
};

export const signInWithEmail = async ({ email, password }) => {
  if (!supabase) {
    throw new Error(supabaseConfigError);
  }

  authState.loading = true;
  authState.error = '';

  const { data, error } = await supabase.auth.signInWithPassword({ email, password });

  authState.loading = false;

  if (error) {
    throw new Error(getErrorMessage(error, '登录失败，请检查邮箱或密码'));
  }

  return data;
};

export const signOutUser = async () => {
  if (!supabase) {
    return;
  }

  authState.loading = true;
  authState.error = '';

  const { error } = await supabase.auth.signOut();

  authState.loading = false;

  if (error) {
    throw new Error(getErrorMessage(error, '退出登录失败，请稍后重试'));
  }
};
