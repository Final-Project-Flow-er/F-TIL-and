# Transaction Isolation 

---

> 트랜잭션 격리 수준

---
# 1. 격리성은 완벽하게 지켜질 수 있는가?
완벽해질 수 없음
완벽한 격리를 위해서는 모든 트랜잭션을 순차적으로 실행해야 하기 때문
이러면 동시성이 0이 되어버림
따라서 **성능과 데이터 정합성 사이의 트레이드오프**를 선택하는 것이 격리 수준

---
# 2. 종류
## 2.1. READ UNCOMMITTED
커밋되지 않은 읽기
### 2.1.1. 동작 원리
다른 트랜잭션의 변경 사항을 커밋 없이도 바로 읽을 수 있음
```java
-- 트랜잭션 A
START TRANSACTION;
UPDATE product SET stock = 90 WHERE id = 1;
-- 아직 커밋 안 함!

-- 트랜잭션 B (동시 실행)
START TRANSACTION;
SELECT stock FROM product WHERE id = 1;
-- 결과: 90 (커밋 안 된 데이터를 읽음!)
```
거의 사용되지 않음
데이터 정합성이 완전히 무시되기 때문에 임시 집계나 로깅에서만 사용
## 2.2. READ COMMITED
커밋된 읽기
### 2.2.1. 동작 원리
커밋된 데이터만 읽을 수 있음
```java
-- 트랜잭션 A
START TRANSACTION;
UPDATE product SET stock = 90 WHERE id = 1;  -- Undo Log에 100 저장
-- 아직 커밋 안 함

-- 트랜잭션 B
START TRANSACTION;
SELECT stock FROM product WHERE id = 1;
-- 결과: 100 (Undo Log에서 읽음!)

-- 트랜잭션 A
COMMIT;  -- 이제 90이 확정됨

-- 트랜잭션 B
SELECT stock FROM product WHERE id = 1;
-- 결과: 90 (커밋됐으니 최신값 읽음)
```
### 2.2.2. 문제점
**Non-Repeatable Read** 발생
```java
@Transactional(isolation = Isolation.READ_COMMITTED)
public void processOrder(Long productId) {
    // 1차 조회: 재고 100개
    Product product1 = productRepository.findById(productId);
    int stock1 = product1.getStock();  // 100
    
    // 다른 트랜잭션이 재고를 90으로 변경하고 COMMIT
    
    // 2차 조회: 재고 90개
    Product product2 = productRepository.findById(productId);
    int stock2 = product2.getStock();  // 90
    
    // ❌ 같은 트랜잭션 내에서 값이 바뀜!
    assert stock1 == stock2;  // 실패!
}
```
### 2.2.3. 실무 사용
Oracle, PostgreSQL의 기본값
웹 서비스의 대부분의 케이스에 적합
## 2.3. REPEATABLE READ
반복 가능한 읽기
### 2.3.1. 동작 원리
트랜잭션이 시작된 시점의 스냅샷 읽음
MySQL InnoDB의 기본값
MySQL의 핵심: MVCC (Multi-Version Concurrency Control)
- 락 없이 동시성을 제어하는 메커니즘
- 데이터를 수정할 때 기존 데이터를 덮어쓰지 않고 새 버전 생성
- 여러 트랜잭션이 동시에 서로 다른 버전을 읽을 수 있음 
- 읽기는 락 없이 진행하고 쓰기도 블로킹 없이 진행되기 때문에 동시성 극대화 
- 핵심 요소
	- Undo Log(백업 저장소)
		- 데이터 변경 전 "이전 버전"을 저장하는 곳
	- 트랜잭션 ID
		- 각 트랜잭션에게 부여하는 고유 번호
	- Read View(스냅샷)
		- 내가 읽을 수 있는 데이터 버전의 기준
```java
-- 트랜잭션 A (ID: 10)
START TRANSACTION;
SELECT stock FROM product WHERE id = 1;  -- 100
-- ⭐ 이 시점의 스냅샷 고정! (trx_id=10 기준)

-- 트랜잭션 B (ID: 11)
START TRANSACTION;
UPDATE product SET stock = 90 WHERE id = 1;
COMMIT;

-- 트랜잭션 C (ID: 12)
START TRANSACTION;
UPDATE product SET stock = 80 WHERE id = 1;
COMMIT;

-- 트랜잭션 A
SELECT stock FROM product WHERE id = 1;  
-- 결과: 100 (여전히 처음 읽은 값!)
-- ⭐ Undo Log에서 trx_id=10 시점 데이터를 읽음
```
### 2.3.2. 문제점
**Phantom Read** 발생
```java
-- 트랜잭션 A
START TRANSACTION;
SELECT COUNT(*) FROM orders WHERE user_id = 1;  -- 10건

-- 트랜잭션 B
START TRANSACTION;
INSERT INTO orders (user_id, ...) VALUES (1, ...);
COMMIT;

-- 트랜잭션 A
SELECT COUNT(*) FROM orders WHERE user_id = 1;  -- 11건! (팬텀)
```
발생 이유
- REPEATABLE READ는 행의 값의 변경은 막지만 새로운 행 추가는 막지 않음
MySQL InnoDB의 특수 케이스
- InnoDB는 Gap Lock으로 Phantom Read를 대부분 방지
- ```java
  
			-- 트랜잭션 A
			START TRANSACTION;
			SELECT * FROM orders WHERE id BETWEEN 1 AND 10 FOR UPDATE;
			-- ⭐ Gap Lock 발동! (1~10 사이 공간에 락)
			
			-- 트랜잭션 B
			INSERT INTO orders (id, ...) VALUES (5, ...);
			-- ❌ 대기! (Gap Lock에 걸림)
		  ```
## 2.4. SERIALIZABLE 직렬화
### 2.4.1. 동작 원리
모든 트랜잭션을 순차적으로 실행하는 것처럼 동작
```java
-- 트랜잭션 A
START TRANSACTION;
SELECT * FROM product WHERE id = 1;
-- ⭐ SELECT만 해도 공유 락(Shared Lock) 획득!

-- 트랜잭션 B
START TRANSACTION;
UPDATE product SET stock = 90 WHERE id = 1;
-- ❌ 대기! (트랜잭션 A의 락이 풀릴 때까지)
```
성능 비교
```java
// 동시 요청 1000개 처리 시간 (가상 시나리오)
READ COMMITTED:    0.5초  ⚡⚡⚡⚡⚡
REPEATABLE READ:   0.7초  ⚡⚡⚡⚡
SERIALIZABLE:      5.0초  ⚡ (10배 느림!)
```
실무 사용
- 금융권 결제 시스템처럼 데이터 정합성이 극도로 중요한 곳에서만 사용

---
# 3. 실제 프로젝트에서의 사용
MySQL을 사용한다면 기본값(REPEATABLE READ)을 그대로 사용
주문/재고 차감 같은 핵심 로직에만 비관적 락을 사용하는 것이 베스트

---
# 내가 생각한 한 줄 정의
>데이터의 정합성을 지키기 위한 정책
