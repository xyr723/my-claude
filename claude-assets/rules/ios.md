# iOS 开发规范

## 语言与框架

### 语言
- **Swift**（唯一选择）— 所有新代码使用 Swift
- **Objective-C** — 仅维护遗留代码或桥接第三方库时使用
- Swift 版本始终跟随项目最低部署版本对应的最新稳定版

### 框架与库
- **UI**: SwiftUI（优先）> UIKit（复杂交互或兼容场景）
- **架构**: MVVM + Clean Architecture / TCA（The Composable Architecture）
- **网络**: URLSession（原生优先）/ Alamofire
- **异步**: Swift Concurrency（async/await + Actor）> Combine > GCD
- **数据持久化**: SwiftData（iOS 17+）/ Core Data / UserDefaults
- **依赖管理**: Swift Package Manager（优先）> CocoaPods
- **图片加载**: Kingfisher / Nuke
- **键值存储**: Keychain（敏感数据）、UserDefaults（非敏感配置）

## 项目结构

```
App/
├── Sources/
│   ├── App/                     # App 入口
│   │   ├── AppDelegate.swift    #   应用代理（如使用 UIKit 生命周期）
│   │   └── MyApp.swift          #   SwiftUI App 入口
│   ├── Data/                    # 数据层
│   │   ├── Network/             #   网络服务（API Client、Endpoint）
│   │   ├── Local/               #   本地存储（Core Data、SwiftData）
│   │   ├── Model/               #   数据模型（DTO、Entity）
│   │   └── Repository/          #   仓库实现
│   ├── Domain/                  # 领域层
│   │   ├── Model/               #   领域模型
│   │   ├── Repository/          #   仓库协议
│   │   └── UseCase/             #   用例
│   ├── Presentation/            # 表现层
│   │   ├── Screens/             #   页面（每个页面一个文件夹）
│   │   │   └── Login/
│   │   │       ├── LoginView.swift
│   │   │       └── LoginViewModel.swift
│   │   ├── Components/          #   可复用 UI 组件
│   │   └── Navigation/          #   导航配置
│   ├── DI/                      # 依赖注入
│   └── Utility/                 # 工具扩展
├── Resources/                   # 资源文件
│   ├── Assets.xcassets
│   ├── Localizable.xcstrings
│   └── Info.plist
├── Tests/                       # 单元测试
└── UITests/                     # UI 测试
```

## 命名规范

### Swift
- **类型（类/结构体/枚举/协议）**: PascalCase — `UserProfile`、`NetworkService`
- **协议**: 描述能力用 `-able`/`-ible`，描述身份用名词 — `Codable`、`DataSource`
- **函数/属性**: camelCase — `fetchUserList()`、`isAuthenticated`
- **常量/静态属性**: camelCase — `static let defaultTimeout: TimeInterval = 30`
- **枚举 case**: camelCase — `case success`、`case networkError`
- **泛型参数**: 单字母大写或 PascalCase — `T`、`Element`、`Response`

### 文件命名
- 文件名与主类型名一致 — `UserRepository.swift`
- 扩展文件: `<类型>+<功能>.swift` — `String+Validation.swift`
- 协议实现: 可使用扩展单独文件 — `UserService+Networking.swift`

### 资源命名
- **图片**: snake_case — `ic_arrow_back`、`bg_login_header`
- **颜色**: 语义化命名 — `primaryText`、`backgroundSecondary`
- **本地化 Key**: 点分层级 — `login.title`、`profile.edit.button`

## SwiftUI 规范

```swift
/// 用户资料卡片
///
/// 展示用户基本信息，支持编辑操作
struct UserProfileCard: View {
    let user: User
    let onEditTap: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 头像和姓名
            HStack {
                AsyncImage(url: user.avatarURL)
                    .frame(width: 48, height: 48)
                    .clipShape(Circle())

                Text(user.name)
                    .font(.headline)
            }

            // 编辑按钮
            Button("编辑", action: onEditTap)
                .buttonStyle(.bordered)
        }
        .padding()
    }
}

#Preview {
    UserProfileCard(
        user: .preview,
        onEditTap: {}
    )
}
```

- **View**: 结构体命名使用名词，后缀可选 `View`/`Screen`/`Cell`
- **body 拆分**: `body` 超过 30 行时，提取子视图为 computed property 或独立组件
- **修饰符顺序**: 布局 → 外观 → 交互 → 动画（从内到外的逻辑顺序）
- **预览**: 每个视图配套 `#Preview`，使用 `.preview` 静态工厂提供模拟数据
- **环境值**: 通过 `@Environment` 获取系统设置，自定义值通过 `EnvironmentKey`

## ViewModel 规范

```swift
/// 登录页面 ViewModel
@MainActor
final class LoginViewModel: ObservableObject {

    // MARK: - 公开状态

    @Published private(set) var uiState = LoginUiState()

    // MARK: - 依赖

    private let loginUseCase: LoginUseCaseProtocol

    // MARK: - 初始化

    init(loginUseCase: LoginUseCaseProtocol) {
        self.loginUseCase = loginUseCase
    }

    // MARK: - 用户操作

    func onLoginTap() async {
        uiState.isLoading = true
        defer { uiState.isLoading = false }

        do {
            try await loginUseCase.execute(
                username: uiState.username,
                password: uiState.password
            )
            uiState.navigateToHome = true
        } catch {
            uiState.errorMessage = error.localizedDescription
        }
    }
}
```

- 标记 `@MainActor` 确保状态更新在主线程
- 使用 `@Published private(set)` 防止外部直接修改状态
- 使用 `MARK` 注释分区组织代码
- ViewModel 不导入 SwiftUI（仅 `import Foundation` / `import Combine`）
- 依赖通过初始化器注入，面向协议编程

## Swift Concurrency

```swift
/// 用户仓库协议
protocol UserRepositoryProtocol: Sendable {
    func fetchUser(id: String) async throws -> User
    func observeUsers() -> AsyncStream<[User]>
}

/// 仓库实现
actor UserRepository: UserRepositoryProtocol {
    private let apiClient: APIClient
    private let database: DatabaseProtocol

    func fetchUser(id: String) async throws -> User {
        // 并发获取远程和本地数据
        async let remote = apiClient.request(UserEndpoint.get(id))
        async let local = database.fetchUser(id: id)

        // 优先使用远程数据，失败时回退本地
        do {
            let user = try await remote
            try await database.save(user)
            return user
        } catch {
            if let cached = try? await local {
                return cached
            }
            throw error
        }
    }
}
```

- 优先使用 `async/await`，替代回调和 Combine
- 使用 `Actor` 保护可变共享状态
- 并行任务使用 `async let` 或 `TaskGroup`
- 使用 `Sendable` 协议保证线程安全
- 取消处理：检查 `Task.isCancelled`，支持 `withTaskCancellationHandler`

## 错误处理

```swift
/// 网络错误类型
enum NetworkError: LocalizedError {
    case invalidResponse(statusCode: Int)
    case decodingFailed(underlying: Error)
    case noConnection
    case serverError(message: String)

    var errorDescription: String? {
        switch self {
        case .invalidResponse(let code):
            return "服务器返回异常状态码: \(code)"
        case .decodingFailed:
            return "数据解析失败"
        case .noConnection:
            return "网络连接不可用"
        case .serverError(let message):
            return message
        }
    }
}
```

- 定义具体的错误枚举，避免使用通用 `NSError`
- 实现 `LocalizedError` 提供用户友好的错误信息
- 错误传播使用 `throws`，不吞没错误
- 在表现层统一处理错误展示

## 性能与安全

### 性能
- 列表使用 `List` / `LazyVStack` + 显式 `id`
- 避免在 `body` 中执行计算，使用 `computed property` 或 `.task` 修饰符
- 图片使用 `AsyncImage` 或缓存库，配置合适的尺寸
- 大数据集使用分页加载
- 使用 Instruments 定期检测内存泄漏和性能瓶颈

### 安全
- 敏感数据（Token、密码）存储在 Keychain
- 网络请求使用 HTTPS，启用 App Transport Security
- 使用 `Codable` 做安全的数据解析
- 禁止在日志中输出敏感信息
- 配置 `Info.plist` 中的隐私使用说明（相机、位置等权限）
- Release 构建禁用调试日志输出

## 测试规范

```swift
@MainActor
final class LoginViewModelTests: XCTestCase {
    private var sut: LoginViewModel!
    private var mockLoginUseCase: MockLoginUseCase!

    override func setUp() {
        super.setUp()
        mockLoginUseCase = MockLoginUseCase()
        sut = LoginViewModel(loginUseCase: mockLoginUseCase)
    }

    override func tearDown() {
        sut = nil
        mockLoginUseCase = nil
        super.tearDown()
    }

    func test_登录成功_应导航到首页() async {
        // Given
        mockLoginUseCase.result = .success(())
        sut.uiState.username = "test"
        sut.uiState.password = "password"

        // When
        await sut.onLoginTap()

        // Then
        XCTAssertTrue(sut.uiState.navigateToHome)
        XCTAssertNil(sut.uiState.errorMessage)
    }
}
```

- 测试方法命名: `test_场景_预期结果`（中文描述增强可读性）
- 使用 Given-When-Then 结构组织测试
- Mock 依赖通过协议注入
- ViewModel 测试标记 `@MainActor`
- UI 测试使用 `XCUITest`，关键流程必须覆盖
