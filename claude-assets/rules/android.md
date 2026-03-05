# Android 开发规范

## 语言与框架

### 语言
- **Kotlin**（唯一选择）— 所有新代码使用 Kotlin
- **Java** — 仅维护遗留代码时使用，不得在新模块中引入
- Kotlin 版本与 AGP（Android Gradle Plugin）保持兼容

### 框架与库
- **UI**: Jetpack Compose（优先）> XML + View（维护旧页面）
- **架构**: MVVM + Clean Architecture + MVI（单向数据流）
- **导航**: Navigation Compose / Navigation Component
- **网络**: Retrofit + OkHttp + Kotlin Serialization
- **异步**: Kotlin Coroutines + Flow
- **数据持久化**: Room（数据库）/ DataStore（键值对）
- **依赖注入**: Hilt / Koin
- **图片加载**: Coil（Compose 首选）/ Glide
- **构建**: Gradle Kotlin DSL（`build.gradle.kts`）
- **版本管理**: Version Catalog（`libs.versions.toml`）

## 项目结构

### 单模块项目
```
app/
├── src/main/
│   ├── java/com/example/app/
│   │   ├── App.kt                    # Application 入口
│   │   ├── MainActivity.kt           # 主 Activity
│   │   ├── data/                     # 数据层
│   │   │   ├── remote/               #   远程数据源（API Service、DTO）
│   │   │   ├── local/                #   本地数据源（Room DAO、DataStore）
│   │   │   ├── model/                #   数据模型（Entity、DTO）
│   │   │   └── repository/           #   仓库实现
│   │   ├── domain/                   # 领域层
│   │   │   ├── model/                #   领域模型
│   │   │   ├── repository/           #   仓库接口
│   │   │   └── usecase/              #   用例
│   │   ├── presentation/             # 表现层
│   │   │   ├── screen/               #   页面（每个页面一个包）
│   │   │   │   └── login/
│   │   │   │       ├── LoginScreen.kt
│   │   │   │       ├── LoginViewModel.kt
│   │   │   │       └── LoginUiState.kt
│   │   │   ├── component/            #   可复用 Compose 组件
│   │   │   ├── navigation/           #   导航图配置
│   │   │   └── theme/                #   主题（Color、Type、Theme）
│   │   ├── di/                       # 依赖注入模块
│   │   └── util/                     # 工具类
│   ├── res/                          # 资源文件
│   └── AndroidManifest.xml
├── build.gradle.kts
└── proguard-rules.pro
```

### 多模块项目
```
project/
├── app/                              # 壳模块：组装依赖、配置入口
├── core/
│   ├── core-network/                 # 网络基础设施
│   ├── core-database/                # 数据库基础设施
│   ├── core-ui/                      # 公共 UI 组件和主题
│   ├── core-common/                  # 通用工具
│   └── core-model/                   # 共享数据模型
├── feature/
│   ├── feature-login/                # 登录功能模块
│   ├── feature-home/                 # 首页功能模块
│   └── feature-profile/              # 个人中心功能模块
├── gradle/
│   └── libs.versions.toml            # 版本目录
├── build-logic/                      # 自定义 Gradle 插件（Convention Plugins）
└── settings.gradle.kts
```

- 模块间依赖遵循 **依赖倒置**：`feature` → `domain` ← `data`
- `feature` 模块间互不依赖
- `core` 模块提供基础能力，不包含业务逻辑

## 命名规范

### Kotlin
- **类/接口/对象**: PascalCase — `UserRepository`、`NetworkModule`
- **函数/属性**: camelCase — `fetchUserList()`、`isLoggedIn`
- **常量**: UPPER_SNAKE_CASE — `const val MAX_RETRY_COUNT = 3`
- **包名**: 全小写，不用下划线 — `com.example.app.data.repository`
- **Compose 函数（UI）**: PascalCase — `@Composable fun UserCard()`
- **Compose 函数（非 UI）**: camelCase — `fun rememberScrollState()`

### 文件命名
- 文件名与主类型名一致 — `UserRepository.kt`
- Compose 页面: `<功能>Screen.kt` — `LoginScreen.kt`
- ViewModel: `<功能>ViewModel.kt` — `LoginViewModel.kt`
- UI 状态: `<功能>UiState.kt` — `LoginUiState.kt`
- Hilt Module: `<范围>Module.kt` — `NetworkModule.kt`

### 资源命名
- **布局**: `<类型>_<功能>.xml` — `activity_main.xml`、`fragment_login.xml`
- **Drawable**: `<类型>_<描述>.xml` — `ic_arrow_back.xml`、`bg_rounded_card.xml`
- **字符串**: snake_case，带层级前缀 — `login_title`、`profile_edit_button`
- **尺寸**: `<用途>_<大小>.xml` — `margin_small`、`text_size_body`
- **颜色**: 语义化命名 — `color_primary`、`color_text_secondary`

## Jetpack Compose 规范

```kotlin
/**
 * 用户资料卡片
 *
 * @param user 用户数据
 * @param onEditClick 编辑按钮点击回调
 * @param modifier 外部传入的修饰符
 */
@Composable
fun UserProfileCard(
    user: User,
    onEditClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Card(modifier = modifier) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            // 用户头像
            AsyncImage(
                model = user.avatarUrl,
                contentDescription = "${user.name}的头像",
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape),
                contentScale = ContentScale.Crop,
            )

            // 用户姓名
            Text(
                text = user.name,
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.weight(1f),
            )

            // 编辑按钮
            IconButton(onClick = onEditClick) {
                Icon(
                    imageVector = Icons.Default.Edit,
                    contentDescription = "编辑",
                )
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
private fun UserProfileCardPreview() {
    AppTheme {
        UserProfileCard(
            user = User.preview(),
            onEditClick = {},
        )
    }
}
```

- **Modifier 参数**: 始终作为第一个可选参数，默认值 `Modifier`
- **尾随逗号**: 多行参数始终添加尾随逗号
- **Preview**: 每个公开组件配套 `@Preview`，使用 `private` 修饰
- **无状态优先**: 组件尽量设计为无状态（Stateless），状态由调用方传入
- **contentDescription**: 所有图片/图标必须提供无障碍描述
- **主题引用**: 颜色和字体始终通过 `MaterialTheme` 引用，禁止硬编码

## ViewModel 与状态管理

```kotlin
/**
 * 登录页面 ViewModel
 */
@HiltViewModel
class LoginViewModel @Inject constructor(
    private val loginUseCase: LoginUseCase,
) : ViewModel() {

    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()

    /** 单次事件（导航、Toast 等） */
    private val _events = Channel<LoginEvent>(Channel.BUFFERED)
    val events: Flow<LoginEvent> = _events.receiveAsFlow()

    fun onAction(action: LoginAction) {
        when (action) {
            is LoginAction.UsernameChanged -> {
                _uiState.update { it.copy(username = action.value) }
            }
            is LoginAction.PasswordChanged -> {
                _uiState.update { it.copy(password = action.value) }
            }
            is LoginAction.LoginClicked -> login()
        }
    }

    private fun login() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            loginUseCase(
                username = _uiState.value.username,
                password = _uiState.value.password,
            ).onSuccess {
                _events.send(LoginEvent.NavigateToHome)
            }.onFailure { error ->
                _uiState.update {
                    it.copy(errorMessage = error.localizedMessage)
                }
            }

            _uiState.update { it.copy(isLoading = false) }
        }
    }
}

/** UI 状态 — 不可变数据类 */
data class LoginUiState(
    val username: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
)

/** 用户操作 — 密封接口 */
sealed interface LoginAction {
    data class UsernameChanged(val value: String) : LoginAction
    data class PasswordChanged(val value: String) : LoginAction
    data object LoginClicked : LoginAction
}

/** 单次事件 — 密封接口 */
sealed interface LoginEvent {
    data object NavigateToHome : LoginEvent
    data class ShowToast(val message: String) : LoginEvent
}
```

- **单向数据流**: Action → ViewModel → UiState → UI
- **UiState**: 使用 `data class`，`StateFlow` 暴露，不可变
- **单次事件**: 使用 `Channel` + `receiveAsFlow`（导航、Toast 等不重复消费的事件）
- **Action 密封类**: 所有用户操作封装为 `sealed interface`
- ViewModel 不持有 `Context`、`Activity`、`View` 引用
- 使用 `viewModelScope` 管理协程生命周期

## Kotlin Coroutines + Flow

```kotlin
/**
 * 用户仓库实现
 */
class UserRepositoryImpl @Inject constructor(
    private val apiService: UserApiService,
    private val userDao: UserDao,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher,
) : UserRepository {

    /** 获取用户列表，支持离线回退 */
    override fun getUsers(): Flow<Result<List<User>>> = flow {
        // 先返回本地缓存
        val cached = userDao.getAllUsers().map { it.toDomain() }
        if (cached.isNotEmpty()) {
            emit(Result.success(cached))
        }

        // 拉取远程数据并更新缓存
        runCatching {
            apiService.getUsers()
        }.onSuccess { response ->
            val users = response.map { it.toDomain() }
            userDao.insertAll(response.map { it.toEntity() })
            emit(Result.success(users))
        }.onFailure { error ->
            if (cached.isEmpty()) {
                emit(Result.failure(error))
            }
        }
    }.flowOn(ioDispatcher)
}
```

- IO 操作使用 `Dispatchers.IO`，通过注入 `@IoDispatcher` 便于测试
- 使用 `flowOn` 指定上游执行线程
- 在 Compose 中使用 `collectAsStateWithLifecycle()` 收集 Flow
- 错误处理使用 `Result` 类型或自定义 `sealed class`
- 取消处理：协程自动支持取消，不阻塞非取消安全的调用
- 避免 `GlobalScope`，始终使用结构化并发

## Hilt 依赖注入

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = if (BuildConfig.DEBUG) {
                    HttpLoggingInterceptor.Level.BODY
                } else {
                    HttpLoggingInterceptor.Level.NONE
                }
            })
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
            .build()
    }
}

/** 仓库绑定 */
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(
        impl: UserRepositoryImpl,
    ): UserRepository
}
```

- 使用 `@Provides` 提供第三方库实例
- 使用 `@Binds` 绑定接口与实现
- Scope 选择: `@Singleton`（全局）/ `@ViewModelScoped` / `@ActivityScoped`
- Debug 和 Release 的网络配置分离
- ViewModel 使用 `@HiltViewModel` + `@Inject constructor`

## 错误处理

```kotlin
/** 应用统一错误类型 */
sealed class AppError : Exception() {
    /** 网络错误 */
    data class Network(
        val code: Int? = null,
        override val message: String = "网络连接异常",
    ) : AppError()

    /** 服务端错误 */
    data class Server(
        val code: String,
        override val message: String,
    ) : AppError()

    /** 本地数据错误 */
    data class Local(
        override val message: String = "本地数据异常",
        override val cause: Throwable? = null,
    ) : AppError()

    /** 未知错误 */
    data class Unknown(
        override val cause: Throwable,
    ) : AppError() {
        override val message: String = "发生未知错误"
    }
}

/** Result 扩展 — 统一错误映射 */
inline fun <T> safeApiCall(block: () -> T): Result<T> {
    return try {
        Result.success(block())
    } catch (e: IOException) {
        Result.failure(AppError.Network())
    } catch (e: HttpException) {
        Result.failure(AppError.Server(code = e.code().toString(), message = e.message()))
    } catch (e: Exception) {
        Result.failure(AppError.Unknown(cause = e))
    }
}
```

- 定义 `sealed class` 错误层级
- 使用 `Result<T>` 包装返回值，不在仓库层抛异常
- `safeApiCall` 统一捕获并映射异常
- 在 UI 层根据错误类型展示不同提示

## 性能与安全

### 性能
- Compose: 使用 `key()` / `remember` / `derivedStateOf` 避免不必要重组
- 列表: 使用 `LazyColumn` / `LazyRow`，item 配 `key` 参数
- 图片: 指定尺寸加载，避免全尺寸解码
- 避免在 Composition 中执行副作用，使用 `LaunchedEffect` / `SideEffect`
- 使用 Baseline Profiles 优化启动性能
- 使用 R8/ProGuard 混淆和压缩 Release 包

### 安全
- 敏感数据使用 `EncryptedSharedPreferences` / `EncryptedFile`
- 网络请求使用 HTTPS，配置证书固定（Certificate Pinning）
- API Key 通过 `BuildConfig` 或 NDK 注入，不硬编码在源码中
- 禁止在日志中输出敏感信息（Timber 自定义 Tree 过滤 Release 日志）
- 混淆规则正确配置，保护关键业务逻辑
- 输入验证在客户端和服务端双重执行

## 测试规范

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class LoginViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var sut: LoginViewModel
    private lateinit var fakeLoginUseCase: FakeLoginUseCase

    @Before
    fun setup() {
        fakeLoginUseCase = FakeLoginUseCase()
        sut = LoginViewModel(loginUseCase = fakeLoginUseCase)
    }

    @Test
    fun `登录成功时应发送导航事件`() = runTest {
        // Given
        fakeLoginUseCase.result = Result.success(Unit)
        sut.onAction(LoginAction.UsernameChanged("test"))
        sut.onAction(LoginAction.PasswordChanged("password"))

        // When
        sut.onAction(LoginAction.LoginClicked)

        // Then
        val event = sut.events.first()
        assertThat(event).isEqualTo(LoginEvent.NavigateToHome)
        assertThat(sut.uiState.value.isLoading).isFalse()
    }

    @Test
    fun `登录失败时应展示错误信息`() = runTest {
        // Given
        fakeLoginUseCase.result = Result.failure(AppError.Network())

        // When
        sut.onAction(LoginAction.LoginClicked)

        // Then
        assertThat(sut.uiState.value.errorMessage).isNotNull()
        assertThat(sut.uiState.value.isLoading).isFalse()
    }
}
```

- 测试方法命名: 反引号 + 中文描述 — `` `登录成功时应发送导航事件` ``
- 使用 `MainDispatcherRule` 替换主线程调度器
- 使用 Fake/Stub 替代 Mock（优先可读性）
- 使用 `runTest` 执行协程测试
- 使用 Truth（`assertThat`）或 kotlin.test 断言
- Compose UI 测试使用 `createComposeRule()`
