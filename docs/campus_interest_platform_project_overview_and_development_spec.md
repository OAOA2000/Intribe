# 校园兴趣部落与活动协作平台 项目介绍与开发说明文档

# 1. 项目概述

## 1.1 项目名称

校园兴趣部落与活动协作平台

## 1.2 项目定位

本项目旨在构建一个面向高校学生的数字化兴趣社区与活动协作平台。

平台以“兴趣连接”和“活动协作”为核心，通过现代化 Web 应用的方式，为学生提供：

- 兴趣部落发现与加入
- 校园活动发布与报名
- 社区讨论与实时协作
- 消息通知与社交互动
- 部落运营与活动管理
- AI 辅助协作与内容增强能力

项目整体风格偏向“轻量化校园社交 + 社区协作”，而非传统教务或后台管理系统。

---

# 2. 项目目标

## 2.1 用户目标

平台主要面向：

- 普通学生用户
- 兴趣部落成员
- 部落管理员 / 活动组织者
- 校园社团运营人员

用户能够：

1. 浏览校园兴趣社区
2. 加入感兴趣的部落
3. 查看和报名活动
4. 参与社区讨论
5. 获取活动通知与消息提醒
6. 使用 AI 能力提升协作效率

## 2.2 技术目标

项目希望实现：

- 现代化前端体验
- 响应式跨端适配
- 基于 Supabase 的轻后端架构
- 实时消息与协作能力
- AI 功能可扩展架构
- 适合快速迭代的模块化结构

---

# 3. 当前项目状态

目前项目已经完成：

- 前端基础架构
- UI 视觉体系
- 核心页面与主要业务交互
- Supabase Auth 登录注册接入
- 路由结构
- 页面导航体系
- Flask 后端服务基础架构
- Supabase 数据表 SQL 初始化脚本
- Supabase RLS 权限策略脚本
- Seed 数据脚本
- 前端 API service 封装
- 用户资料、部落、活动、报名、消息、管理中台等核心 API
- AI 活动文案占位接口

当前系统属于：

“前后端业务闭环初步实现 + Supabase 数据层接入”阶段。

当前已经从单纯原型阶段进入可联调阶段。前端不再只依赖 Mock 数据，主要页面已经开始通过 Flask API 读取和写入 Supabase 数据。

已经具备的真实业务能力包括：

- 用户通过 Supabase Auth 登录注册
- 后端校验前端传入的 Supabase access token
- 当前用户 profile 获取与更新
- 部落列表、我的部落、加入部落、退出部落
- 活动列表、活动报名、退出报名
- 管理员发布、编辑、删除活动
- 消息列表与标记已读
- 管理中台统计数据与可管理活动列表
- 顶部和发现页搜索部落 / 活动
- AI 活动文案接口占位返回

仍需继续完善：

1. 更完整的部落详情页、活动详情页和消息创建流程
2. 成员审核、入部申请、活动签到等更细业务流程
3. 更严格的表单校验、分页、错误提示和空状态
4. Supabase 实时订阅能力
5. 自动化集成测试和 RLS 验证
6. AI 能力从占位逻辑升级为真实 LLM 调用

后续重点不再是堆叠静态 UI，而是继续完善数据一致性、权限边界、业务闭环和部署可用性。

---

# 4. 技术栈

## 4.1 前端技术栈

当前 FrontEnd 使用：

- Vue 3
- Vite
- Tailwind CSS
- Vue Router
- Lucide-vue-next
- Headless UI
- Supabase JS SDK

### 技术特点

#### Vue 3

用于构建响应式组件化前端。

#### Vite

作为现代前端构建工具，提供：

- 快速热更新
- ES Module 开发体验
- 高速构建

#### Tailwind CSS

项目全部使用 Tailwind 原子化类名构建 UI。

禁止使用大量传统 CSS 文件。

#### Lucide-vue-next

统一图标系统。

#### Headless UI

用于构建可访问性友好的交互组件。

#### Supabase

用于：

- 用户认证
- 数据库存储
- Row Level Security
- 实时能力
- 后续 Edge Functions

---

## 4.2 部署架构

当前项目设计为：

```text
前端：
Vue + Vite 静态站点

部署：
Tencent EdgeOne Pages

后端：
Supabase + Edge Functions

数据库：
PostgreSQL (Supabase)
```

### EdgeOne Pages

EdgeOne 仅作为：

- 静态页面托管
- CDN
- 前端部署平台

当前代码中没有使用 EdgeOne SDK。

---

# 5. 项目目录结构

当前项目结构：

```text
SoftwareSystem/
├── FrontEnd/
│   ├── src/
│   │   ├── lib/
│   │   ├── router/
│   │   ├── services/
│   │   ├── stores/
│   │   └── views/
│   ├── package.json
│   ├── vite.config.js
│   └── ...
├── BackEnd/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   └── supabase_client.py
│   ├── sql/
│   │   ├── 001_init_schema.sql
│   │   ├── 002_rls_policies.sql
│   │   └── 003_seed_data.sql
│   ├── tests/
│   ├── run.py
│   ├── requirements.txt
│   └── README.md
├── docs/
├── .env.example
└── ...
```

当前目录已经形成前后端分离结构：

```text
SoftwareSystem/
├── FrontEnd/          # Vue 3 + Vite + Tailwind 前端
├── BackEnd/           # Flask 后端 API 服务
├── docs/              # 项目文档
└── ...
```

### FrontEnd

前端负责：

- 页面展示
- 用户交互
- Supabase Auth 登录注册
- 从 Supabase 获取 session access_token
- 通过 `src/services/api.js` 调用 Flask API

### BackEnd

后端负责：

- 统一业务 API
- Supabase JWT 校验
- 用户上下文注入
- Supabase REST 数据访问
- 业务权限辅助判断
- 统一 JSON 响应
- AI 能力预留

### BackEnd/sql

SQL 文件用于 Supabase 初始化：

1. `001_init_schema.sql`：创建业务表、索引和 updated_at trigger
2. `002_rls_policies.sql`：开启并配置 RLS 权限策略
3. `003_seed_data.sql`：插入初始部落和活动数据

执行 SQL 时需要复制文件内容到 Supabase SQL Editor，而不是在 SQL Editor 中输入本地文件路径。

---

# 6. 前端架构说明

## 6.1 页面结构

当前系统已经实现以下核心页面：

### HomeView.vue

兴趣发现大厅。

核心功能：

- 兴趣标签筛选
- 热门部落展示
- 活动推荐
- 搜索入口

视觉重点：

- Banner 区域
- 卡片式布局
- 社交社区氛围

---

### TribesView.vue

我的部落页面。

包含：

- 已加入部落
- 推荐部落
- 加入操作
- 部落入口

未来扩展：

- 部落详情
- 成员列表
- 活动管理
- 公告系统

---

### MessagesView.vue

消息中心。

当前为消息列表 UI。

未来扩展：

- 实时通知
- 系统消息
- 活动提醒
- 私聊 / 群聊
- AI 总结通知

---

### ProfileView.vue

个人中心。

包含：

- 用户信息
- 统计数据
- 设置入口

未来扩展：

- 编辑资料
- 兴趣标签
- 活动历史
- AI 个性推荐

---

### DashboardView.vue

管理中台。

主要面向：

- 部落管理员
- 活动组织者

当前 UI 包含：

- 数据统计卡片
- 活动管理列表
- 编辑 / 删除入口

未来扩展：

- 数据分析
- 报名审核
- AI 活动运营助手
- 用户活跃分析

---

# 7. UI / UX 设计理念

## 7.1 设计关键词

- 现代校园
- 数字社区
- 轻量协作
- 社交化体验
- 信息可视化

---

## 7.2 视觉体系

项目采用：

- Glassmorphism（轻玻璃质感）
- 卡片式布局
- 大圆角（2xl）
- 柔和阴影
- 轻动效反馈

目标是避免传统管理系统的沉重感。

---

## 7.3 配色体系

### 主色调

Indigo（靛蓝）

用于：

- 主按钮
- 导航激活态
- 品牌识别

### 行动色

Amber（橙色）

用于：

- 立即报名
- CTA 按钮
- 热门标签

### 社区色

Mint（薄荷绿）

用于：

- 活动状态
- 社区氛围
- 招募状态

---

## 7.4 响应式设计

### 移动端

- 底部导航栏
- 单列布局
- 强化触控体验

### PC 端

- 左侧边栏
- 多列卡片布局
- 更强信息密度

---

# 8. 当前业务模型（规划）

## 8.1 用户（Users）

系统用户。

来源：

Supabase Auth

扩展 Profile 表存储：

- 用户昵称
- 专业
- 年级
- 头像
- 兴趣标签

---

## 8.2 兴趣部落（Tribes）

平台核心社区单位。

字段建议：

```text
id
name
description
avatar
category
owner_id
member_count
created_at
```

---

## 8.3 部落成员（TribeMembers）

用于维护用户与部落关系。

字段建议：

```text
id
tribe_id
user_id
role
joined_at
```

role 示例：

- member
- admin
- owner

---

## 8.4 活动（Events）

活动系统是平台核心。

字段建议：

```text
id
tribe_id
title
description
location
start_time
status
cover_image
created_by
```

status 示例：

- recruiting
- ongoing
- finished

---

## 8.5 活动报名（EventRegistrations）

用户与活动关系。

字段建议：

```text
id
event_id
user_id
status
registered_at
```

---

## 8.6 消息（Messages）

用于系统通知与协作。

字段建议：

```text
id
sender_id
receiver_id
content
type
created_at
```

---

# 9. Supabase 架构设计

## 9.1 当前已完成

目前已经完成：

- Supabase 项目连接
- 用户注册
- 用户登录
- Session 管理
- 前端获取 Supabase access_token
- Flask 后端校验 Supabase access_token
- 后端基于用户 JWT 调用 Supabase REST API
- 业务表 Schema SQL
- RLS 权限策略 SQL
- Seed 数据 SQL

创建的用户已经能够在 Supabase 后台看到。

---

## 9.2 数据表设计

当前 Supabase PostgreSQL 规划并已提供 SQL 初始化脚本的核心表包括：

- `profiles`
- `tribes`
- `tribe_members`
- `events`
- `event_registrations`
- `messages`

这些表覆盖：

- 用户扩展资料
- 兴趣部落
- 部落成员与角色
- 活动发布与管理
- 活动报名与取消
- 用户消息通知

当前 SQL 还包含：

- `updated_at` 自动更新时间 trigger
- 常用查询索引
- 初始部落 seed 数据
- 初始活动 seed 数据

---

## 9.3 认证与后端访问模式

当前认证链路为：

```text
前端 Supabase Auth
  -> 获取 access_token
  -> 请求 Flask API 时携带 Authorization: Bearer <token>
  -> Flask 调用 Supabase Auth /auth/v1/user 校验 token
  -> Flask 使用用户 JWT 访问 Supabase REST
  -> Supabase RLS 生效
```

这种模式的优点：

- 前端不接触 service role key
- 普通业务请求优先依赖用户 JWT + RLS
- 权限不只依赖前端按钮控制
- 后续可以在 Flask 中集中扩展审计、日志、限流和 AI 能力

`SUPABASE_SERVICE_ROLE_KEY` 只应在后端可信环境使用。当前项目中它主要用于后端服务端聚合统计等场景，例如计算完整部落成员数，不能暴露给前端。

---

## 9.4 RLS（权限控制）

RLS 已经提供策略脚本。

当前权限目标包括：

- 用户只能修改自己的资料
- 登录用户可以查看部落和活动
- 用户可以加入 / 退出部落
- owner / admin 可以管理部落成员
- owner / admin 可以创建、更新、删除活动
- 用户可以报名和取消自己的活动报名
- 活动组织者可以查看报名列表
- 用户只能查看和更新自己的消息

必须避免：

“前端做了按钮限制，但数据库没有权限限制”的情况。

---

## 9.5 当前仍需完善

后续 Supabase 侧建议继续补充：

1. 更细粒度的成员审核表与审批策略
2. 活动签到与报名容量限制
3. 消息创建来源约束
4. 实时订阅策略
5. RLS 集成测试
6. 生产环境备份与迁移流程

---

# 10. AI 功能规划

## 10.1 AI 的定位

AI 不是项目核心主体。

AI 是：

“增强协作与社区运营效率的能力层”。

因此：

必须先完成业务闭环，再接入 AI。

---

## 10.2 AI 功能方向

### AI 活动助手

帮助生成：

- 活动描述
- 宣传文案
- 活动总结

---

### AI 消息总结

自动总结：

- 群聊讨论
- 活动公告
- 协作内容

---

### AI 推荐系统

推荐：

- 兴趣部落
- 活动
- 志同道合用户

---

### AI 协作助手

未来可扩展：

- AI 问答
- AI 日程整理
- AI 协作文档
- AI 活动策划

---

## 10.3 AI 架构原则

禁止：

```text
前端直接调用 LLM API
```

推荐：

```text
前端
  -> 后端 / Edge Function
      -> LLM API
          -> 返回结果
```

避免暴露 API Key。

---

# 11. 推荐开发顺序

当前推荐路线：

## 阶段 1

完成 Supabase 数据库 Schema。

---

## 阶段 2

实现：

- 部落 CRUD
- 活动 CRUD
- 用户关系
- 报名逻辑

---

## 阶段 3

完成：

- RLS
- 权限系统
- Session 校验

---

## 阶段 4

完成：

- 实时消息
- 通知系统
- 协作能力

---

## 阶段 5

引入 AI 功能。

---

## 阶段 6

完成部署：

- EdgeOne Pages
- 环境变量
- SPA fallback
- CDN 优化

---

# 12. EdgeOne Pages 部署说明

## Root Directory

```text
FrontEnd
```

## Build Command

```bash
npm ci && npm run build
```

## Output Directory

```text
dist
```

## 环境变量

```text
VITE_SUPABASE_URL
VITE_SUPABASE_ANON_KEY
```

---

## SPA 回退配置

Vue Router History 模式需要：

```text
/* -> /index.html
```

否则刷新页面会 404。

---

# 13. 工程规范建议

## 13.1 组件分层

建议拆分：

### 页面容器

views/

负责：

- 页面状态
- 数据获取
- 页面布局

---

### 业务组件

components/business/

例如：

- TribeCard
- EventCard
- MessageItem

---

### 基础组件

components/ui/

例如：

- Button
- Modal
- Input
- Badge

---

# 13.2 状态管理

当前项目规模较小。

短期可使用：

- composables
- reactive
- provide/inject

后续可考虑：

- Pinia

---

# 13.3 API 组织

建议统一：

```text
src/services/
```

例如：

```text
services/
  auth.js
  tribes.js
  events.js
  messages.js
```

避免页面直接写大量 Supabase 查询。

---

# 14. 项目阶段定位

当前项目已经完成：

- 高保真 UI 原型
- 前端交互框架
- 基础认证能力
- Flask 后端服务
- Supabase Schema / RLS / Seed SQL
- 主要业务 API
- 前端主要页面 API 接入
- 部落、活动、报名、消息、管理中台的初步闭环

当前项目阶段可以定位为：

“MVP 业务闭环初步完成，进入联调、修正和增强阶段”。

目前已经不再只是静态原型。系统已经具备真实登录、真实数据读取、真实报名和管理操作能力。

后续重点是：

- 提升业务完整度
- 修正边界场景
- 完善权限和 RLS 验证
- 优化用户体验
- 建立测试和部署流程
- 引入实时能力
- 在业务稳定后接入真实 AI 能力

建议将下一阶段拆为：

1. 业务完善阶段：详情页、审批、签到、消息生成
2. 稳定性阶段：分页、校验、错误处理、集成测试
3. 实时协作阶段：Supabase Realtime 消息与通知
4. AI 增强阶段：活动文案、推荐、总结等 LLM 能力

---

# 15. 总结

校园兴趣部落与活动协作平台是一个：

“现代校园兴趣社区 + 活动协作 + AI 增强能力”的 Web 平台。

当前已经具备：

- 现代化 UI
- 社交化设计语言
- 响应式布局
- Supabase Auth
- 页面基础结构
- Flask 后端 API
- Supabase 数据表设计
- RLS 权限策略
- 前端 API 调用封装
- 部落发现、加入、退出
- 活动浏览、报名、退出报名
- 管理员活动发布、编辑、删除
- 消息列表与已读状态
- 个人资料编辑与我的活动查看
- 管理中台统计与活动管理
- AI 接口预留

后续核心任务转为：

1. 完善详情页和更复杂业务流程
2. 加强权限边界和 RLS 测试
3. 补充消息生成、成员审核和活动签到
4. 构建实时通知与协作能力
5. 建立生产部署、日志和监控
6. 在业务闭环稳定后接入真实 LLM 能力

项目整体技术路线偏向：

“Vue 强交互前端 + Flask 业务 API + Supabase 数据与权限 + AI 增强协作”的现代 Web 应用架构。

当前代码已经从展示型原型向可运行 MVP 迈进，后续应围绕真实用户流程继续打磨，而不是继续增加孤立的静态页面。
