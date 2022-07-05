# 仓库结构

## 文档

`doc/`中的文件非常重要 基本上包含了VerilogOJ的所有构建思路

- `doc/submission/` 最终的设计稿
- `doc/design/` 全栈设计思路
    - `doc/fig/` 构思图
    - `doc/plan/` 他们当时的时间安排 可以借鉴
- `doc/research/` 与Verilog相关的东西

## 前端

`frontend/` 使用Vue2构建 Javascript编程语言

## 后端

`backend/` 使用Django构建 Python编程语言

## 判题模块

`judger/` 其实是在 `backend/judge` 中 主要是Python

## 开发环境部署

`deploy/` & `docker-compose.yml`
