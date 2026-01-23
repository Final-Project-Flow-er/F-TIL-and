# Index

---

> 특정 칼럼을 이용해 더욱 빠르게 검색하게 해 주는 색인표

---
# 1. B-Tree 구조란?
## 1.1. 정의
Balanced Tree 균형잡힌 트리
데이터가 정렬된 상태로 저장되며 항상 좌우 균형을 유지하는 트리 구조
## 1.2. 구조도
```java
                 [5]  ← Root Node (루트 노드)
                /   \
              /       \
           [2]         [8]  ← Branch Node (브랜치 노드)
          / \         /  \
        /     \     /      \
     [1,2]  [3,4]  [6,7]  [9,10]  ← Leaf Node (리프 노드)
       ↓      ↓      ↓      ↓
    실제 데이터 주소 (포인터)
```
## 1.3. 핵심 특징
### 1.3.1. 한 노드에 여러 데이터를 저장
N차 B-Tree의 경우 Root Node는 N-1개의 key 값 보유
자식 노드는 최대 N개
### 1.3.2. 항상 정렬된 상태 유지
오름차순/내림차순
데이터를 삽입할 때부터 정렬 상태가 됨
### 1.3.3. 균형 유지
모든 리프 노드의 깊이가 동일
### 1.3.4. key-value 구조
- key: 인덱스 칼럼 값
- value: 실제 데이터 주소
## 1.4. 궁금증
> Q: 데이터가 속한 리스트를 빨리 찾아낸다고 해도 해당 리스트의 크기가 큰데 거기서 원하는 값만 추출하는 것이 빠른가?
> A: 빠르다. 디스크가 아니라 메모리에서 처리하기 때문이다. 또한 이미 정렬되어 있기 때문에 그 시간은 무시할 만 한다.

> Q: 리프 노드가 아닌 노드들에는 하위 노드들의 주소만이 저장되어 있는가?
> A: 아니다. 모든 노드에 키와 값이 저장된다. 하지만 MySQL에서 사용하는 것은 B-Tree가 아니라 B+Tree인데 B+Tree는 리프에만 데이터를 저장한다. 다른 내부 노드는 키와 자식 포인터를 갖고 데이터는 갖지 않는다. 리프 노드에는 키와 실제 데이터를 저장한다. 리프 노드끼리 연결 리스트로 연결되어 있다.
> 그렇다면 왜 B-Tree가 아닌 B+Tree를 사용할까?
> 첫째로 데이터가 공간을 차지하기 때문에 데이터를 저장할 공간에 키와 포인터를 저장한다. 이러면 차수를 무한대로 늘릴 수 없는 상황에 트리의 높이가 낮아진다.
> 둘째로 범위 검색이 빠르다. B+Tree는 리프 노드가 연결 리스트이기 때문에 정렬되어 있는 상태에서 빠른 검색이 가능하다. 반면 B-Tree는 범위 검색 시 트리를 여러 번 타야한다. 1001번에서 2000번을 검색하면 1001번 찾고, 루트에서 1002번까지 찾고, 루트에서 1003번까지 찾고... 이걸 1000번 반복해야 한다.

> Q: B+Tree의 경우 리프 노드에 포인터까지 저장할 필요가 있는가? 어차피 데이터도 같이 저장되어 있는데.
> A: B+Tree에서 포인터는 연결 리스트의 포인터이다. 다음 순번의 데이터를 가리키고 있는 것이기 때문에 범위 검색에서 사용된다.

---
# 2. 왜 인덱스를 타면 빠른가
## 2.1. 인덱스가 없을 때(Full Table Scan)
`SELECT * FROM orders WHERE order_id=5000`
### 2.1.2. 동작 과정
```text
1. orders 테이블의 첫 번째 행부터 시작
2. 1번 행 확인 → order_id != 5000
3. 2번 행 확인 → order_id != 5000
4. 3번 행 확인 → order_id != 5000
...
5. 5000번 행 확인 → order_id == 5000 ✅ 찾음!

시간 복잡도: O(N) - 전체 스캔!
```
100만건의 데이터가 있으면 평균 50만건의 데이터를 읽어야 함
## 2.2. 인덱스가 있을 때(B-Tree Search)
```text
B-Tree 인덱스 (order_id):
높이(Height) = 3

Level 0 (Root):     [5000, 10000]
                    /      |      \
Level 1 (Branch):  [2500] [7500]  [15000]
                   / | \ / | \  / | \
Level 2 (Leaf):  리프 노드들 (실제 데이터 주소)
```
### 2.2.1. 동작 과정
```text
1. Root 노드 읽기: 5000 == 5000 → 왼쪽 포인터 따라감 (1회 I/O)
2. Branch 노드 읽기: 5000 > 2500 → 오른쪽 포인터 (1회 I/O)
3. Leaf 노드 읽기: 5000 찾음! (1회 I/O)
4. 실제 데이터 주소로 이동 (1회 I/O)

총 4회 디스크 I/O!
시간 복잡도: O(log N)
```
100만건이어도 3~4회 디스크 접근으로 찾음
## 2.3. 왜 O(log N)인가
B-Tree는 한 노드에 여러 개의 키를 저장하기 때문
```text
예: 101차 B-Tree (한 노드에 최대 100개 키 저장)

Level 0 (Root):      1개 노드 (최대 100개 키)
Level 1 (Branch):    101개 노드 (최대 10,100개 키)
Level 2 (Branch):    10,201개 노드 (최대 1,020,100개 키)
Level 3 (Leaf):      1,030,301개 노드

→ 높이 4로 약 100만 개 데이터 저장 가능!
```

---
# 3. 복합 인덱스(Composite Index)
2개 이상의 인덱스로 N차 조회하는 것
## 3.1. 예시
### 3.1.1. 실제 쿼리
```sql
-- 특정 매장의 완료된 주문 조회
SELECT * FROM orders
WHERE store_id = 1 AND status = 'COMPLETED';
```
### 3.1.2. 인덱스 설정
```sql
CREATE INDEX idx_store_status ON orders(store_id, status);
```
### 3.1.3. B-Tree 구조
```text
                    [store_id=1, status='COMPLETED']
                           /        |        \
[store_id=1, status='PENDING'] ... [store_id=2, status='COMPLETED']

리프 노드 구조:
(store_id=1, status='COMPLETED') → 실제 데이터 주소
(store_id=1, status='PENDING')   → 실제 데이터 주소
(store_id=2, status='COMPLETED') → 실제 데이터 주소
```
### 3.1.4. 쿼리 패턴별 인덱스 활용
1. 첫 번째 칼럼만 조회
```sql
SELECT * FROM orders WHERE store_id = 1;
-- ✅ 인덱스 사용! (store_id로 먼저 정렬되어 있음)
```
2. 첫 번째 + 두 번째 칼럼 조회
```sql
SELECT * FROM orders 
WHERE store_id = 1 AND status = 'COMPLETED';
-- ✅ 인덱스 완전 활용! (양쪽 다 정렬되어 있음)
```
3. 두 번째 칼럼만 조회 -> 이건 안 됨
```sql
SELECT * FROM orders WHERE status = 'COMPLETED';
-- ❌ 인덱스 사용 불가! (status는 store_id가 같을 때만 정렬됨)
```
- 인덱스를 일부만 사용하게 됨

---
# 4. 카럼 순서 결정 법칙
## 4.1. 원칙 1: 카디널리티가 높은 칼럼을 앞에
카디널리티: 중복도가 낮은 정도
```text
orders 테이블 (10만 건):
- store_id: 10개 (1번 매장, 2번 매장, ..., 10번 매장)
- status: 3개 (PENDING, COMPLETED, CANCELLED)
- user_id: 5000개 (다양한 사용자)

카디널리티: user_id > store_id > status
```
### 4.1.1. 추천 순서
```sql
-- ✅ 좋은 예
CREATE INDEX idx_user_store ON orders(user_id, store_id);

-- ❌ 나쁜 예
CREATE INDEX idx_status_store ON orders(status, store_id);
-- status는 3개 값만 있어서 분산이 안 됨!
```
## 4.2. 원칙 2: WHERE 절에서 = 조건이 많은 칼럼을 앞에
```sql
-- 쿼리 1: store_id는 항상 =, status는 가끔 IN
SELECT * FROM orders 
WHERE store_id = 1 AND status IN ('PENDING', 'COMPLETED');

-- 쿼리 2: status는 항상 =, store_id는 범위
SELECT * FROM orders 
WHERE store_id > 5 AND status = 'COMPLETED';

-- ✅ 추천 인덱스
CREATE INDEX idx_store_status ON orders(store_id, status);
-- store_id를 먼저!
```
## 4.3. 실제 쿼리 분석
### 4.3.1. 실 쿼리
```sql
-- 쿼리 A (80% 비중): 매장별 주문 조회
SELECT * FROM orders WHERE store_id = ?;

-- 쿼리 B (15% 비중): 매장별 + 상태별 조회
SELECT * FROM orders WHERE store_id = ? AND status = ?;

-- 쿼리 C (5% 비중): 상태별만 조회
SELECT * FROM orders WHERE status = ?;
```
### 4.3.2. 인덱스 설계
```sql
-- ✅ 주 인덱스 (쿼리 A, B 최적화)
CREATE INDEX idx_store_status ON orders(store_id, status);

-- ✅ 보조 인덱스 (쿼리 C 최적화)
CREATE INDEX idx_status ON orders(status);
```

---
# 5. 복합 인덱스 주의사항
## 5.1. 인덱스 순서 무시
```sql
-- 인덱스: (store_id, status, created_at)

-- ✅ 좋은 쿼리
WHERE store_id = 1 AND status = 'COMPLETED' AND created_at > '2026-01-01'

-- ⚠️ 일부만 사용
WHERE store_id = 1 AND created_at > '2026-01-01'
-- status를 건너뛰었으므로 created_at 인덱스 사용 불가!

-- ❌ 인덱스 사용 불가
WHERE status = 'COMPLETED' AND created_at > '2026-01-01'
-- 첫 번째 컬럼(store_id) 조건이 없음!
```
## 5.2. 범위 조건 뒤는 사용 불가
```sql
-- 인덱스: (store_id, price, status)

-- ⚠️ 문제
WHERE store_id = 1 AND price > 10000 AND status = 'COMPLETED'
-- price가 범위 조건(>)이므로, status 인덱스는 사용 불가!

-- ✅ 해결: 순서 변경
-- 인덱스: (store_id, status, price)
WHERE store_id = 1 AND status = 'COMPLETED' AND price > 10000
-- 모든 컬럼 인덱스 활용!
```

---
# 내가 생각한 한 줄 정의
> 우선순위를 주는 느낌
