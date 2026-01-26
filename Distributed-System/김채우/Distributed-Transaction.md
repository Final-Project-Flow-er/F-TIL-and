# Distribute Transaction

---

> 모듈 간 통신을 할 HTTP 요청이 별동의 트랜잭션으로 처리되어 하나의 원자적 트랜잭션으로 묶을 수 없는 것

---
# 1. 문제 상황
```java
@Service
@Transactional
public class OrderService {
    
    private final OrderRepository orderRepository;
    private final ProductClient productClient;  // Feign Client
    private final InventoryClient inventoryClient;  // Feign Client
    
    public OrderResponse createOrder(OrderRequest request) {
        // 1. 주문 생성 (order-service DB에 저장)
        Order order = orderRepository.save(new Order(request));
        
        // 2. 재고 차감 (inventory-service HTTP 호출)
        inventoryClient.decreaseStock(request.getProductId(), request.getQuantity());
        
        // 3. 포인트 차감 (member-service HTTP 호출)
        memberClient.deductPoints(request.getMemberId(), order.getTotalAmount());
        
        return OrderResponse.from(order);
    }
}
```
## 1.1. 트랜잭션 분리 문제
Order 저장은 성공했는데 재고 차감이 실패할 경우 -> DB에 주문은 남고 재고는 그대로
재고 차감은 성공했는데 포인트 차감이 실패할 경우 -> 재고는 줄었지만 주문은 미완료
`Transactional`은 같은 데이터베이스 내의 로컬 트랜잭션만 관리
- HTTP로 다른 서비스를 호출하면 각자 독립적인 트랜잭션으로 실행

---
# 2. 해결 방법
## 2.1. Saga 패턴
### 2.1.1. Orchestration SAGA(Try-Catch)
중앙 조정자가 전체 흐름을 직접 제어
```java
@Service
public class OrderOrchestrator {  // 중앙 조정자
    
    private final ProductClient productClient;
    private final InventoryClient inventoryClient;
    private final PaymentClient paymentClient;
    
    public OrderResponse createOrder(OrderRequest request) {
        boolean inventoryReserved = false;
        boolean paymentProcessed = false;
        
        try {
            // 조정자가 직접 각 서비스에 명령
            productClient.validateProduct(request.getProductId());
            
            inventoryClient.reserveStock(request.getProductId());
            inventoryReserved = true;
            
            paymentClient.processPayment(request.getAmount());
            paymentProcessed = true;
            
            return OrderResponse.success();
            
        } catch (Exception e) {
            // 조정자가 보상 트랜잭션 실행
            if (paymentProcessed) {
                paymentClient.refund(request.getAmount());
            }
            if (inventoryReserved) {
                inventoryClient.releaseStock(request.getProductId());
            }
            throw new OrderFailedException();
        }
    }
}
```
특징
- 중앙에서 전체 흐름을 명확히 파악 가능
- 동기식 호출(Feign Client로 직접 호출)
- 상태 추적이 쉬움
- 구현이 간단하지만 중앙 조정자에 복잡성 집중
### 2.1.2. Choreography SAGA
Spring Event 방식
각 서비스가 이벤트를 발행하고 다른 서비스가 이를 구독해 순차적으로 처리
```java
@Service
public class OrderService {
    
    private final ApplicationEventPublisher eventPublisher;
    
    @Transactional
    public OrderResponse createOrder(OrderRequest request) {
        // 1. 주문을 PENDING 상태로 저장
        Order order = orderRepository.save(
            Order.create(request, OrderStatus.PENDING)
        );
        
        // 2. 이벤트 발행
        eventPublisher.publishEvent(
            new OrderCreatedEvent(order.getId(), request)
        );
        
        return OrderResponse.from(order);
    }
}

// Inventory Service
@Component
public class InventoryEventListener {
    
    @EventListener
    @Transactional
    public void handleOrderCreated(OrderCreatedEvent event) {
        try {
            // 재고 차감
            inventoryService.decreaseStock(event.getProductId(), event.getQuantity());
            
            // 다음 단계 이벤트 발행
            eventPublisher.publishEvent(
                new InventoryDecreasedEvent(event.getOrderId())
            );
        } catch (Exception e) {
            // 실패 시 보상 이벤트 발행
            eventPublisher.publishEvent(
                new InventoryDecreaseFailed(event.getOrderId())
            );
        }
    }
}
```
특징
- 중앙 조정자가 없고 각 서비스가 이벤트로 소통
- 비동기식 (메시지 큐, Spring Event)
- 서비스 간 느슨한 결합
- 확장이 쉽지만 전체 흐름 파악이 어려움
### 2.1.3. 두 방식 비교
| 구분         | Orchestration (Try-Catch) | Choreography (Spring Event) |
| ---------- | ------------------------- | --------------------------- |
| **제어 방식**  | 중앙 조정자가 명령​               | 이벤트 구독/발행으로 자율 동작 ​         |
| **통신 방식**  | 동기식 (Feign Client)​       | 비동기식 (Event, 메시지 큐)         |
| **결합도**    | 조정자와 강한 결합​               | 서비스 간 느슨한 결합 ​              |
| **상태 추적**  | 쉬움 (조정자가 관리)​             | 어려움 (이벤트 로그 추적 필요)​         |
| **구현 난이도** | 쉬움​                       | 어려움 (이벤트 의존성 복잡)​           |
| **확장성**    | 조정자가 병목 가능​               | 서비스 추가 시 확장 용이 ​            |
## 2.2. 보상 트랜잭션(Compensating Transaction)
실패 시 이미 완료된 작업을 되돌리는 역작업 수행
```java
@Service
public class OrderService {
    
    public OrderResponse createOrder(OrderRequest request) {
        Order order = null;
        boolean inventoryDecreased = false;
        boolean pointsDeducted = false;
        
        try {
            // 1. 주문 생성
            order = orderRepository.save(new Order(request));
            
            // 2. 재고 차감
            inventoryClient.decreaseStock(request.getProductId(), request.getQuantity());
            inventoryDecreased = true;
            
            // 3. 포인트 차감
            memberClient.deductPoints(request.getMemberId(), order.getTotalAmount());
            pointsDeducted = true;
            
            // 4. 주문 상태를 COMPLETED로 변경
            order.complete();
            orderRepository.save(order);
            
            return OrderResponse.from(order);
            
        } catch (Exception e) {
            // 보상 트랜잭션 실행 (역순으로)
            if (pointsDeducted) {
                memberClient.refundPoints(request.getMemberId(), order.getTotalAmount());
            }
            if (inventoryDecreased) {
                inventoryClient.increaseStock(request.getProductId(), request.getQuantity());
            }
            if (order != null) {
                order.cancel();
                orderRepository.save(order);
            }
            
            throw new OrderCreationFailedException("주문 생성 중 오류 발생", e);
        }
    }
}
```
### 2.2.1. 보상 트랜잭션에 필요한 API
각 Feign Client에 복구용 API가 필요
```java
@FeignClient(name = "inventory-service")
public interface InventoryClient {
    
    @PostMapping("/internal/inventory/decrease")
    void decreaseStock(@RequestParam Long productId, @RequestParam int quantity);
    
    // 보상 트랜잭션용 API
    @PostMapping("/internal/inventory/increase")
    void increaseStock(@RequestParam Long productId, @RequestParam int quantity);
}
```
## 2.3. Outbox 패턴
데이터 변경과 이벤트 발행을 동일 트랜잭션에 묶어 최종 일관성 보장
```java
@Service
@Transactional
public class OrderService {
    
    private final OrderRepository orderRepository;
    private final OutboxRepository outboxRepository;
    
    public OrderResponse createOrder(OrderRequest request) {
        // 1. 주문 저장
        Order order = orderRepository.save(new Order(request));
        
        // 2. Outbox에 이벤트 저장 (같은 트랜잭션)
        outboxRepository.save(
            new OutboxEvent("OrderCreated", order.getId(), request)
        );
        
        // 3. 별도 스케줄러가 Outbox를 폴링하여 이벤트 발행
        
        return OrderResponse.from(order);
    }
}
```

---
# 3. Spring Event -> MSA 전환
MSA로 분리 시 ApplicationContext 또한 분리되기 때문에 Feign Client를 사용하고 있다면 코드를 바꿔줘야 함
하지만 이후 Spring Event에서 메시지 큐로 전환하는 것은 간단하고 이벤트 기반 설계 자체는 그대로 유지
## 3.1. 전환 1단계: 현재
```java
// Order Service
@Service
public class OrderService {
    private final ApplicationEventPublisher eventPublisher;
    
    public void createOrder(OrderRequest request) {
        Order order = orderRepository.save(new Order(request));
        
        // Spring Event 발행
        eventPublisher.publishEvent(
            new OrderCreatedEvent(order.getId(), request)
        );
    }
}

// Inventory Service
@Component
public class InventoryEventListener {
    
    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        inventoryService.reserveStock(event.getProductId());
    }
}
```
## 3.2. 전환 2단계: MSA로 전환 후(Kafka 사용)
이벤트 발행/구독 코드만 변경
```java
// Order Service (Producer)
@Service
public class OrderService {
    private final KafkaTemplate<String, OrderCreatedEvent> kafkaTemplate;
    
    public void createOrder(OrderRequest request) {
        Order order = orderRepository.save(new Order(request));
        
        // Kafka로 이벤트 발행 (Spring Event 대신)
        kafkaTemplate.send("order-created-topic", 
            new OrderCreatedEvent(order.getId(), request)
        );
    }
}

// Inventory Service (Consumer)
@Component
public class InventoryKafkaListener {
    
    @KafkaListener(topics = "order-created-topic")
    public void handleOrderCreated(OrderCreatedEvent event) {
        // 동일한 비즈니스 로직
        inventoryService.reserveStock(event.getProductId());
    }
}
```
## 3.3. 변경되는 것 vs 유지되는 것
| 항목          | Spring Event                    | Kafka/RabbitMQ          |
| ----------- | ------------------------------- | ----------------------- |
| **이벤트 클래스** | 그대로 유지​                         | 그대로 유지                  |
| **비즈니스 로직** | 그대로 유지​                         | 그대로 유지                  |
| **발행 방식**   | `eventPublisher.publishEvent()` | `kafkaTemplate.send()`​ |
| **구독 방식**   | `@EventListener`                | `@KafkaListener`​       |
| **통신 범위**   | 같은 프로세스 내                       | 네트워크를 통한 분산 통신​         |
## 3.4. 점진적 전환
### 3.4.1. 1단계: 모놀리 + Spring Event
모듈 간 이벤트 설계로 느슨한 결합 구현
이벤트 중심 사고방식에 익숙해지기
### 3.4.2. 모놀리 + Kafka(하이브리드)
외부로 분리할 준비가 된 이벤트만 Kafka 사용
Spring Event를 받아 Kafka로 전달
### 3.4.3. 완전한 MSA + Kafka
각 서비스를 독립된 애플리케이션으로 분리
Spring Event 제거, 모든 통신을 Kafka로 전환

---
# 내가 생각한 한 줄 정의
>각기 다른 HTTP 요청에 대한 작업 하나로 묶어주기
