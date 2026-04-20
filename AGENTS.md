# AGENTS.md

## Project Overview

Dify is an open-source platform for developing LLM applications with an intuitive interface combining agentic AI workflows, RAG pipelines, agent capabilities, and model management.

The codebase is split into:

- **Backend API** (`/api`): Python Flask application organized with Domain-Driven Design
- **Frontend Web** (`/web`): Next.js application using TypeScript and React
- **Docker deployment** (`/docker`): Containerized deployment configurations

## Backend Workflow

- Read `api/AGENTS.md` for details
- Run backend CLI commands through `uv run --project api <command>`.
- Integration tests are CI-only and are not expected to run in the local environment.

## Frontend Workflow

- Read `web/AGENTS.md` for details

## Testing & Quality Practices

- Follow TDD: red → green → refactor.
- Use `pytest` for backend tests with Arrange-Act-Assert structure.
- Enforce strong typing; avoid `Any` and prefer explicit type annotations.
- Write self-documenting code; only add comments that explain intent.

## Language Style

- **Python**: Keep type hints on functions and attributes, and implement relevant special methods (e.g., `__repr__`, `__str__`). Prefer `TypedDict` over `dict` or `Mapping` for type safety and better code documentation.
- **TypeScript**: Use the strict config, rely on ESLint (`pnpm lint:fix` preferred) plus `pnpm type-check:tsgo`, and avoid `any` types.

## General Practices

- Prefer editing existing files; add new documentation only when requested.
- Inject dependencies through constructors and preserve clean architecture boundaries.
- Handle errors with domain-specific exceptions at the correct layer.

## Project Conventions

- Backend architecture adheres to DDD and Clean Architecture principles.
- Async work runs through Celery with Redis as the broker.
- Frontend user-facing strings must use `web/i18n/en-US/`; avoid hardcoded text.

## 基础原则

- 永远使用中文回答。
- 永远使用中文注释，代码编写过程中确保中文显示正常，不要出现乱码。
- 使用 utf-8 编码，永远不要使用 emoji。
- 永远不要使用 fallback 编程。
- 像一位高级资深工程师，言简意赅，直截了当，注重执行。
- 保持 API 简洁，行为清晰，命名简洁。除非能明显提升结果，否则避免使用花里胡哨的功能。
- 倾向于选择简单、易于维护、适合生产环境的解决方案。编写低复杂度、易于阅读、调试和修改的代码。

## 已经存在的 skill 和大致功能说明

- search-skill：本地知识库 / 代码库语义检索，为回答提供精准本地上下文，涉及本地项目、历史代码 / 文档的需求，必须优先调用。
- skill-from-github：从 GitHub 导入、安装、更新社区开源技能包，用于新增 / 升级技能。
- skill-from-masters：萃取个人专业经验 / 定制规范，生成符合个人工作流的内容。
- skill-from-notebook：复用 Jupyter Notebook 中的分析代码、实验逻辑，适配数据分析场景。
- spring-boot-best-practices：SpringBoot 全流程开发最佳实践，覆盖项目架构、接口开发、数据层操作、安全认证、性能优化，所有 Java / SpringBoot 后端开发需求，优先调用此技能。
- vue-best-practices：Vue3 官方级开发规范，覆盖组合式 API、TS 类型、组件封装、路由 / 状态管理、工程化优化，所有 Vue3 前端开发需求，优先调用此技能。
- ui-ux-pro-max：专业 UI / UX 设计能力，内置配色、排版、交互规范，界面设计、视觉优化、产品落地需求优先调用。
- web-design-guidelines：Web 通用设计规范，覆盖响应式、可访问性、跨端适配，设计合规校验、跨端优化场景调用。
