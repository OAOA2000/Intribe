<template>
  <div class="border-l-2 border-gray-100 pl-3" :style="{ marginLeft: `${indent}px` }">
    <div class="rounded-xl bg-gray-50 p-3">
      <div class="flex items-start justify-between gap-3">
        <div>
          <p class="text-sm font-semibold text-gray-900">{{ authorName }}</p>
          <p class="text-xs text-gray-500">{{ formatDate(comment.created_at) }}</p>
        </div>
        <div v-if="(canEdit || canDelete) && !comment.deleted_at" class="flex shrink-0 gap-2 text-xs">
          <button v-if="canEdit" class="text-primary hover:underline" @click="startEdit">编辑</button>
          <button v-if="canDelete" class="text-red-600 hover:underline" @click="$emit('delete', comment)">删除</button>
        </div>
      </div>

      <form v-if="editing" class="mt-3 space-y-2" @submit.prevent="submitEdit">
        <textarea
          v-model="editContent"
          class="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
          rows="3"
        />
        <div class="flex gap-2">
          <button class="btn-primary text-sm" type="submit">保存</button>
          <button class="rounded-lg bg-gray-200 px-4 py-2 text-sm text-gray-700" type="button" @click="editing = false">
            取消
          </button>
        </div>
      </form>
      <p v-else class="mt-3 whitespace-pre-line text-sm leading-6 text-gray-700">
        {{ comment.content }}
      </p>

      <button
        v-if="!comment.deleted_at"
        class="mt-3 text-sm text-primary hover:underline"
        type="button"
        @click="replying = !replying"
      >
        {{ replying ? '收起回复' : '回复' }}
      </button>

      <form v-if="replying" class="mt-3 space-y-2" @submit.prevent="submitReply">
        <textarea
          v-model="replyContent"
          class="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
          placeholder="写下你的回复..."
          rows="3"
        />
        <button class="btn-secondary text-sm disabled:opacity-60" type="submit" :disabled="!replyContent.trim()">
          发布回复
        </button>
      </form>
    </div>

    <div v-if="comment.children?.length" class="mt-3 space-y-3">
      <CommentNode
        v-for="child in comment.children"
        :key="child.id"
        :comment="child"
        :current-user-id="currentUserId"
        :depth="depth + 1"
        @reply="$emit('reply', $event)"
        @delete="$emit('delete', $event)"
        @update="$emit('update', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';

defineOptions({ name: 'CommentNode' });

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  currentUserId: {
    type: String,
    default: ''
  },
  depth: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits(['reply', 'delete', 'update']);

const replying = ref(false);
const editing = ref(false);
const replyContent = ref('');
const editContent = ref('');

const indent = computed(() => Math.min(props.depth, 4) * 12);
const authorName = computed(() => props.comment.author?.display_name || '校园同学');
const canEdit = computed(() => Boolean(props.comment.can_edit));
const canDelete = computed(() => Boolean(props.comment.can_delete));

const formatDate = (value) => {
  if (!value) {
    return '刚刚';
  }
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value));
};

const startEdit = () => {
  editContent.value = props.comment.content;
  editing.value = true;
};

const submitReply = () => {
  const content = replyContent.value.trim();
  if (!content) {
    return;
  }
  emit('reply', { parent_id: props.comment.id, content });
  replyContent.value = '';
  replying.value = false;
};

const submitEdit = () => {
  const content = editContent.value.trim();
  if (!content) {
    return;
  }
  emit('update', { comment: props.comment, content });
  editing.value = false;
};
</script>
