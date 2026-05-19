import { apiRequest } from './api';

const withAiError = async (request) => {
  try {
    return await request();
  } catch (error) {
    throw new Error(error?.message || 'AI 服务暂时不可用，请稍后重试');
  }
};

const aiPath = (path) => `/ai${path.startsWith('/') ? path : `/${path}`}`;

export const aiApi = {
  request: (path, options = {}) => withAiError(() => apiRequest(aiPath(path), options)),
  post: (path, body) => withAiError(() => apiRequest(aiPath(path), { method: 'POST', body })),
  generateActivityCopy: (body) =>
    withAiError(() => apiRequest('/ai/activity-copy', { method: 'POST', body }))
};
