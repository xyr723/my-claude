# 代码风格

## 前端代码风格（主力方向）

### React / JSX
```tsx
// 组件定义：优先使用函数组件 + 箭头函数
const UserCard: React.FC<UserCardProps> = ({ name, avatar }) => {
  return (
    <div className="user-card">
      <img src={avatar} alt={name} />
      <span>{name}</span>
    </div>
  )
}
```

- 组件文件使用 `.tsx` 扩展名
- 每个组件文件只导出一个主组件
- 自定义 Hook 以 `use` 开头，单独文件存放
- 事件处理函数以 `handle` 开头（如 `handleClick`）
- 回调 prop 以 `on` 开头（如 `onSubmit`）
- 状态变量使用 `[value, setValue]` 命名模式
- 可复用 UI 片段必须拆分为独立组件，禁止在页面组件中堆积大量 JSX
- 页面组件（Page/Screen）只负责组合子组件和管理页面级状态，不包含具体 UI 实现
- 拆分粒度参考：出现两次以上的结构、逻辑独立的区块、可独立测试的交互单元

### Vue (如使用)
```vue
<!-- 使用 <script setup lang="ts"> 语法 -->
<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  title: string
  count?: number
}

const props = withDefaults(defineProps<Props>(), {
  count: 0,
})

const doubled = computed(() => props.count * 2)
</script>
```

- 使用 Composition API + `<script setup>`
- Props 使用 TypeScript 接口定义
- 组合式函数以 `use` 开头
- 可复用 UI 片段必须拆分为独立组件，禁止在单个 `.vue` 文件中堆积大量模板
- 页面组件只负责布局编排和页面级状态，具体 UI 实现下沉到子组件
- 拆分粒度参考：出现两次以上的结构、逻辑独立的区块、可独立测试的交互单元

### CSS / 样式
- Tailwind CSS 优先；复杂样式使用 CSS Modules
- 避免深层嵌套（最多 3 层）
- 响应式设计使用移动优先策略
- 颜色、间距等使用设计令牌/CSS 变量
- z-index 使用预定义层级常量

### 异步处理
- 优先使用 `async/await`，避免 `.then()` 链
- 所有异步操作必须有错误处理
- 网络请求统一封装，包含超时和重试机制
- 加载状态和错误状态必须处理

## 后端代码风格（学习方向）

### 通用原则
- API 遵循 RESTful 规范，资源名使用复数
- 错误响应格式统一：`{ code, message, data }`
- 请求/响应使用 DTO 做数据转换
- 数据库操作使用参数化查询，防止 SQL 注入
- 日志分级：debug / info / warn / error

### Go（如使用）
- 遵循 Go 官方编码规范
- 错误处理使用 `if err != nil` 模式，不忽略错误
- 使用 `context` 传递请求上下文

### Python（如使用）
- 遵循 PEP 8 规范
- 使用 type hints
- 使用 `dataclass` 或 `pydantic` 定义数据模型

## 游戏开发代码风格（学习方向）

### Unreal Engine (C++)
- 遵循 UE 编码规范：类名前缀（A/U/F/S/E/I）
- 使用 `UPROPERTY` / `UFUNCTION` 宏暴露属性和方法
- 内存管理使用 UE 的 GC 系统，避免裸指针
- 注释中标注 UE 特定概念（如 Actor、Component、GameMode）

### Unity (C#)
- MonoBehaviour 子类文件名与类名一致
- 使用 `[SerializeField]` 而非 public 字段暴露到编辑器
- 协程用 `IEnumerator`，新项目优先考虑 UniTask
- 遵循 Unity 生命周期顺序组织方法

## 通用格式要求

- 缩进：2 空格（前端）/ 4 空格（后端 Python/C#）/ Tab（Go）
- 行尾无分号（TypeScript/JavaScript，依据项目 ESLint 配置）
- 字符串使用单引号（JS/TS）或双引号（根据项目配置）
- 尾随逗号：多行时始终添加
- 最大行宽：100 字符（前端）/ 120 字符（后端）
