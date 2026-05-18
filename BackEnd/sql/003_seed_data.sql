insert into public.tribes (name, description, category, icon)
values
  ('编程爱好者', '一起刷题、做项目、参加编程马拉松。', '科技', 'Code'),
  ('篮球社', '校内篮球训练、友谊赛和赛事组织。', '运动', 'Trophy'),
  ('吉他社', '从弹唱入门到校园音乐会，一起享受音乐。', '艺术', 'Music'),
  ('学术研究会', '论文阅读、科研方法交流和跨学科研讨。', '学术', 'BookOpen'),
  ('摄影社', '校园采风、人像创作与后期分享。', '艺术', 'Camera'),
  ('舞蹈社', '街舞、爵士与校园舞台排练。', '艺术', 'Sparkles'),
  ('电影社', '观影、影评、短片创作和放映活动。', '生活', 'Film'),
  ('志愿者协会', '公益活动、志愿服务与校园互助。', '公益', 'HeartHandshake')
on conflict do nothing;

insert into public.events (tribe_id, title, description, location, start_time, status, cover_icon)
select id, '编程马拉松', '24小时编程挑战，组队完成校园创新应用。', '创新实验室 A201', now() + interval '7 days', 'recruiting', 'Code'
from public.tribes where name = '编程爱好者'
on conflict do nothing;

insert into public.events (tribe_id, title, description, location, start_time, status, cover_icon)
select id, '校园篮球友谊赛', '面向全校同学的篮球交流赛，欢迎组队报名。', '东区篮球场', now() + interval '10 days', 'recruiting', 'Trophy'
from public.tribes where name = '篮球社'
on conflict do nothing;

insert into public.events (tribe_id, title, description, location, start_time, status, cover_icon)
select id, '吉他音乐会', '吉他社年度小型音乐会，开放舞台与自由点歌。', '学生活动中心小剧场', now() + interval '14 days', 'recruiting', 'Music'
from public.tribes where name = '吉他社'
on conflict do nothing;
