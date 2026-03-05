# 编码偏好

## 语言与环境

### 主力方向：前端开发
- **语言**: TypeScript（优先）、JavaScript
- **框架**: React / Vue / Svelte（根据项目选择）
- **样式**: Tailwind CSS / CSS Modules / Styled Components
- **构建**: Vite（优先）、Webpack、Turbopack
- **包管理**: pnpm（优先）> yarn > npm
- **运行时**: Node.js、Bun

### 学习方向：后端开发
- **语言**: Go / Java / Python / Rust（根据项目选择）
- **框架**: Gin / Spring Boot / FastAPI / Actix-web 等
- 后端代码需额外注释说明设计意图，方便学习理解

### 学习方向：移动端开发
- **Android**: Kotlin + Jetpack Compose + Hilt + Coroutines（详见 `android.md`）
- **iOS**: Swift + SwiftUI + Swift Concurrency（详见 `ios.md`）
- 移动端代码需额外注释说明平台特有概念和生命周期行为

### 学习方向：游戏开发
- **引擎**: Unreal Engine (C++) / Unity (C#)
- **脚本**: Blueprint（UE）、Lua（可选）
- 游戏开发代码需附带引擎概念说明和参考文档链接

## 全局约束

### 禁止 Emoji
- 代码、注释、commit message、文档、CLI 输出中一律不使用 emoji
- 使用纯文本标记替代（如 `[WARNING]` 而非警告符号）

### Python 工具链
- **优先使用 `uv`** 作为 Python 包管理器和虚拟环境管理工具
- `uv` > `pip` > `poetry` > `conda`
- 创建虚拟环境: `uv venv`
- 安装依赖: `uv pip install` / `uv add`
- 运行脚本: `uv run`
- 锁定依赖: `uv lock`

## 通用偏好

### 类型系统
- 始终使用严格类型，禁止 `any`（TypeScript 中使用 `unknown` 替代）
- 优先使用 `interface` 定义对象类型，`type` 用于联合/交叉/工具类型
- 函数参数和返回值必须有类型注解

### 命名规范
- **变量/函数**: camelCase（如 `getUserInfo`）
- **常量**: UPPER_SNAKE_CASE（如 `MAX_RETRY_COUNT`）
- **类/组件/类型**: PascalCase（如 `UserProfile`）
- **文件名（组件）**: PascalCase（如 `UserCard.tsx`）
- **文件名（工具/配置）**: camelCase 或 kebab-case
- **CSS 类名**: kebab-case 或 BEM
- **布尔变量**: 使用 `is`/`has`/`should`/`can` 前缀

### 代码质量
- 函数行数不超过 50 行，超出则拆分
- 嵌套层级不超过 3 层
- 单个文件不超过 300 行
- 组件 props 超过 3 个时使用接口定义
- 避免魔法数字，使用具名常量
- 错误处理不得吞没异常（空 catch）

### 注释规范
- **语言**: 全部使用中文
- 函数/组件使用 JSDoc/TSDoc 注释
- 复杂逻辑添加行内注释说明"为什么"，而非"做了什么"
- TODO 格式: `// TODO(作者): 描述 — 日期`
- FIXME 格式: `// FIXME(作者): 描述 — 日期`

### 导入顺序
```
1. 框架/运行时（react, vue, node:*）
2. 第三方库（按字母排序）
3. 项目内部模块（@/）
4. 相对路径模块
5. 样式文件
6. 类型导入（type imports 放最后）
```
