# 校园兴趣部落与活动协作平台 项目介绍与开发说明文档

## 1. 项目概述

### 1.1 项目名称

校园兴趣部落与活动协作平台

### 1.2 项目定位

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

## 2. 项目目标

### 2.1 用户目标

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

### 2.2 技术目标

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
- 核心页面原型
- Supabase Auth 登录注册接入
- 路由结构
- 页面导航体系
- Mock 数据驱动的 UI 展示

当前系统属于：

“高保真前端原型 + 初步认证系统”阶段。

尚未完成：

- 数据库 Schema
- 实际业务数据流
- 权限系统（RLS）
- 活动真实 CRUD
- 消息系统
- AI 功能
- 后端服务逻辑

因此后续开发重点应放在：

1. 数据模型建设
2. Supabase 数据层
3. 业务逻辑实现
4. AI 能力接入

而不是继续堆叠静态 UI。

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
│   ├── package.json
│   ├── vite.config.js
│   └── ...
├── .env.example
└── ...
```

未来建议扩展为：

```text
SoftwareSystem/
├── FrontEnd/          # Vue 前端
├── BackEnd/           # 后端服务（可选）
├── Docs/              # 项目文档
├── Database/          # SQL / Schema
├── Scripts/           # 自动化脚本
└── ...
```

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

创建的用户已经能够在 Supabase 后台看到。

---

## 9.2 下一阶段重点

后续开发重点：

### 第一阶段

数据库 Schema 建设。

### 第二阶段

Row Level Security（RLS）权限系统。

### 第三阶段

真实业务数据接入。

### 第四阶段

实时能力。

### 第五阶段

AI 能力接入。

---

## 9.3 RLS（权限控制）

RLS 是后续开发重点。

例如：

- 用户只能修改自己的资料
- 用户只能查看自己加入的部落内容
- 管理员才能删除活动
- 组织者才能审核报名

必须避免：

“前端做了按钮限制，但数据库没有权限限制”的情况。

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

接下来真正进入：

“业务系统实现阶段”。

后续重点不再是页面视觉，而是：

- 数据结构
- 权限系统
- 实时协作
- AI 能力
- 系统稳定性

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

后续核心任务是：

1. 完成数据层
2. 完成权限体系
3. 完成业务逻辑
4. 构建实时协作
5. 接入 AI 能力

项目整体技术路线偏向：

“轻后端 + 强前端 + AI 增强协作”的现代 Web 应用架构。

