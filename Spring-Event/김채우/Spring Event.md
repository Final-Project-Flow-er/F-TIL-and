# Spring Event

---

> 애플리케이션 내부 이벤트 발행/구독 매커니즘으로 같은 프로세스 내 컴포넌트 간 느슨한 결합 구현에 도움

---
# 1. 개념
Observer 패턴을 구현한 것
발행: 특정 상황이 발생했을 때 이를 알림
구독: 관심 있는 컴포넌트들이 자동으로 반응
Publisher(이벤트 발행) -> ApplicationEventPublisher(전파) -> Listeners(자동 호출)
## 1.1. 기본 사용법
### 1.1.1. 이벤트 클래스 정의
```java
// 일반 Java 클래스로 정의 (Spring 4.2 이후)
public class OrderCreatedEvent {
    private final Long orderId;
    private final String productName;
    private final int quantity;
    
    public OrderCreatedEvent(Long orderId, String productName, int quantity) {
        this.orderId = orderId;
        this.productName = productName;
        this.quantity = quantity;
    }
    
    // getters
}

// 또는 Record 사용 (간결함)
public record OrderCreatedEvent(Long orderId, String productName, int quantity) {}
```
### 1.1.2. 이벤트 발행 Publisher
```java
@Service
@RequiredArgsConstructor
public class OrderService {
    
    private final OrderRepository orderRepository;
    private final ApplicationEventPublisher eventPublisher;
    
    @Transactional
    public Order createOrder(OrderRequest request) {
        // 1. 비즈니스 로직 수행
        Order order = orderRepository.save(new Order(request));
        
        // 2. 이벤트 발행
        eventPublisher.publishEvent(
            new OrderCreatedEvent(
                order.getId(), 
                order.getProductName(), 
                order.getQuantity()
            )
        );
        
        return order;
    }
}
```
### 1.1.3. 이벤트 구독
```java
// 방법 1: @EventListener 어노테이션
@Component
public class InventoryEventListener {
    
    private final InventoryService inventoryService;
    
    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        inventoryService.decreaseStock(event.productName(), event.quantity());
        System.out.println("재고 차감 완료: " + event.orderId());
    }
}

// 방법 2: ApplicationListener 인터페이스
@Component
public class NotificationListener implements ApplicationListener<OrderCreatedEvent> {
    
    @Override
    public void onApplicationEvent(OrderCreatedEvent event) {
        sendNotification("주문 생성됨: " + event.orderId());
    }
}
```
## 1.2. 활용
### 1.2.1. 트랜잭션 이벤트 리스너
```java
@Component
public class EmailEventListener {
    
    // 트랜잭션 커밋 후에만 실행
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void sendEmail(OrderCreatedEvent event) {
        emailService.sendOrderConfirmation(event.orderId());
    }
    
    // 트랜잭션 롤백 시 실행
    @TransactionalEventListener(phase = TransactionPhase.AFTER_ROLLBACK)
    public void handleFailure(OrderCreatedEvent event) {
        log.error("주문 생성 실패: " + event.orderId());
    }
}
```
옵션
- `BEFORE_COMMIT`: 트랜잭션 커밋 직전
- `AFTER_COMMIT`: 트랜잭션 커밋 후(기본값)
- `AFTER_ROLLBACK`: 트랜잭션 롤백 후
- `AFTER_COMPLETION`: 트랜잭션 완료 후(커밋/롤백 관계 없이)
### 1.2.2. 비동기 이벤트 처리
```java
@Configuration
@EnableAsync
public class AsyncConfig {
    
    @Bean
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(10);
        executor.setQueueCapacity(100);
        executor.initialize();
        return executor;
    }
}

@Component
public class AsyncEventListener {
    
    @Async
    @EventListener
    public void handleOrderCreatedAsync(OrderCreatedEvent event) {
        // 별도 스레드에서 실행
        sendSlackNotification(event);
    }
}
```
### 1.2.3. 조건부 이벤트 리스너
```java
@Component
public class ConditionalListener {
    
    // 특정 조건일 때만 실행
    @EventListener(condition = "#event.quantity > 100")
    public void handleBulkOrder(OrderCreatedEvent event) {
        log.info("대량 주문 감지: " + event.quantity());
    }
}
```
### 1.2.4. 이벤트 순서 제어
```java
@Component
public class OrderedListener {
    
    @Order(1)
    @EventListener
    public void firstListener(OrderCreatedEvent event) {
        System.out.println("1번째 실행");
    }
    
    @Order(2)
    @EventListener
    public void secondListener(OrderCreatedEvent event) {
        System.out.println("2번째 실행");
    }
}
```

---
# 2. Spring Event 특징
## 2.1. 장점
1. 느슨한 결합: 발행자는 구독자를 알 필요가 없음
2. 간단한 구현: 별도 인프라 없이 어노테이션만으로 사용 가능
3. 트랜잭션 통합: `@TransactionalEventListener`로 트랜잭션과 연동
4. 유연한 확장: 새로운 리스너 추가 시 기존 코드 수정 불필요
5. 동기/비동기 선택: `@Async`로 간단히 비동기 처리 가능
## 2.2. 단점
1. 같은 프로세스 제한: ApplicationContext 내에서만 작동
2. 분산 환경 미지원: 여러 서버 간 이벤트 전파 불가
3. 메시지 영속성 없음: 서버 재시작 시 이벤트 손실
4. 순서 보장 제한: 비동기 처리 시 실행 순서 보장 어려움
5. 디버깅 어려움: 이벤트 흐름 추적이 직접 호출보다 복잡

---
# 내가 생각한 한 줄 정의
> 서비스 간 의존도를 낮춰주는 Spring Framework의 기능 중 하나
