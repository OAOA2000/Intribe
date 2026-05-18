# SoftwareSystem

基于 Vue 3 + Vite 的前端项目，已接入 Supabase Auth（邮箱注册/登录/退出），可直接部署到腾讯 EdgeOne Pages。

## 功能

- 邮箱注册（支持邮件确认场景）
- 邮箱密码登录
- 登录态持久化（刷新后保持会话）
- 受保护路由（未登录自动跳转到登录页）
- 退出登录

## 本地启动

1. 安装依赖

```bash
npm install
```

2. 配置环境变量（复制示例）

```bash
cp .env.example .env.local
```

3. 在 `.env.local` 中填写你的 Supabase 项目配置

```env
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-public-key
```

4. 运行开发环境

```bash
npm run dev
```

## Supabase 控制台配置

1. 进入 Supabase 项目 -> `Authentication` -> `Providers`，启用 `Email`。
2. 在 `Authentication` -> `URL Configuration` 中设置：
- `Site URL`：你的线上域名（例如 `https://your-app.example.com`）
- `Redirect URLs`：
  - `http://localhost:5173`
  - `https://<你的 EdgeOne Pages 域名>`
  - 如有自定义域名也要加入

## 部署到腾讯 EdgeOne Pages

在 EdgeOne Pages 项目里使用以下构建配置：

- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `npm install`

并在项目环境变量中添加：

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

添加后重新部署即可。
