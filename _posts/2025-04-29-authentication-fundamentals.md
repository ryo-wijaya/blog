---
layout: post
title: "Authentication Fundamentals Cheatsheet"
description: >-
  Personal cheatsheet for authentication and authorisation. Covers password hashing, JWT, OAuth2 grant types, OpenID Connect, token storage, and implementation examples with Spring Security and FastAPI + authlib.
author: ryo
date: 2025-04-29 02:02:01 +0800
categories: [Software Engineering]
tags: [auth, oauth2, security, cheatsheet]
toc: true
comments: true
pin: false
published: true
---

## 1. Authentication vs Authorization

| | Authentication (AuthN) | Authorization (AuthZ) |
|---|---|---|
| Question | Who are you? | What are you allowed to do? |
| Verified via | Password, token, biometrics | Roles, permissions, scopes |
| Example | Login with email + password | Can this user delete a post? |

**Sessions vs Tokens:**

| | Session-based | Token-based (JWT) |
|---|---|---|
| State stored | Server (session store) | Client (token itself) |
| Scalability | Needs sticky sessions or shared store | Stateless - any server can validate |
| Revocation | Easy (delete session) | Hard (token is self-contained) |
| Best for | Traditional web apps | APIs, SPAs, microservices |

---

## 2. Password Hashing

Never store passwords in plain text or with reversible encryption. Use a slow, salted hashing algorithm.

**Recommended algorithms:** bcrypt, Argon2id, scrypt. MD5 and SHA-* are not suitable - they are too fast.

```java
// Spring Security - BCryptPasswordEncoder
PasswordEncoder encoder = new BCryptPasswordEncoder(12); // cost factor
String hashed = encoder.encode("mypassword");
boolean matches = encoder.matches("mypassword", hashed); // true
```

```python
# Python - passlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("mypassword")
ok = pwd_context.verify("mypassword", hashed)   # True
```

**Key properties of bcrypt/Argon2:**
- Output includes the algorithm, cost factor, and random salt
- Same password produces different hash each time (salted)
- Cost factor increases computation time, making brute-force expensive

---

## 3. JWT (JSON Web Token)

### 3.1. Structure

A JWT is three base64url-encoded parts separated by dots: `header.payload.signature`

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZXhwIjoxNzAwMDAwfQ.abc123sig
```

**Header:**
```json
{"alg": "HS256", "typ": "JWT"}
```

**Payload (claims):**
```json
{
  "sub": "user123",           // subject (user id or username)
  "iat": 1699999000,          // issued at (unix timestamp)
  "exp": 1700000800,          // expiry
  "roles": ["ADMIN", "USER"]  // custom claims
}
```

**Signature:** HMAC-SHA256(base64url(header) + "." + base64url(payload), secret)

The signature guarantees the token has not been tampered with. It does **not** encrypt the payload - the payload is readable by anyone.

### 3.2. Common Algorithms

| Algorithm | Type | Notes |
|---|---|---|
| `HS256` | Symmetric (shared secret) | Simple, but same key signs and verifies - not for public APIs |
| `RS256` | Asymmetric (RSA) | Private key signs, public key verifies - safe to distribute the public key |
| `ES256` | Asymmetric (ECDSA) | Like RS256 but smaller keys and faster |

### 3.3. Claims Reference

| Claim | Name | Meaning |
|---|---|---|
| `iss` | Issuer | Who issued the token |
| `sub` | Subject | Who the token represents |
| `aud` | Audience | Who the token is intended for |
| `exp` | Expiration | Unix timestamp - reject after this |
| `nbf` | Not Before | Unix timestamp - reject before this |
| `iat` | Issued At | When the token was issued |
| `jti` | JWT ID | Unique identifier (useful for revocation) |

### 3.4. Validation Checklist

When validating a received JWT:
1. Verify the signature with the correct key
2. Check `exp` has not passed
3. Check `nbf` is not in the future
4. Check `iss` matches expected issuer
5. Check `aud` includes your service
6. Check the algorithm is what you expect (reject `none`)

---

## 4. OAuth2

OAuth2 is an **authorisation** framework. It lets a user grant a third-party app limited access to their account without sharing credentials.

### 4.1. Roles

| Role | Description |
|---|---|
| **Resource Owner** | The user who owns the data |
| **Resource Server** | The API that holds the data |
| **Authorization Server** | Issues tokens after authenticating the user |
| **Client** | The application requesting access |

### 4.2. Grant Types

| Grant Type | When to Use |
|---|---|
| **Authorization Code + PKCE** | Web apps, SPAs, mobile apps - user-facing login |
| **Client Credentials** | Machine-to-machine, no user involved |
| **Device Code** | Devices without a browser (TV, CLI) |
| **Refresh Token** | Exchange refresh token for new access token |
| ~~Implicit~~ | Deprecated - replaced by Auth Code + PKCE |
| ~~Resource Owner Password~~ | Deprecated - client gets user credentials directly |

### 4.3. Token Types

| Token | Purpose | Lifetime |
|---|---|---|
| **Access Token** | Presented to resource server to access APIs | Short (5-60 min) |
| **Refresh Token** | Used to get a new access token silently | Long (days/weeks) |
| **ID Token** | Contains user identity info (OIDC only) | Short |

---

## 5. OpenID Connect (OIDC)

OIDC is an **authentication** layer built on top of OAuth2. It adds identity (who the user is) to OAuth2's authorisation (what the user can do).

**What OIDC adds:**
- An **ID Token** (JWT) containing user identity claims (`sub`, `email`, `name`, `picture`)
- A `/userinfo` endpoint to fetch additional user claims
- A **discovery document** at `/.well-known/openid-configuration` describing the provider's endpoints

**Standard scopes:**

| Scope | Claims returned |
|---|---|
| `openid` | Required. Enables OIDC, returns `sub` |
| `email` | `email`, `email_verified` |
| `profile` | `name`, `given_name`, `family_name`, `picture` |
| `address` | `address` |
| `phone` | `phone_number` |

---

## 6. OAuth2 Flows in Depth

### 6.1. Authorization Code + PKCE (user-facing apps)

PKCE (Proof Key for Code Exchange) prevents authorization code interception attacks. Required for public clients (SPAs, mobile apps) and recommended for all.

```
1. App generates code_verifier (random string, 43-128 chars)
   and code_challenge = BASE64URL(SHA256(code_verifier))

2. App redirects user to Authorization Server:
   GET /authorize
     ?client_id=my_app
     &response_type=code
     &redirect_uri=https://myapp.com/callback
     &scope=openid email profile
     &state=random_csrf_token
     &code_challenge=abc123...
     &code_challenge_method=S256

3. User authenticates and consents at Authorization Server

4. Authorization Server redirects back to app:
   GET https://myapp.com/callback?code=AUTH_CODE&state=random_csrf_token

5. App verifies state matches, then exchanges code for tokens:
   POST /token
     grant_type=authorization_code
     &code=AUTH_CODE
     &redirect_uri=https://myapp.com/callback
     &client_id=my_app
     &code_verifier=original_verifier    <- proves app that initiated the flow

6. Authorization Server returns:
   {
     "access_token": "...",
     "refresh_token": "...",
     "id_token": "...",
     "expires_in": 3600
   }
```

### 6.2. Client Credentials (machine-to-machine)

No user involved. Used for service-to-service calls.

```
POST /token
  grant_type=client_credentials
  &client_id=service_a
  &client_secret=secret
  &scope=reports:read

Response:
  {
    "access_token": "...",
    "expires_in": 3600,
    "token_type": "Bearer"
  }
```

The client then passes the token as `Authorization: Bearer <token>` on every API call.

---

## 7. Token Storage

Where you store tokens determines your exposure to XSS and CSRF attacks. There is no option that eliminates both risks — the choice is a trade-off.

| Storage | XSS risk | CSRF risk | Notes |
|---|---|---|---|
| `localStorage` / `sessionStorage` | High | None | JavaScript can read it - XSS attack exposes the token |
| `httpOnly` cookie | None | Medium | JS cannot read it. Add `SameSite=Strict` or `Lax` to mitigate CSRF |
| In-memory (JS variable) | Low | None | Lost on page refresh - best for access tokens in SPAs |

**Recommended pattern for SPAs:**
- Store access token in memory (JS variable)
- Store refresh token in `httpOnly`, `Secure`, `SameSite=Strict` cookie
- On page load, use the refresh token cookie to silently get a new access token

---

## 8. Refresh Tokens

When an access token expires, the client can exchange a refresh token for a new one without re-authenticating. The flow below shows the exchange request.

```
1. Access token expires (401 Unauthorized response)

2. Client sends refresh token:
   POST /token
     grant_type=refresh_token
     &refresh_token=REFRESH_TOKEN
     &client_id=my_app

3. Authorization Server returns new access token (and possibly new refresh token)
```

**Refresh token rotation:** Issue a new refresh token with each use and invalidate the old one. If a stolen token is detected (reuse of an already-used token), revoke the entire token family.

**Revocation:** Call the `/revoke` endpoint (RFC 7009) to invalidate a token before expiry.

---

## 9. Spring Security - JWT Implementation

Add Spring Security and JJWT. The implementation involves three components: a `JwtService` for token operations, a `JwtAuthFilter` that validates the token on each request, and a `SecurityConfig` that wires everything together.

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.12.5</version>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-impl</artifactId>
    <version>0.12.5</version>
    <scope>runtime</scope>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-jackson</artifactId>
    <version>0.12.5</version>
    <scope>runtime</scope>
</dependency>
```

```java
// JwtService.java
@Service
public class JwtService {

    @Value("${jwt.secret}")           // base64-encoded key in application.yml
    private String secret;

    private static final long EXPIRY_MS = 1000L * 60 * 30;   // 30 minutes

    public String generateToken(UserDetails user) {
        return Jwts.builder()
            .subject(user.getUsername())
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + EXPIRY_MS))
            .signWith(getKey())
            .compact();
    }

    public String extractUsername(String token) {
        return parseClaims(token).getSubject();
    }

    public boolean isValid(String token, UserDetails user) {
        return extractUsername(token).equals(user.getUsername())
            && !parseClaims(token).getExpiration().before(new Date());
    }

    private Claims parseClaims(String token) {
        return Jwts.parser().verifyWith(getKey()).build()
            .parseSignedClaims(token).getPayload();
    }

    private SecretKey getKey() {
        return Keys.hmacShaKeyFor(Decoders.BASE64.decode(secret));
    }
}
```

```java
// JwtAuthFilter.java
@Component
@RequiredArgsConstructor
public class JwtAuthFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res,
                                    FilterChain chain) throws ServletException, IOException {
        String header = req.getHeader("Authorization");
        if (header == null || !header.startsWith("Bearer ")) {
            chain.doFilter(req, res);
            return;
        }

        String token = header.substring(7);
        String username = jwtService.extractUsername(token);

        if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            UserDetails user = userDetailsService.loadUserByUsername(username);
            if (jwtService.isValid(token, user)) {
                UsernamePasswordAuthenticationToken auth =
                    new UsernamePasswordAuthenticationToken(user, null, user.getAuthorities());
                auth.setDetails(new WebAuthenticationDetailsSource().buildDetails(req));
                SecurityContextHolder.getContext().setAuthentication(auth);
            }
        }
        chain.doFilter(req, res);
    }
}
```

```java
// SecurityConfig.java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthFilter jwtAuthFilter;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/auth/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public AuthenticationManager authManager(AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }
}
```

```java
// AuthController.java
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthenticationManager authManager;
    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;

    @PostMapping("/login")
    public ResponseEntity<Map<String, String>> login(@RequestBody LoginRequest req) {
        authManager.authenticate(
            new UsernamePasswordAuthenticationToken(req.username(), req.password())
        );
        UserDetails user = userDetailsService.loadUserByUsername(req.username());
        String token = jwtService.generateToken(user);
        return ResponseEntity.ok(Map.of("access_token", token, "token_type", "bearer"));
    }
}
```

### 9.1. Spring Security OAuth2 Client (OIDC Login)

For delegating login to an external provider (Google, Okta, Keycloak):

```yaml
# application.yml
spring:
  security:
    oauth2:
      client:
        registration:
          google:
            client-id: ${GOOGLE_CLIENT_ID}
            client-secret: ${GOOGLE_CLIENT_SECRET}
            scope: openid, email, profile
          keycloak:
            client-id: my-app
            client-secret: ${KEYCLOAK_SECRET}
            authorization-grant-type: authorization_code
            scope: openid, email, profile
        provider:
          keycloak:
            issuer-uri: https://keycloak.example.com/realms/myrealm
```

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .authorizeHttpRequests(auth -> auth.anyRequest().authenticated())
        .oauth2Login(oauth2 -> oauth2.defaultSuccessUrl("/dashboard", true));
    return http.build();
}

// Access user info in a controller
@GetMapping("/me")
public Map<String, Object> me(@AuthenticationPrincipal OidcUser oidcUser) {
    return Map.of(
        "subject",  oidcUser.getSubject(),
        "email",    oidcUser.getEmail(),
        "name",     oidcUser.getFullName()
    );
}
```

---

## 10. FastAPI - JWT + OIDC with authlib

### 10.1. JWT Implementation

See the FastAPI Fundamentals cheatsheet for full JWT implementation with `python-jose` and `passlib`. Key pieces:

```python
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "..."   # env var
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
pwd_context = CryptContext(schemes=["bcrypt"])

def create_access_token(subject: str, expires_delta: timedelta = timedelta(minutes=30)):
    expire = datetime.now(timezone.utc) + expires_delta
    return jwt.encode({"sub": subject, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 10.2. OIDC / OAuth2 with authlib

Use `authlib`'s Starlette integration for OIDC login flows. `SessionMiddleware` is required to persist the OAuth state and nonce between the redirect and callback requests.

```bash
pip install authlib httpx itsdangerous
```

```python
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from fastapi.responses import RedirectResponse

# SessionMiddleware is required - stores state/nonce in session
app.add_middleware(SessionMiddleware, secret_key="session-secret")

config = Config(".env")   # reads GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET from .env
oauth = OAuth(config)

oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")    # OIDC userinfo from ID token
    # user_info contains: sub, email, name, picture, email_verified
    return {
        "email": user_info["email"],
        "name": user_info["name"],
    }

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")
```

For multiple providers, register each:

```python
oauth.register(name="github", ...)
oauth.register(name="microsoft", ...)
```

---

## 11. Common Mistakes & Attacks

### 11.1. JWT Pitfalls

| Mistake | Risk | Fix |
|---|---|---|
| Accepting `alg: none` | Token bypass - no signature needed | Always specify accepted algorithms: `algorithms=["HS256"]` |
| Algorithm confusion (`RS256` vs `HS256`) | Attacker signs with public key as HMAC secret | Pin the algorithm on the server, never trust header's `alg` |
| Long expiry on access tokens | Long window for stolen token | Keep access tokens short-lived (15-60 min) |
| Storing JWT in `localStorage` | XSS exposes token | Use `httpOnly` cookie or in-memory |
| No audience (`aud`) validation | Token issued for service A accepted by service B | Validate `aud` claim on the resource server |
| Sensitive data in payload | Payload is readable by anyone | JWT is signed, not encrypted - never put passwords or PII in claims |

### 11.2. OAuth2 Attack Surface

| Attack | Description | Mitigation |
|---|---|---|
| **CSRF on redirect** | Attacker tricks user into completing auth flow | Validate `state` parameter matches what was sent |
| **Authorization code interception** | Attacker intercepts code in redirect | Use PKCE |
| **Open redirect** | Redirect to attacker-controlled URI | Whitelist exact redirect URIs at the Authorization Server |
| **Token leakage via Referer** | Access token in URL gets leaked in Referer headers | Never put tokens in URL query params |
| **SSRF via issuer URL** | Attacker controls `iss` to point to their server | Pin the expected issuer, do not fetch OIDC discovery dynamically from untrusted input |

### 11.3. General Best Practices

- Use HTTPS everywhere - tokens in transit over HTTP can be stolen.
- Rotate secrets/keys regularly.
- Implement token revocation (refresh token rotation + blacklist for `jti`).
- Use short-lived access tokens + refresh token rotation.
- Log authentication events (logins, failed attempts, token refreshes).
- Rate limit login and token endpoints.
- Validate all redirect URIs strictly - prefer exact matching over prefix matching.
