# Dynamic Query

---

> 사용자의 요청 값에 따라 실행 시점에 SQL 문장이 실시간으로 바뀌는 쿼리

---
# 1. 정적 쿼리 vs 동적 쿼리
## 1.1. 정적 쿼리
정적 쿼리는 내용이 미리 고정되어 있음
조건이 바뀔 때마다 메소드를 따로 만들어야 함
```java
// 1. 이름으로만 검색할 때
findByTitle(String title);

// 2. 가격으로만 검색할 때
findByPrice(int price);

// 3. 둘 다 검색할 때
findByTitleAndPrice(String title, int price);

// 4. 만약 조건이 10개라면...? -> 메소드를 수백 개 만들어야 함 (지옥 시작)
```
## 1.2. 동적 쿼리
동적 쿼리는 조건이 들어오면 `WHERE`절을 붙이고 안 들어오면 뺌
하나의 코드로 모든 상황을 처리
```java
SELECT * FROM PRODUCT
WHERE 1=1
  -- 사용자가 title을 입력했으면 이 줄을 추가
  AND TITLE = ? 
  -- 사용자가 price를 입력했으면 이 줄을 추가
  AND PRICE = ?
```

---
# 2. 동적 쿼리 만들기
QueryDSL이 가장 좋음
자바 코드로 `if`문을 사용해 깔끔하게 조립 가능
직관적이며 버그가 적음
실무에서는 `BooleanExpression` 방식을 사용해 구현
```java
public List<Product> searchProduct(String title, Integer price) {
    return queryFactory
        .selectFrom(product)
        .where(
            // title이 null이면 무시, 있으면 조건 추가
            eqTitle(title), 
            // price가 null이면 무시, 있으면 조건 추가
            eqPrice(price)  
        )
        .fetch();
}

// 조립 부품 (메소드)
private BooleanExpression eqTitle(String title) {
    if (title == null || title.isEmpty()) return null; // null 반환 시 where 절에서 자동 생략됨
    return product.title.eq(title);
}
```

---
# 내가 생각한 한 줄 정의
>조건에 따라 변하는 쿼리
