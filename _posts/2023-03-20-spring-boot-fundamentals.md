---
layout: post
title: "Spring Boot Fundamentals Cheatsheet"
description: >-
  Personal cheatsheet for Spring Boot fundamentals. Covers Maven, IoC/DI, AOP, beans, configuration, REST, JPA, security, testing, and more.
author: ryo
date: 2023-03-20 00:00:00 +0800
categories: [Software Engineering]
tags: [spring, spring-boot, java, cheatsheet]
toc: true
comments: true
pin: false
published: true
---

## 1. Project Setup

### 1.1. Spring Initializr

Generate a project at [start.spring.io](https://start.spring.io) or via IntelliJ. Choose:
- **Project:** Maven
- **Language:** Java
- **Spring Boot version:** 3.x
- **Packaging:** Jar (most common) or War (for external servlet container)
- **Java:** 17 or 21

### 1.2. Group, Artifact, Package Name

| Field | Example | Meaning |
|---|---|---|
| `groupId` | `com.example` | Organisation/domain (reverse domain) |
| `artifactId` | `my-app` | Project name / module name |
| `version` | `0.0.1-SNAPSHOT` | Build version. `SNAPSHOT` = in-development |
| `name` | `my-app` | Display name |
| `package name` | `com.example.myapp` | Root Java package for source files |

### 1.3. JAR vs WAR

| | JAR | WAR |
|---|---|---|
| Contains | App + embedded Tomcat | App only (no server) |
| Deployment | Run directly with `java -jar` | Deploy to external Tomcat/JBoss |
| Default in Spring Boot | yes | Needs `extends SpringBootServletInitializer` |

### 1.4. Standard Maven Project Layout

```
my-app/
├── pom.xml
└── src/
    ├── main/
    │   ├── java/com/example/myapp/
    │   │   └── MyAppApplication.java
    │   └── resources/
    │       ├── application.yml
    │       └── static/      # served as-is (CSS, JS)
    │       └── templates/   # Thymeleaf etc.
    └── test/
        └── java/com/example/myapp/
```

---

## 2. Maven Essentials

### 2.1. `pom.xml` Anatomy

```xml
<project>
  <modelVersion>4.0.0</modelVersion>

  <!-- Project coordinates -->
  <groupId>com.example</groupId>
  <artifactId>my-app</artifactId>
  <version>0.0.1-SNAPSHOT</version>
  <packaging>jar</packaging>

  <!-- Inherit Spring Boot defaults -->
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.0</version>
  </parent>

  <properties>
    <java.version>17</java.version>
  </properties>

  <dependencies>
    <!-- Starters pull in all needed transitive dependencies -->
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-test</artifactId>
      <scope>test</scope>   <!-- only on test classpath -->
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <!-- Allows mvn spring-boot:run and creates executable fat JAR -->
      <plugin>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-maven-plugin</artifactId>
      </plugin>
    </plugins>
  </build>
</project>
```

### 2.2. Dependencies vs Plugins

| | `<dependencies>` | `<plugins>` |
|---|---|---|
| Purpose | Libraries your code needs at compile/runtime/test | Tools that participate in the build process |
| Example | `spring-boot-starter-web` | `spring-boot-maven-plugin` |
| On classpath? | yes | no |

### 2.3. What Is the Classpath?

List of directories and JARs the JVM searches when loading classes. Maven manages this by scope:

| Scope | Compile | Test | Runtime JAR |
|---|---|---|---|
| `compile` (default) | yes | yes | yes |
| `test` | no | yes | no |
| `runtime` | no | yes | yes |
| `provided` | yes | yes | no (e.g. servlet API when WAR) |

### 2.4. Maven Lifecycle Phases

Phases run sequentially - running a later phase runs all prior ones.

| Phase | What it does |
|---|---|
| `validate` | Validate project structure |
| `compile` | Compile `src/main/java` |
| `test` | Run unit tests (`src/test/java`) |
| `package` | Package into JAR/WAR |
| `verify` | Run integration tests |
| `install` | Install artifact to local `~/.m2` repository |
| `deploy` | Push to remote repository |

### 2.5. Common Commands

```bash
mvn clean                    # delete target/ directory
mvn compile                  # compile source
mvn test                     # run tests
mvn package                  # build the JAR
mvn clean install            # clean build + install to local repo
mvn clean install -DskipTests # skip tests

mvn spring-boot:run          # run app directly (no JAR needed)
java -jar target/my-app.jar  # run the built fat JAR

mvn dependency:tree          # show full dependency tree
mvn dependency:resolve       # download all dependencies
```

### 2.6. Spring Boot Starters

Each starter is a single dependency that pulls in all transitive dependencies needed for a feature.

| Starter | What it brings |
|---|---|
| `spring-boot-starter-web` | Spring MVC, Tomcat, Jackson |
| `spring-boot-starter-data-jpa` | Hibernate, Spring Data JPA, JDBC |
| `spring-boot-starter-security` | Spring Security |
| `spring-boot-starter-test` | JUnit 5, Mockito, MockMvc, AssertJ |
| `spring-boot-starter-validation` | Hibernate Validator |
| `spring-boot-starter-actuator` | Health, metrics, info endpoints |
| `spring-boot-starter-aop` | AspectJ for AOP |
| `spring-boot-starter-mail` | JavaMail integration |
| `spring-boot-starter-cache` | Spring Cache abstraction |

---

## 3. IoC Container & Dependency Injection

### 3.1. Inversion of Control (IoC)

Traditional code: **you** create and manage dependencies (`new Service()`).

IoC: the **container** creates and manages objects. You declare what you need, the container wires it.

### 3.2. ApplicationContext vs BeanFactory

| | `BeanFactory` | `ApplicationContext` |
|---|---|---|
| Basic DI | yes | yes |
| Eager bean init | no (lazy) | yes (by default) |
| Event publishing | no | yes |
| AOP integration | no | yes |
| i18n, MessageSource | no | yes |
| Use in Spring Boot | Never directly | `SpringApplication.run()` returns this |

```java
ApplicationContext ctx = SpringApplication.run(MyApp.class, args);
MyService svc = ctx.getBean(MyService.class); // manual retrieval - rarely needed
```

### 3.3. Types of Dependency Injection

**Constructor Injection (preferred):**
```java
@Service
public class OrderService {
    private final PaymentService paymentService;

    public OrderService(PaymentService paymentService) { // Spring injects this
        this.paymentService = paymentService;
    }
}
// If only one constructor exists, @Autowired is optional (Spring Boot auto-detects)
```

**Setter Injection (optional dependencies):**
```java
@Service
public class OrderService {
    private PaymentService paymentService;

    @Autowired
    public void setPaymentService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }
}
```

**Field Injection (avoid - hard to test, hides dependencies):**
```java
@Service
public class OrderService {
    @Autowired
    private PaymentService paymentService; // works but discouraged
}
```

---

## 4. Configuration Classes in Depth

### 4.1. `@Configuration` and `@Bean`

`@Configuration` marks a class as a source of bean definitions. Methods annotated with `@Bean` are factory methods - the return value becomes a Spring-managed bean.

```java
@Configuration
public class AppConfig {

    @Bean
    public DataSource dataSource() {
        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl("jdbc:postgresql://localhost:5432/mydb");
        ds.setUsername("user");
        ds.setPassword("pass");
        return ds;
    }

    @Bean
    public JdbcTemplate jdbcTemplate(DataSource dataSource) { // Spring injects the bean above
        return new JdbcTemplate(dataSource);
    }
}
```

`@Configuration` classes are CGLIB-proxied by default - calling `dataSource()` from within the config class returns the **same singleton bean**, not a new instance each time.

### 4.2. `@Import`

Include another configuration class without component scanning:

```java
@Configuration
@Import({DatabaseConfig.class, SecurityConfig.class})
public class AppConfig { ... }
```

### 4.3. `@PropertySource`

Load additional `.properties` files into the `Environment`:

```java
@Configuration
@PropertySource("classpath:custom.properties")
public class AppConfig {
    @Value("${custom.timeout}")
    private int timeout;
}
```

### 4.4. Conditional Beans

```java
// Only create bean if a condition is met
@Bean
@ConditionalOnProperty(name = "feature.cache.enabled", havingValue = "true")
public CacheManager cacheManager() { return new ConcurrentMapCacheManager(); }

@Bean
@ConditionalOnMissingBean(DataSource.class)  // only if no DataSource bean exists
public DataSource defaultDataSource() { ... }

@Bean
@ConditionalOnClass(name = "com.example.SomeLibrary") // only if class on classpath
public SomeLibraryIntegration integration() { ... }

@Bean
@Profile("prod") // only active when 'prod' profile is active
public EmailSender realEmailSender() { ... }

@Bean
@Profile("dev")
public EmailSender fakeEmailSender() { ... }
```

### 4.5. `@EnableXxx` Annotations

Used on `@Configuration` classes to activate specific Spring features:

| Annotation | Effect |
|---|---|
| `@EnableAutoConfiguration` | Turns on Spring Boot auto-config (included in `@SpringBootApplication`) |
| `@EnableWebMvc` | Full control over MVC config (disables Spring Boot MVC auto-config) |
| `@EnableJpaRepositories` | Enable Spring Data JPA repo scanning |
| `@EnableTransactionManagement` | Enable `@Transactional` support |
| `@EnableAsync` | Enable `@Async` method execution |
| `@EnableScheduling` | Enable `@Scheduled` tasks |
| `@EnableCaching` | Enable Spring's cache abstraction |
| `@EnableAspectJAutoProxy` | Enable AOP via AspectJ |

---

## 5. Auto-Configuration

### 5.1. How It Works

`@SpringBootApplication` includes `@EnableAutoConfiguration`, which triggers the auto-configuration mechanism:

1. Spring Boot reads `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` from all JARs on the classpath
2. Each entry is an `@AutoConfiguration` class gated by `@Conditional` annotations
3. If the conditions are met (e.g. a class is on the classpath, a property is set), the beans are registered
4. Your own beans take priority - auto-configured beans only register if you haven't defined one

```java
// Example: DataSourceAutoConfiguration only activates if:
// - spring-jdbc is on the classpath
// - No DataSource bean is already defined
@AutoConfiguration
@ConditionalOnClass({ DataSource.class, EmbeddedDatabaseType.class })
@ConditionalOnMissingBean(DataSource.class)
public class DataSourceAutoConfiguration { ... }
```

### 5.2. Debugging Auto-Configuration

```bash
# Add to application.yml to see what was configured and why
logging.level.org.springframework.boot.autoconfigure=DEBUG

# Or run with --debug flag
java -jar app.jar --debug
```

The "Conditions Evaluation Report" on startup shows every auto-configuration class and whether it was applied or skipped.

---

## 6. Beans & Stereotypes

### 6.1. Stereotype Annotations

All are specialisations of `@Component` - picked up by component scanning:

| Annotation | Layer | Extra behaviour |
|---|---|---|
| `@Component` | Generic | Base stereotype |
| `@Service` | Business logic | None (semantic only) |
| `@Repository` | Data access | Wraps persistence exceptions into `DataAccessException` |
| `@Controller` | Web MVC | Handles HTTP, returns view name |
| `@RestController` | Web REST | `@Controller` + `@ResponseBody` on all methods |
| `@Configuration` | Config | CGLIB proxy for `@Bean` methods |

### 6.2. Component Scanning

`@SpringBootApplication` includes `@ComponentScan`, which scans the main class package and all sub-packages. Any `@Component` class (or stereotype) in those packages gets registered as a bean.

```java
// If you need to scan additional packages:
@ComponentScan(basePackages = {"com.example.app", "com.example.shared"})
```

### 6.3. Key DI Annotations

| Annotation | Purpose |
|---|---|
| `@Autowired` | Inject a dependency by type |
| `@Qualifier("beanName")` | Disambiguate when multiple beans of same type exist |
| `@Primary` | Mark one bean as default when multiple exist |
| `@Value("${prop.key}")` | Inject a property value |
| `@Lazy` | Delay bean initialisation until first use |
| `@DependsOn("otherBean")` | Force another bean to be initialised first |

```java
// Multiple implementations of same interface
@Service @Primary
public class EmailNotificationService implements NotificationService { ... }

@Service @Qualifier("sms")
public class SmsNotificationService implements NotificationService { ... }

// Injection
@Autowired
private NotificationService notificationService; // gets EmailNotificationService (Primary)

@Autowired @Qualifier("sms")
private NotificationService smsService;          // gets SmsNotificationService explicitly
```

---

## 7. Bean Lifecycle

```
1. Instantiation          - Spring creates the object (calls constructor)
2. Dependency Injection   - Spring injects all dependencies (@Autowired, @Value, etc.)
3. @PostConstruct         - Your initialisation logic (runs after DI is complete)
4. In Use                 - Bean serves requests
5. @PreDestroy            - Your cleanup logic (runs before bean is destroyed)
6. Destruction            - Bean is removed from context
```

```java
@Service
public class CacheService {

    private Map<String, Object> cache;

    @PostConstruct
    public void init() {
        cache = new HashMap<>();
        System.out.println("Cache initialized");
    }

    @PreDestroy
    public void cleanup() {
        cache.clear();
        System.out.println("Cache cleared");
    }
}
```

Alternatively, use `InitializingBean` / `DisposableBean` interfaces, or specify `initMethod`/`destroyMethod` in `@Bean`:

```java
@Bean(initMethod = "init", destroyMethod = "close")
public DataSource dataSource() { ... }
```

---

## 8. Bean Scopes

| Scope | One instance per... | Default |
|---|---|---|
| `singleton` | Spring container (entire app) | yes |
| `prototype` | Each request for the bean (`getBean()` call) | no |
| `request` | HTTP request (web-aware contexts only) | no |
| `session` | HTTP session (web-aware contexts only) | no |
| `application` | `ServletContext` (one per app) | no |

```java
@Component
@Scope("prototype") // or use ConfigurableBeanFactory.SCOPE_PROTOTYPE constant
public class ReportGenerator { ... }
```

**Singleton + Prototype injection problem:** If a singleton bean needs a new prototype instance per method call, inject `ApplicationContext` or use `@Lookup`:

```java
@Component
public class OrderProcessor {
    @Autowired
    private ApplicationContext ctx;

    public void process() {
        ReportGenerator gen = ctx.getBean(ReportGenerator.class); // new instance each time
    }
}
```

---

## 9. AOP (Aspect-Oriented Programming)

### 9.1. What It Is

Separates **cross-cutting concerns** (logging, security, transactions, metrics) from business logic. Define the logic once in an **Aspect**, apply it to many methods via **pointcuts**.

Key concepts:
- **Aspect** - the module containing cross-cutting logic
- **Advice** - the code to run (`@Before`, `@After`, `@Around`, etc.)
- **Pointcut** - expression that selects which methods to intercept
- **Join point** - specific point in execution (method call, in Spring AOP)
- **Weaving** - linking aspects to target code (Spring does this at runtime via proxies)

### 9.2. Dependency

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-aop</artifactId>
</dependency>
```

### 9.3. Advice Types

Advice is the code that executes at a join point. Spring AOP provides five types: `@Before`, `@AfterReturning`, `@AfterThrowing`, `@After` (finally), and `@Around`.

```java
@Aspect
@Component
public class LoggingAspect {

    // Runs before the matched method
    @Before("execution(* com.example.service.*.*(..))")
    public void logBefore(JoinPoint jp) {
        System.out.println("Calling: " + jp.getSignature().getName());
    }

    // Runs after method returns (not on exception)
    @AfterReturning(pointcut = "execution(* com.example.service.*.*(..))", returning = "result")
    public void logAfterReturning(Object result) {
        System.out.println("Returned: " + result);
    }

    // Runs after exception is thrown
    @AfterThrowing(pointcut = "execution(* com.example.service.*.*(..))", throwing = "ex")
    public void logAfterThrowing(Exception ex) {
        System.err.println("Exception: " + ex.getMessage());
    }

    // Runs after method regardless (like finally)
    @After("execution(* com.example.service.*.*(..))")
    public void logAfter(JoinPoint jp) { ... }

    // Wraps the method - most powerful
    @Around("execution(* com.example.service.*.*(..))")
    public Object logAround(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        Object result = pjp.proceed(); // call the actual method
        long elapsed = System.currentTimeMillis() - start;
        System.out.println(pjp.getSignature().getName() + " took " + elapsed + "ms");
        return result;
    }
}
```

### 9.4. Pointcut Expressions

Pointcut expressions use AspectJ syntax to select which methods advice applies to. Named pointcuts (`@Pointcut`) can be reused across multiple advice methods.

```java
// All methods in a package
execution(* com.example.service.*.*(..))

// Specific method
execution(public String com.example.service.UserService.findById(Long))

// Methods with a specific annotation
@annotation(org.springframework.transaction.annotation.Transactional)

// All public methods
execution(public * *(..))

// Combined
@Pointcut("execution(* com.example.service.*.*(..))")
private void serviceLayer() {}

@Before("serviceLayer()")
public void logService(JoinPoint jp) { ... }
```

### 9.5. Limitations

Spring AOP only works on Spring-managed beans and only intercepts **external method calls** through the proxy. A method calling another method on the same bean bypasses the proxy - the advice won't run.

---

## 10. Properties & YAML Configuration

### 10.1. `application.yml` vs `application.properties`

Both are equivalent - YAML is more readable for hierarchical config.

```yaml
# application.yml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/mydb
    username: user
    password: secret
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true

app:
  feature:
    cache-enabled: true
  max-upload-size: 10MB
```

```properties
# application.properties equivalent
server.port=8080
spring.datasource.url=jdbc:postgresql://localhost:5432/mydb
```

### 10.2. Injecting Properties

```java
// Single value
@Value("${app.max-upload-size}")
private String maxUploadSize;

@Value("${app.feature.cache-enabled:false}") // with default
private boolean cacheEnabled;

// Whole group of properties - type-safe
@ConfigurationProperties(prefix = "app.feature")
@Component // or used with @EnableConfigurationProperties on a @Configuration class
public class FeatureProperties {
    private boolean cacheEnabled;  // maps to app.feature.cache-enabled
    private int retryCount;        // maps to app.feature.retry-count
    // getters and setters required (or use record)
}
```

```java
@Autowired
private FeatureProperties featureProps;

featureProps.isCacheEnabled();
```

### 10.3. Profiles

Activate different config per environment:

```yaml
# application.yml - shared base config
app:
  name: MyApp

---
# Profile-specific section (Spring Boot 2.4+)
spring:
  config:
    activate:
      on-profile: dev
spring.datasource.url: jdbc:h2:mem:testdb

---
spring:
  config:
    activate:
      on-profile: prod
spring.datasource.url: jdbc:postgresql://prod-db:5432/mydb
```

Or use separate files: `application-dev.yml`, `application-prod.yml`

```bash
# Activate a profile
java -jar app.jar --spring.profiles.active=prod
# Or in YAML
spring.profiles.active: dev
```

### 10.4. Externalising Config

Spring Boot loads config in this priority order (higher = wins):

1. Command-line args (`--server.port=9090`)
2. OS environment variables (`SERVER_PORT=9090`)
3. `application.yml` / `application.properties` in `/config` dir next to JAR
4. `application.yml` / `application.properties` in classpath root
5. `@PropertySource` files
6. `@Value` defaults

---

## 11. Building REST Endpoints

### 11.1. Basic Controller

```java
@RestController // = @Controller + @ResponseBody on all methods
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping                         // GET /api/users
    public List<UserDto> getAll() {
        return userService.findAll();
    }

    @GetMapping("/{id}")                // GET /api/users/123
    public ResponseEntity<UserDto> getById(@PathVariable Long id) {
        return userService.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping                        // POST /api/users
    public ResponseEntity<UserDto> create(@RequestBody @Valid CreateUserRequest request) {
        UserDto created = userService.create(request);
        URI location = URI.create("/api/users/" + created.getId());
        return ResponseEntity.created(location).body(created); // 201 + Location header
    }

    @PutMapping("/{id}")
    public ResponseEntity<UserDto> update(@PathVariable Long id,
                                          @RequestBody @Valid UpdateUserRequest request) {
        return ResponseEntity.ok(userService.update(id, request));
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT) // 204
    public void delete(@PathVariable Long id) {
        userService.delete(id);
    }
}
```

### 11.2. Request Binding Annotations

| Annotation | Binds from | Example |
|---|---|---|
| `@PathVariable` | URL path segment | `GET /users/{id}` |
| `@RequestParam` | Query string | `GET /users?page=1&size=10` |
| `@RequestBody` | Request body (JSON → object) | `POST /users` with JSON body |
| `@RequestHeader` | HTTP header | `Authorization` header |
| `@CookieValue` | Cookie | `session` cookie |

```java
@GetMapping("/search")
public List<UserDto> search(
    @RequestParam(defaultValue = "0") int page,
    @RequestParam(defaultValue = "10") int size,
    @RequestParam(required = false) String name) { ... }
```

### 11.3. `ResponseEntity`

Full control over HTTP response - status code, headers, body:

```java
return ResponseEntity.ok(body);                         // 200
return ResponseEntity.created(location).body(dto);      // 201
return ResponseEntity.noContent().build();              // 204
return ResponseEntity.notFound().build();               // 404
return ResponseEntity.status(HttpStatus.CONFLICT).body(error); // 409

// With custom headers
return ResponseEntity.ok()
    .header("X-Custom-Header", "value")
    .body(dto);
```

### 11.4. CORS

```java
// Per controller or method
@CrossOrigin(origins = "http://localhost:3000")
@RestController
public class UserController { ... }

// Global - in a @Configuration class
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOrigins("http://localhost:3000", "https://myapp.com")
                .allowedMethods("GET", "POST", "PUT", "DELETE")
                .allowedHeaders("*")
                .allowCredentials(true);
    }
}
```

### 11.5. Filters vs Interceptors

| | `OncePerRequestFilter` (Filter) | `HandlerInterceptor` |
|---|---|---|
| Runs at | Servlet level - before Spring MVC | Spring MVC level - after DispatcherServlet |
| Access to Spring beans | yes (if a Spring component) | yes |
| Can abort request | yes (`filterChain.doFilter` not called) | yes (`preHandle` returns false) |
| Sees response body | yes | Only `afterCompletion` (already committed) |
| Best for | Auth, logging, encoding, rate limiting | Logging, auth checking (Spring MVC level), locale |

```java
// Filter
@Component
public class RequestLoggingFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest req,
                                    HttpServletResponse res,
                                    FilterChain chain) throws ServletException, IOException {
        System.out.println("Request: " + req.getMethod() + " " + req.getRequestURI());
        chain.doFilter(req, res); // pass to next filter/servlet
        System.out.println("Response status: " + res.getStatus());
    }
}

// Interceptor - must register in WebMvcConfigurer
@Component
public class AuthInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest req, HttpServletResponse res, Object handler) {
        String token = req.getHeader("Authorization");
        if (token == null) {
            res.setStatus(401);
            return false; // abort
        }
        return true; // continue
    }
}

@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Autowired AuthInterceptor authInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(authInterceptor)
                .addPathPatterns("/api/**")
                .excludePathPatterns("/api/public/**");
    }
}
```

---

## 12. Bean Validation

Add the validation starter to enable `@Valid`/`@Validated` support and the Hibernate Validator constraint annotations.

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

### 12.1. Constraint Annotations

Annotate fields with constraint annotations. Use `@Valid` on nested objects to cascade validation into them.

```java
public class CreateUserRequest {
    @NotNull
    @NotBlank
    @Size(min = 2, max = 50)
    private String name;

    @Email
    private String email;

    @Min(0) @Max(150)
    private int age;

    @Pattern(regexp = "^\\+?[0-9]{8,15}$")
    private String phone;

    @NotNull
    @Future  // date must be in the future
    private LocalDate appointmentDate;

    @Valid   // cascade validation to nested object
    private AddressRequest address;
}
```

### 12.2. Triggering Validation

Place `@Valid` on the `@RequestBody` parameter. Constraint violations automatically produce a 400 response, handled by `MethodArgumentNotValidException`.

```java
// @Valid on controller parameter triggers validation
@PostMapping
public ResponseEntity<UserDto> create(@RequestBody @Valid CreateUserRequest req) { ... }

// Validation errors automatically return 400 Bad Request
// To customise the error response, handle MethodArgumentNotValidException in @ControllerAdvice
```

### 12.3. `@Validated` vs `@Valid`

| | `@Valid` | `@Validated` |
|---|---|---|
| Origin | `javax.validation` / `jakarta.validation` | Spring |
| Supports groups | no | yes |
| Use on | Controller params, nested objects | Class-level (service), groups |

```java
// Validation groups for different operations
public interface OnCreate {}
public interface OnUpdate {}

public class UserRequest {
    @Null(groups = OnCreate.class)    // id must be null on create
    @NotNull(groups = OnUpdate.class) // id must be present on update
    private Long id;
}

@PutMapping("/{id}")
public UserDto update(@RequestBody @Validated(OnUpdate.class) UserRequest req) { ... }
```

---

## 13. Exception Handling

### 13.1. `@ControllerAdvice` + `@ExceptionHandler`

```java
@ControllerAdvice
public class GlobalExceptionHandler {

    // Handle specific exception
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(ResourceNotFoundException ex,
                                                         HttpServletRequest req) {
        ErrorResponse error = new ErrorResponse(
            HttpStatus.NOT_FOUND.value(),
            ex.getMessage(),
            req.getRequestURI()
        );
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }

    // Handle validation failures
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationError(MethodArgumentNotValidException ex) {
        List<String> errors = ex.getBindingResult().getFieldErrors().stream()
            .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
            .collect(Collectors.toList());
        ErrorResponse error = new ErrorResponse(400, "Validation failed", errors);
        return ResponseEntity.badRequest().body(error);
    }

    // Catch-all
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneral(Exception ex) {
        return ResponseEntity.internalServerError()
            .body(new ErrorResponse(500, "Internal server error"));
    }
}
```

### 13.2. RFC 7807 `ProblemDetail` (Spring Boot 3.x)

Spring Boot 3 has built-in support for RFC 7807 Problem Details:

```java
@ExceptionHandler(ResourceNotFoundException.class)
public ProblemDetail handleNotFound(ResourceNotFoundException ex) {
    ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
    pd.setTitle("Resource Not Found");
    pd.setProperty("timestamp", Instant.now());
    return pd;
}
```

```yaml
# Enable automatic ProblemDetail for Spring MVC exceptions
spring:
  mvc:
    problemdetails:
      enabled: true
```

---

## 14. `@Async` and `@Scheduled`

### 14.1. `@Async`

Enable async with `@EnableAsync` on a config class. Annotate methods with `@Async` - they run in a separate thread and return immediately.

```java
@Configuration
@EnableAsync
public class AsyncConfig {
    @Bean
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(10);
        executor.setQueueCapacity(25);
        executor.setThreadNamePrefix("Async-");
        executor.initialize();
        return executor;
    }
}

@Service
public class EmailService {

    @Async
    public void sendEmail(String to, String body) {
        // runs in background thread
        // caller gets control back immediately
    }

    @Async
    public CompletableFuture<String> fetchData() {
        String result = doSlowWork();
        return CompletableFuture.completedFuture(result);
    }
}
```

**Caveat:** Same self-invocation problem as AOP - calling an `@Async` method from within the same bean won't be async (proxy is bypassed).

### 14.2. `@Scheduled`

Enable with `@EnableScheduling` on a config class:

```java
@Configuration
@EnableScheduling
public class SchedulingConfig {}

@Component
public class ReportTask {

    @Scheduled(fixedDelay = 5000)   // 5s after last run finishes
    public void runReport() { ... }

    @Scheduled(fixedRate = 60000)   // every 60s, regardless of duration
    public void syncData() { ... }

    @Scheduled(initialDelay = 10000, fixedRate = 60000) // wait 10s before first run
    public void delayedTask() { ... }

    @Scheduled(cron = "0 0 9 * * MON-FRI") // every weekday at 9am
    public void morningTask() { ... }
    // cron: second minute hour day-of-month month day-of-week
}
```

---

## 15. Spring Data JPA

### 15.1. Entity Mapping

Annotate a class with `@Entity` to map it to a database table. Use JPA annotations to control column names, nullability, relationships, and ID generation strategy.

```java
@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY) // auto-increment
    private Long id;

    @Column(name = "full_name", nullable = false, length = 100)
    private String name;

    @Column(unique = true)
    private String email;

    @Enumerated(EnumType.STRING) // store enum name, not ordinal
    private Role role;

    @CreatedDate  // auto-populated by Spring Data auditing
    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Order> orders = new ArrayList<>();

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "department_id")
    private Department department;
}
```

### 15.2. Relationships

| Annotation | Meaning | Default Fetch |
|---|---|---|
| `@OneToOne` | One-to-one | `EAGER` |
| `@OneToMany` | One entity has many | `LAZY` |
| `@ManyToOne` | Many entities belong to one | `EAGER` |
| `@ManyToMany` | Many-to-many (join table) | `LAZY` |

**Always prefer `LAZY` fetching.** `EAGER` can cause N+1 problems and load unnecessary data.

```java
// @ManyToMany
@Entity
public class Student {
    @ManyToMany
    @JoinTable(name = "student_courses",
               joinColumns = @JoinColumn(name = "student_id"),
               inverseJoinColumns = @JoinColumn(name = "course_id"))
    private Set<Course> courses = new HashSet<>();
}
```

### 15.3. JpaRepository

`JpaRepository` provides CRUD, paging, and sorting out of the box. Spring generates the implementation at startup from method names or `@Query` annotations.

```java
public interface UserRepository extends JpaRepository<User, Long> {
    // JpaRepository provides: save, findById, findAll, deleteById, count, existsById, etc.

    // Derived query methods - Spring generates SQL from method name
    Optional<User> findByEmail(String email);
    List<User> findByNameContainingIgnoreCase(String name);
    List<User> findByAgeGreaterThanAndRoleEquals(int age, Role role);
    boolean existsByEmail(String email);
    long countByRole(Role role);
    List<User> findAllByOrderByNameAsc();
}
```

### 15.4. `@Query`

Use JPQL to reference entity class and field names. For native SQL, set `nativeQuery = true`. Modifying queries require `@Modifying` and `@Transactional`.

```java
// JPQL - uses entity class and field names, not table/column names
@Query("SELECT u FROM User u WHERE u.email = :email AND u.role = :role")
Optional<User> findByEmailAndRole(@Param("email") String email, @Param("role") Role role);

// Native SQL
@Query(value = "SELECT * FROM users WHERE created_at > :since", nativeQuery = true)
List<User> findRecentUsers(@Param("since") LocalDateTime since);

// Modifying query - for UPDATE/DELETE
@Modifying
@Transactional
@Query("UPDATE User u SET u.role = :role WHERE u.id = :id")
int updateRole(@Param("id") Long id, @Param("role") Role role);
```

### 15.5. `@Transactional` - Propagation & Isolation

**Propagation** - how transactions relate to each other when methods call each other:

| Propagation | Behaviour |
|---|---|
| `REQUIRED` (default) | Join existing transaction; create new if none |
| `REQUIRES_NEW` | Always create new transaction; suspend existing |
| `MANDATORY` | Must have existing transaction; throw if none |
| `NEVER` | Must NOT have transaction; throw if one exists |
| `NOT_SUPPORTED` | Suspend existing transaction; run without |
| `SUPPORTS` | Join if exists; run without if none |
| `NESTED` | Nested savepoint within existing transaction |

**Isolation** - how visible other transactions' changes are:

| Isolation | Dirty Read | Non-repeatable Read | Phantom Read |
|---|---|---|---|
| `READ_UNCOMMITTED` | yes | yes | yes |
| `READ_COMMITTED` | no | yes | yes |
| `REPEATABLE_READ` | no | no | yes |
| `SERIALIZABLE` | no | no | no |

```java
@Transactional(
    propagation = Propagation.REQUIRES_NEW,
    isolation = Isolation.READ_COMMITTED,
    rollbackFor = Exception.class,        // default: only RuntimeException
    timeout = 30                          // seconds
)
public void processPayment(Long orderId) {
    // runs in its own new transaction
}

@Transactional(readOnly = true) // optimisation hint for SELECT-only methods
public List<User> findAll() { ... }
```

**Self-invocation caveat:** Calling a `@Transactional` method from within the same bean bypasses the proxy - the transaction annotation is ignored.

---

## 16. Spring Security (Basics)

Adding this dependency immediately secures all endpoints with basic auth. The default user is `user` and the password is printed in the console on startup.

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
```

### 16.1. `SecurityFilterChain`

`SecurityFilterChain` defines the HTTP security rules applied to every request — which paths require authentication, what roles are needed, session policy, and CSRF settings.

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())          // disable for stateless APIs
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .httpBasic(Customizer.withDefaults()); // or .formLogin() or JWT filter

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

### 16.2. Common Annotations

```java
@PreAuthorize("hasRole('ADMIN')")                    // on method
@PreAuthorize("hasAuthority('user:read')")
@PreAuthorize("#id == authentication.principal.id")  // SpEL expression

// Enable method security on config class
@EnableMethodSecurity
```

---

## 17. Startup Hooks

Run initialization logic after the application context is ready by implementing `CommandLineRunner` or `ApplicationRunner`. Both are called with any command-line arguments passed to the app.

```java
// Runs after application context is ready
@Component
public class DataLoader implements CommandLineRunner {
    @Override
    public void run(String... args) throws Exception {
        // seed data, warmup caches, etc.
        System.out.println("Application started with args: " + Arrays.toString(args));
    }
}

// ApplicationRunner - same but receives ApplicationArguments (more structured)
@Component
public class AppRunner implements ApplicationRunner {
    @Override
    public void run(ApplicationArguments args) throws Exception {
        boolean debug = args.containsOption("debug");
        List<String> files = args.getNonOptionArgs();
    }
}
```

---

## 18. Actuator

Add the actuator starter to expose health, metrics, and operational endpoints. Configure which endpoints are exposed via `management.endpoints.web.exposure.include`.

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,env,loggers  # or "*" for all
  endpoint:
    health:
      show-details: always
```

| Endpoint | URL | Description |
|---|---|---|
| Health | `GET /actuator/health` | App health status |
| Info | `GET /actuator/info` | Custom app info |
| Metrics | `GET /actuator/metrics` | JVM, HTTP, custom metrics |
| Env | `GET /actuator/env` | All properties |
| Loggers | `GET/POST /actuator/loggers` | View/change log levels at runtime |
| Beans | `GET /actuator/beans` | All beans in context |
| Mappings | `GET /actuator/mappings` | All `@RequestMapping` routes |

---

## 19. Testing

### 19.1. Test Slice Annotations

| Annotation | Loads | Use for |
|---|---|---|
| `@SpringBootTest` | Full application context | Integration tests |
| `@WebMvcTest(Controller.class)` | Only web layer (controller + MVC) | Controller unit tests |
| `@DataJpaTest` | JPA layer + H2 in-memory DB | Repository tests |
| `@RestClientTest` | `RestTemplate`/`RestClient` components | REST client tests |

### 19.2. `@SpringBootTest`

Loads the full application context. `WebEnvironment.MOCK` (default) uses MockMvc without a real HTTP port. `WebEnvironment.RANDOM_PORT` starts a real embedded server.

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class UserIntegrationTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void createUser_returns201() {
        CreateUserRequest req = new CreateUserRequest("Ryo", "ryo@example.com");
        ResponseEntity<UserDto> res = restTemplate.postForEntity("/api/users", req, UserDto.class);

        assertThat(res.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(res.getBody().getName()).isEqualTo("Ryo");
    }
}
```

### 19.3. `@WebMvcTest` + `MockMvc`

Only loads the web layer. Any Spring beans the controller depends on must be mocked with `@MockBean`.

```java
@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void getUser_returns200() throws Exception {
        UserDto dto = new UserDto(1L, "Ryo", "ryo@example.com");
        given(userService.findById(1L)).willReturn(Optional.of(dto));

        mockMvc.perform(get("/api/users/1")
                    .contentType(MediaType.APPLICATION_JSON))
               .andExpect(status().isOk())
               .andExpect(jsonPath("$.name").value("Ryo"))
               .andExpect(jsonPath("$.email").value("ryo@example.com"));
    }

    @Test
    void createUser_withInvalidBody_returns400() throws Exception {
        CreateUserRequest req = new CreateUserRequest("", "not-an-email"); // invalid

        mockMvc.perform(post("/api/users")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(objectMapper.writeValueAsString(req)))
               .andExpect(status().isBadRequest());
    }

    @Test
    void createUser_returns201() throws Exception {
        CreateUserRequest req = new CreateUserRequest("Ryo", "ryo@example.com");
        UserDto dto = new UserDto(1L, "Ryo", "ryo@example.com");
        given(userService.create(any(CreateUserRequest.class))).willReturn(dto);

        mockMvc.perform(post("/api/users")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(objectMapper.writeValueAsString(req)))
               .andExpect(status().isCreated())
               .andExpect(header().exists("Location"))
               .andExpect(jsonPath("$.id").value(1L));
    }
}
```

### 19.4. `@DataJpaTest`

In-memory H2 database. Only loads JPA-related beans. Transactions roll back after each test by default.

```java
@DataJpaTest
class UserRepositoryTest {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private TestEntityManager entityManager; // helper for setting up test data

    @Test
    void findByEmail_returnsUser() {
        User user = new User("Ryo", "ryo@example.com");
        entityManager.persistAndFlush(user); // persist and flush to DB

        Optional<User> found = userRepository.findByEmail("ryo@example.com");

        assertThat(found).isPresent();
        assertThat(found.get().getName()).isEqualTo("Ryo");
    }

    @Test
    void findByEmail_notFound_returnsEmpty() {
        Optional<User> found = userRepository.findByEmail("none@example.com");
        assertThat(found).isEmpty();
    }
}
```

To use a real database instead of H2:

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE) // use actual DB
@ActiveProfiles("test")
class UserRepositoryTest { ... }
```

### 19.5. Mockito in Depth

Included in `spring-boot-starter-test`.

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private PaymentService paymentService;   // full mock - all methods return default values

    @Mock
    private OrderRepository orderRepository;

    @Spy
    private PricingEngine pricingEngine = new PricingEngine(); // real object, can spy on calls

    @Captor
    private ArgumentCaptor<Order> orderCaptor; // capture args passed to mock

    @InjectMocks
    private OrderService orderService; // creates instance and injects mocks above

    @Test
    void processOrder_callsPaymentWithCorrectAmount() {
        Order order = new Order(100.0);
        given(orderRepository.save(any(Order.class))).willReturn(order); // BDDMockito style
        when(paymentService.charge(anyDouble())).thenReturn(true);       // Mockito style

        orderService.process(order);

        // Verify a method was called
        verify(paymentService).charge(100.0);

        // Verify with argument captor
        verify(orderRepository).save(orderCaptor.capture());
        Order savedOrder = orderCaptor.getValue();
        assertThat(savedOrder.getStatus()).isEqualTo(OrderStatus.PROCESSED);

        // Verify call count
        verify(paymentService, times(1)).charge(anyDouble());
        verify(orderRepository, never()).delete(any());
    }

    @Test
    void processOrder_paymentFails_throwsException() {
        when(paymentService.charge(anyDouble())).thenThrow(new PaymentException("declined"));

        assertThatThrownBy(() -> orderService.process(new Order(50.0)))
            .isInstanceOf(PaymentException.class)
            .hasMessage("declined");
    }

    @Test
    void spyExample() {
        doReturn(99.0).when(pricingEngine).calculate(any()); // override only this method
        // rest of pricingEngine runs real code
    }
}
```

**Key Mockito methods:**

| Method | Purpose |
|---|---|
| `when(mock.method()).thenReturn(value)` | Stub a return value |
| `when(mock.method()).thenThrow(ex)` | Stub an exception |
| `given(mock.method()).willReturn(value)` | BDDMockito style (preferred) |
| `doReturn(val).when(spy).method()` | Stub on spy (avoids calling real method during stubbing) |
| `verify(mock).method(args)` | Assert method was called |
| `verify(mock, times(n)).method(args)` | Assert exact call count |
| `verify(mock, never()).method(args)` | Assert never called |
| `verify(mock, atLeast(n)).method(args)` | Assert called at least n times |
| `ArgumentCaptor.capture()` | Capture argument for assertion |
| `any()`, `anyString()`, `eq(val)` | Argument matchers |
| `ArgumentMatchers.argThat(pred)` | Custom argument matcher |

### 19.6. Testing with Profiles & Properties

Activate a profile or override specific properties for a test class without touching the main configuration.

```java
@SpringBootTest
@ActiveProfiles("test")  // activate application-test.yml
class MyTest { ... }

@SpringBootTest
@TestPropertySource(properties = {"app.feature.enabled=true", "server.port=0"})
class MyTest { ... }
```

### 19.7. AssertJ (Fluent Assertions)

Included via `spring-boot-starter-test`:

```java
// Basic
assertThat(result).isEqualTo(expected);
assertThat(list).hasSize(3).contains("a", "b");
assertThat(optional).isPresent().contains("value");
assertThat(string).startsWith("hello").endsWith("world").contains("ello");
assertThat(number).isGreaterThan(0).isLessThanOrEqualTo(100);

// Collections
assertThat(list).containsExactly("a", "b", "c");          // exact order
assertThat(list).containsExactlyInAnyOrder("c", "a", "b"); // any order
assertThat(list).filteredOn(u -> u.getAge() > 18).hasSize(2);
assertThat(list).extracting(User::getName).containsOnly("Ryo", "Alice");

// Exceptions
assertThatThrownBy(() -> service.doThing())
    .isInstanceOf(IllegalArgumentException.class)
    .hasMessageContaining("invalid");

assertThatNoException().isThrownBy(() -> service.doThing());
```
