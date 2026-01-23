# BuilderBuilder, BuilderExpression 

---

> 사용자가 입력한 검색 조건을 동적으로 설정하는 역할

---
# 1. 사용법
```java
@Repository
@RequiredArgsConstructor
public class ProductRepositoryImpl implements ProductRepositoryCustom {
    
    private final JPAQueryFactory queryFactory;
    
    public List<Product> searchProducts(ProductSearchCondition condition) {
        // ⭐ BooleanBuilder 생성
        BooleanBuilder builder = new BooleanBuilder();
        
        // 조건 1: 상품명 (있으면 추가)
        if (condition.getName() != null && !condition.getName().isEmpty()) {
            builder.and(product.name.contains(condition.getName()));
        }
        
        // 조건 2: 최소 가격 (있으면 추가)
        if (condition.getMinPrice() != null) {
            builder.and(product.price.goe(condition.getMinPrice()));  // goe: >=
        }
        
        // 조건 3: 최대 가격 (있으면 추가)
        if (condition.getMaxPrice() != null) {
            builder.and(product.price.loe(condition.getMaxPrice()));  // loe: <=
        }
        
        // 조건 4: 재고 있음 (true일 때만)
        if (condition.getInStock() != null && condition.getInStock()) {
            builder.and(product.stock.gt(0));
        }
        
        // ⭐ where에 builder 전달
        return queryFactory
            .selectFrom(product)
            .where(builder)  // 조건이 없으면 전체 조회
            .orderBy(product.createdAt.desc())
            .fetch();
    }
}
```

---
# 2. OR 조건 결합
```java
public List<Product> searchProductsAdvanced(ProductSearchCondition condition) {
    BooleanBuilder builder = new BooleanBuilder();
    
    // (이름 OR 설명)에 "떡볶이" 포함
    if (condition.getKeyword() != null) {
        BooleanBuilder orBuilder = new BooleanBuilder();
        orBuilder.or(product.name.contains(condition.getKeyword()));
        orBuilder.or(product.description.contains(condition.getKeyword()));
        
        builder.and(orBuilder);  // WHERE (name LIKE '%떡볶이%' OR description LIKE '%떡볶이%')
    }
    
    // 가격 범위
    if (condition.getMinPrice() != null) {
        builder.and(product.price.goe(condition.getMinPrice()));
    }
    
    return queryFactory
        .selectFrom(product)
        .where(builder)
        .fetch();
}
```

---
# 3. BooleanExpression
| 구분      | BooleanBuilder   | BooleanExpression |
| ------- | ---------------- | ----------------- |
| **가변성** | 가변 객체 (상태 변경 가능) | 불변 객체​            |
| **재사용** | 어려움              | 쉬움 (메서드로 분리)      |
| **가독성** | 중간               | 높음                |
| **테스트** | 어려움              | 쉬움                |
## 3.1. 사용법
```java
@Repository
@RequiredArgsConstructor
public class ProductRepositoryImpl {
    
    private final JPAQueryFactory queryFactory;
    
    public List<Product> searchProducts(ProductSearchCondition condition) {
        return queryFactory
            .selectFrom(product)
            .where(
                nameContains(condition.getName()),        // ⭐ 메서드로 분리
                priceGoe(condition.getMinPrice()),
                priceLoe(condition.getMaxPrice()),
                stockGt()
            )
            .fetch();
    }
    
    // ⭐ 재사용 가능한 조건 메서드
    private BooleanExpression nameContains(String name) {
        return name != null ? product.name.contains(name) : null;
    }
    
    private BooleanExpression priceGoe(Integer minPrice) {
        return minPrice != null ? product.price.goe(minPrice) : null;
    }
    
    private BooleanExpression priceLoe(Integer maxPrice) {
        return maxPrice != null ? product.price.loe(maxPrice) : null;
    }
    
    private BooleanExpression stockGt() {
        return product.stock.gt(0);
    }
    
    // ⭐ 조건 조합도 가능!
    private BooleanExpression priceRange(Integer minPrice, Integer maxPrice) {
        BooleanExpression min = priceGoe(minPrice);
        BooleanExpression max = priceLoe(maxPrice);
        
        if (min != null && max != null) {
            return min.and(max);  // min AND max
        }
        if (min != null) return min;
        if (max != null) return max;
        return null;
    }
}
```
메소드로 조건을 빼서 조합하고 호출해 사용하는 것
## 3.2. 장점
null 반환 시 자동으로 조건 무시
메소드로 분리해서 재사용 (다른 쿼리에서도 사용 가능)
테스트 작성 쉬움 (조건 메소드만 단위 테스트)

---
# 내가 생각한 한 줄 정의
> 동적 쿼리를 만듬에 있어 가독성과 재사용성 향상
