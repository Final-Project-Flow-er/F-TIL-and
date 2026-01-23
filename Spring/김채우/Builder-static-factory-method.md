# Builder와 정적 팩토리 메소드

---

> Builder만 사용했을 때의 부족한 부분을 정적 팩토리 메소드로 보완

---
# 1. Builder만 사용할 때
## 1.1. 나쁜 예시
```java
@Entity
@Getter
@Builder
public class Order {
    private Long orderId;
    private Long userId;
    private OrderStatus status;
    private LocalDateTime orderedAt;
}

// 사용하는 곳 (가독성 낮음)
Order order = Order.builder()
    .userId(1L)
    .status(OrderStatus.PENDING)
    .orderedAt(LocalDateTime.now())
    .build();  // ❌ 이게 신규 주문인지, 재주문인지, 취소인지 알 수 없음!
```
### 1.1.1. 문제점
생성 의도가 불명확
비즈니스 로직의 외부 유출
필수값 검증 불가능
## 1.2. 해결
정적 팩토리 메소드 + 빌더 조합
### 1.2.1. 좋은 예시
```java
@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)  // JPA용
public class Order {
    
    @Id @GeneratedValue
    private Long orderId;
    
    private Long userId;
    private Long storeId;
    
    @Enumerated(EnumType.STRING)
    private OrderStatus status;
    
    private LocalDateTime orderedAt;
    private LocalDateTime completedAt;
    
    @Builder(access = AccessLevel.PRIVATE)  // ⭐ private으로 숨김!
    private Order(Long userId, Long storeId, OrderStatus status, 
                  LocalDateTime orderedAt) {
        this.userId = userId;
        this.storeId = storeId;
        this.status = status;
        this.orderedAt = orderedAt;
    }
    
    // ✅ 정적 팩토리 메서드 1: 신규 주문 생성
    public static Order createNewOrder(Long userId, Long storeId) {
        validateUserId(userId);
        validateStoreId(storeId);
        
        return Order.builder()
            .userId(userId)
            .storeId(storeId)
            .status(OrderStatus.PENDING)
            .orderedAt(LocalDateTime.now())
            .build();
    }
    
    // ✅ 정적 팩토리 메서드 2: 재주문
    public static Order createReorder(Order originalOrder) {
        return Order.builder()
            .userId(originalOrder.getUserId())
            .storeId(originalOrder.getStoreId())
            .status(OrderStatus.PENDING)
            .orderedAt(LocalDateTime.now())
            .build();
    }
    
    // ✅ 정적 팩토리 메서드 3: 테스트용 주문
    public static Order createForTest(Long userId, OrderStatus status) {
        return Order.builder()
            .userId(userId)
            .storeId(999L)  // 테스트 매장
            .status(status)
            .orderedAt(LocalDateTime.now())
            .build();
    }
    
    private static void validateUserId(Long userId) {
        if (userId == null || userId <= 0) {
            throw new IllegalArgumentException("유효하지 않은 사용자 ID입니다.");
        }
    }
    
    private static void validateStoreId(Long storeId) {
        if (storeId == null || storeId <= 0) {
            throw new IllegalArgumentException("유효하지 않은 매장 ID입니다.");
        }
    }
}
```

---
# 2. 정적 팩토리 메소드의 장점
## 2.1. 이름을 가짐
```java
// ❌ 생성자: 의미 불명확
new Order(userId, storeId, OrderStatus.PENDING, LocalDateTime.now());

// ✅ 정적 팩토리: 의미 명확
Order.createNewOrder(userId, storeId);
Order.createReorder(originalOrder);
Order.createForTest(userId, OrderStatus.COMPLETED);
```
## 2.2. 객체 생성의 캡슐화: 유효성 검증
```java
public static Order createNewOrder(Long userId, Long storeId) {
    // 비즈니스 규칙을 여기서 통제!
    validateUserId(userId);
    validateStoreId(storeId);
    
    if (isStoreOpen(storeId)) {  // 매장 영업시간 체크
        return Order.builder()
            .userId(userId)
            .storeId(storeId)
            .status(OrderStatus.PENDING)
            .orderedAt(LocalDateTime.now())
            .build();
    } else {
        throw new StoreClosedException("영업시간이 아닙니다.");
    }
}
```
## 2.3. 호출 시마다 새 객체를 만들지 않아도 됨
```java
public class OrderStatus {
    
    // ⭐ 싱글톤 패턴처럼 캐싱 가능
    private static final Order EMPTY_ORDER = Order.builder()
        .userId(0L)
        .storeId(0L)
        .status(OrderStatus.EMPTY)
        .orderedAt(LocalDateTime.now())
        .build();
    
    public static Order empty() {
        return EMPTY_ORDER;  // 항상 같은 객체 반환
    }
}
```
## 2.4. 하위 타입 객체 반환 가능
```java
public abstract class Payment {
    
    // ⭐ 결제 방법에 따라 다른 구현체 반환
    public static Payment from(PaymentType type, int amount) {
        return switch (type) {
            case CARD -> new CardPayment(amount);
            case CASH -> new CashPayment(amount);
            case POINT -> new PointPayment(amount);
        };
    }
}
```
## 2.5. 매개변수에 따라 다른 객체 반환
```java
public static Order createByAmount(Long userId, int totalAmount) {
    if (totalAmount >= 50000) {
        // 5만원 이상: VIP 주문
        return Order.createVipOrder(userId);
    } else {
        // 일반 주문
        return Order.createNewOrder(userId, storeId);
    }
}
```

---
# 3. 정적 팩토리 메소드 네이밍 컨벤션

| 메서드 이름          | 의미                | 예시                                      |
| --------------- | ----------------- | --------------------------------------- |
| **from**        | 하나의 매개변수를 받아 변환   | `Order.from(orderDto)`                  |
| **of**          | 여러 매개변수를 받아 생성    | `Order.of(userId, storeId)`             |
| **create**      | 새로운 객체 생성 (명시적)   | `Order.createNewOrder(userId, storeId)` |
| **valueOf**     | from/of의 더 자세한 버전 | `OrderStatus.valueOf("PENDING")`        |
| **getInstance** | 싱글톤 (같은 인스턴스 반환)  | `Settings.getInstance()`                |
| **newInstance** | 항상 새 인스턴스 반환      | `Order.newInstance()`                   |

---
# 4. 빌더 vs 정적 팩토리 선택 기준
| 상황                 | 추천             | 이유          |
| ------------------ | -------------- | ----------- |
| 필수값만 있고 단순함 (1-3개) | 정적 팩토리만        | 간결함         |
| 선택적 필드가 많음 (4개 이상) | 정적 팩토리 + 빌더 조합 | 가독성 + 의미 전달 |
| 생성 로직이 복잡함         | 정적 팩토리 + 빌더    | 캡슐화​        |
| 불변 객체 필요           | 빌더 (Setter 없이) | 안정성​        |


---
# 내가 생각한 한 줄 정의
> 가독성 좋고 비즈니스 로직을 숨기기 위해 사용


