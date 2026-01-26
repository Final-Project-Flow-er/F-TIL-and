## Spring Security란?
스프링 기반의 어플리케이션 보안(인증, 인가 등)을 담당하는 스프링 하위 프레임워크

## 인증과 인가
- **인증**: 보호된 리소스에 접근하는 사용자를 식별하는 과정으로 사용자를 증명하는 것
- **인가**: 인증된 사용자가 시스템 자원에 대한 접근 시 권한이 있는지 확인하는 과정 (권한 부여)

## 인증 방식
- **Session**: 서버 메모리(또는 Redis 등)에 사용자 인증 정보를 저장하고, 클라이언트는 세션 ID를 쿠키로 보관하여 요청마다 서버에 전달하는 방식
- **Token**: 서버가 발급한 인증 수단으로, 클라이언트가 이를 저장하고 요청 시 서버에 함께 보내 인증을 수행하는 방식 (JWT는 Token 방식의 대표적인 구현)

## JWT란?
인증 서버에서 토큰을 발급하고 이 토큰을 클라이언트-서버 통신에서 API 보안을 위해 사용

## Spring Security의 핵심 구조
<img width="1037" height="665" alt="image" src="https://github.com/user-attachments/assets/fee622bd-7bd0-4496-ae11-c00bc50daed6" />

`요청 → Security Filter Chain → DispatcherServlet → Controller`  
- Spring Security는 서블릿 필터 기반
- 모든 요청은 Controller 전에 필터를 먼저 통과

## Spring Security + JWT 인증 흐름
1. **Request**: 사용자가 POST /login으로 ID/PW 전송
2. **Authentication Filter**: 로그인 요청을 가로채 ID/PW로 Authentication 객체 생성
3. **AuthenticationManager**: 등록된 AuthenticationProvider에게 인증 위임
4. **UserDetailsService**: DB에서 사용자 정보를 조회하여 UserDetails 반환
5. **AuthenticationProvider**: PasswordEncoder로 비밀번호 검증
6. **Successful Authentication**: 인증된 Authentication 객체가 필터로 반환되고 successfulAuthentication() 실행
7. **JWTUtil**: 인증 정보를 기반으로 JWT 토큰 생성
8. **Response**: JWT를 Authorization 헤더에 담아 응답

[로그인 이후 요청]   
1. **JWT 인증 필터**: 요청의 JWT를 검증하고 Authentication 생성
2. **SecurityContextHolder**: 인증 정보를 저장
3. **Controller**: 인증된 사용자로 API 접근
