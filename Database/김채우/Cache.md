# Cache

---

> 성능 최적화의 핵심으로 자주 사용되는 데이터를 임시로 빠른 저장소에 보관

---
# 1. 캐시 계층 구조 더 자세히 설명해줘
```text
속도 ⚡⚡⚡⚡⚡     용량 📦        가격 💰💰💰
    ↑               ↓              ↑

Level 0: CPU 레지스터
         - 0.3ns
         - 수십 byte
         - CPU 내부

Level 1: L1 캐시 (CPU)
         - 0.5~1ns
         - 32~64 KB
         - 코어당 독립

Level 2: L2 캐시 (CPU)
         - 3~7ns
         - 256 KB ~ 1 MB
         - 코어당 독립

Level 3: L3 캐시 (CPU)
         - 10~20ns
         - 8~32 MB
         - 모든 코어 공유

Level 4: 메인 메모리 (RAM)
         - 50~100ns
         - 8~64 GB
         - 시스템 전체

Level 5: 애플리케이션 캐시 (Redis)  ⭐ 여기!
         - 0.1~1ms (100,000~1,000,000ns)
         - 수십 GB
         - 네트워크 통신

Level 6: SSD
         - 0.1~1ms
         - 100 GB ~ 수 TB

Level 7: HDD
         - 5~10ms
         - 수 TB

    ↓               ↑              ↓
속도 💤           용량 📦📦📦    가격 💰
```

---
# 2. **캐싱 전략**
## 2.1. 전략 1: Cache-Aside(Look-Aside)
가장 많이 사용하는 전략
애플리케이션이 직접 캐시를 관리
```java
@Service
@RequiredArgsConstructor
public class ProductService {
    
    private final ProductRepository productRepository;
    private final RedisTemplate<String, Product> redisTemplate;
    
    public Product getProduct(Long productId) {
        String cacheKey = "product:" + productId;
        
        // 1. 캐시 조회
        Product cached = redisTemplate.opsForValue().get(cacheKey);
        if (cached != null) {
            return cached;  // ⚡ Cache Hit
        }
        
        // 2. 캐시 미스 → DB 조회
        Product product = productRepository.findById(productId)
            .orElseThrow();
        
        // 3. 캐시에 저장
        redisTemplate.opsForValue()
            .set(cacheKey, product, 10, TimeUnit.MINUTES);
        
        return product;
    }
    
    // 데이터 수정 시 캐시 무효화
    public Product updateProduct(Long productId, ProductUpdateDto dto) {
        Product product = productRepository.findById(productId)
            .orElseThrow();
        
        product.update(dto);
        productRepository.save(product);
        
        // ⭐ 캐시 삭제
        String cacheKey = "product:" + productId;
        redisTemplate.delete(cacheKey);
        
        return product;
    }
}
```
### 2.1.1. 흐름
1. 애플리케이션 -> Redis 조회
2. Cache Hit -> 반환
3. Cache Miss -> DB 조회 -> Redis 저장 -> 반환
### 2.1.2. 장점
필요한 데이터만 캐싱
- 메모리 효율적
### 2.1.3. 단점
Cache Miss 시 두 번의 조회(Redis + DB)
코드 복잡
## 2.2. Read-Through(Spring Cache 방식)
캐시가 DB 조회를 자동으로 처리
```java
@Service
@RequiredArgsConstructor
public class ProductService {
    
    private final ProductRepository productRepository;
    
    // ⭐ 어노테이션만 추가!
    @Cacheable(value = "products", key = "#productId")
    public Product getProduct(Long productId) {
        // 1. 캐시 확인 (자동)
        // 2. Cache Miss 시 이 메서드 실행
        // 3. 결과를 캐시에 저장 (자동)
        return productRepository.findById(productId)
            .orElseThrow();
    }
    
    // 캐시 무효화
    @CacheEvict(value = "products", key = "#productId")
    public Product updateProduct(Long productId, ProductUpdateDto dto) {
        Product product = productRepository.findById(productId)
            .orElseThrow();
        
        product.update(dto);
        return productRepository.save(product);
    }
    
    // 캐시 강제 갱신
    @CachePut(value = "products", key = "#result.id")
    public Product createProduct(ProductCreateDto dto) {
        Product product = Product.create(dto);
        return productRepository.save(product);
    }
}
```
### 2.2.1. 설정
```java
@Configuration
@EnableCaching  // ⭐ 캐싱 활성화
public class CacheConfig {
    
    @Bean
    public RedisCacheManager cacheManager(RedisConnectionFactory connectionFactory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(10))  // 10분 TTL
            .serializeKeysWith(
                RedisSerializationContext.SerializationPair
                    .fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(
                RedisSerializationContext.SerializationPair
                    .fromSerializer(new GenericJackson2JsonRedisSerializer()));
        
        return RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(config)
            .build();
    }
}
```
### 2.2.2. 장점
코드 간결(어노테이션만 추가하니까)
AOP로 자동 처리
### 2.2.3. 단점
복잡한 캐싱 로직은 커스터마이징이 어려움
## 2.3. Write-Through
DB 쓰기 시 캐시도 함께 업데이트
```java
public Product updateProduct(Long productId, ProductUpdateDto dto) {
    Product product = productRepository.findById(productId)
        .orElseThrow();
    
    product.update(dto);
    Product saved = productRepository.save(product);
    
    // ⭐ DB와 캐시 동시 업데이트
    String cacheKey = "product:" + productId;
    redisTemplate.opsForValue()
        .set(cacheKey, saved, 10, TimeUnit.MINUTES);
    
    return saved;
}
```
### 2.3.1. 장점
캐시와 DB의 일관성 보장
### 2.3.2. 단점
쓰기 성능 저하(두 곳에 저장하니까)
## 2.4. Write-Behind(Write-Back)
캐시에만 먼저 쓰곧 나중에 DB에 비동기로 저장
```java
public void incrementViewCount(Long productId) {
    String cacheKey = "view:count:" + productId;
    
    // ⭐ Redis에만 증가
    redisTemplate.opsForValue().increment(cacheKey);
    
    // 나중에 스케줄러가 DB에 일괄 저장
}

@Scheduled(fixedRate = 60000)  // 1분마다
public void syncViewCountsToDB() {
    // Redis의 조회수를 DB에 일괄 저장
}
```
### 2.4.1. 장점
쓰기 성능 극대화
DB 부하 감소
### 2.4.2. 단점
데이터 유실 위험(Redis 장애 시)
구현 복잡

---
# 3. 캐시 사용 패턴
## 3.1. 패턴 1: 단일 객체 캐싱
```java
// 상품 상세 조회
@Cacheable(value = "products", key = "#productId")
public Product getProduct(Long productId) {
    return productRepository.findById(productId)
        .orElseThrow();
}
```
### 3.1.1. Redis 저장 구조
```text
Key: products::1001
Value: {"id":1001,"name":"떡볶이","price":5000}
TTL: 600초
```
## 3.2. 패턴 2: 리스트 캐싱
```java
// 인기 상품 Top 10
@Cacheable(value = "popular:products", key = "'top10'")
public List<Product> getPopularProducts() {
    return productRepository.findTop10ByOrderBySalesDesc();
}

// 매장별 메뉴 목록
@Cacheable(value = "store:menus", key = "#storeId")
public List<Product> getStoreMenus(Long storeId) {
    return productRepository.findByStoreId(storeId);
}
```
## 3.3. 패턴 3: 조건부 캐싱(동적 키)
```java
// 검색 결과 캐싱
@Cacheable(
    value = "search:products",
    key = "#keyword + ':' + #page + ':' + #size"
)
public Page<Product> searchProducts(
    String keyword, int page, int size) {
    
    Pageable pageable = PageRequest.of(page, size);
    return productRepository.findByNameContaining(keyword, pageable);
}
```
### 3.3.1. Redis 키
```text
search:products::떡볶이:0:10
search:products::떡볶이:1:10
search:products::순대:0:10
```
## 3.4. 패턴 4: 조건부 캐시 무효화
```java
// 새 상품 등록 시 인기 상품 캐시 삭제
@CacheEvict(
    value = "popular:products",
    allEntries = true  // ⭐ 전체 삭제
)
public Product createProduct(ProductCreateDto dto) {
    return productRepository.save(Product.create(dto));
}

// 특정 매장 메뉴만 삭제
@CacheEvict(value = "store:menus", key = "#storeId")
public void updateStoreMenu(Long storeId, Long productId) {
    // 업데이트 로직
}
```

---
# 4. 캐시 키 설계
```java
// ✅ 좋은 예: 계층적 구조
"product:1001"
"store:5:menus"
"user:2001:orders:recent"
"search:results:떡볶이:page:1"

// ❌ 나쁜 예: 규칙 없음
"p1001"
"storeMenus5"
"user_orders_2001"
```
## 4.1. 동적 키 생성
```java
@Cacheable(
    value = "orders",
    key = "#userId + ':' + #status + ':' + #page",
    condition = "#userId != null"  // ⭐ 조건부 캐싱
)
public Page<Order> getUserOrders(
    Long userId, OrderStatus status, int page) {
    // ...
}
```

---
# 5. TTL(Time To Live) 설정
```java
@Bean
public RedisCacheManager cacheManager(RedisConnectionFactory factory) {
    Map<String, RedisCacheConfiguration> configs = new HashMap<>();
    
    // products: 10분
    configs.put("products",
        RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(10)));
    
    // popular:products: 5분
    configs.put("popular:products",
        RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(5)));
    
    // store:menus: 30분
    configs.put("store:menus",
        RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(30)));
    
    return RedisCacheManager.builder(factory)
        .cacheDefaults(RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(10)))
        .withInitialCacheConfigurations(configs)
        .build();
}
```

---
# 6. 캐시 적용 기준
## 6.1. 좋은 경우
```text
1. 읽기가 많고 쓰기가 적은 데이터
   - 상품 정보, 카테고리, 메뉴
   
2. 자주 조회되는 데이터
   - 인기 상품, 베스트 매장
   
3. 연산 비용이 높은 데이터
   - 통계, 집계 쿼리 결과
   
4. 변경 주기가 긴 데이터
   - 설정, 공지사항
```
## 6.2. 부적합 경우
```text
1. 실시간 정확성이 중요한 데이터
   - 재고 수량, 결제 상태
   
2. 자주 변경되는 데이터
   - 주문 상태, 배송 위치
   
3. 사용자마다 다른 데이터
   - 개인화된 추천
   
4. 보안이 중요한 데이터
   - 비밀번호, 결제 정보
```

---
# 7. 실무 팁
## 7.1. 캐시 워밍업
```java
@Component
@RequiredArgsConstructor
public class CacheWarmer implements ApplicationListener<ContextRefreshedEvent> {
    
    private final ProductService productService;
    
    @Override
    public void onApplicationEvent(ContextRefreshedEvent event) {
        // 서버 시작 시 자주 사용되는 데이터 미리 캐싱
        productService.getPopularProducts();
        productService.getAllCategories();
    }
}
```
## 7.2. 캐시 Stampede 방지
```java
// 문제: TTL 만료 시 동시에 수천 명이 DB 조회
// 해결: 분산 락 사용

@Cacheable(value = "products", key = "#id", sync = true)  // ⭐ sync
public Product getProduct(Long id) {
    return productRepository.findById(id).orElseThrow();
}
```
## 7.3. 모니터링
```java
@Component
@RequiredArgsConstructor
public class CacheMonitor {
    
    private final CacheManager cacheManager;
    
    @Scheduled(fixedRate = 60000)
    public void logCacheStats() {
        cacheManager.getCacheNames().forEach(cacheName -> {
            Cache cache = cacheManager.getCache(cacheName);
            // 캐시 히트율, 사이즈 등 로깅
        });
    }
}
```

---
# 8. 캐시 핵심 개념
1. 자주 사용되는 데이터를 빠른 저장소에 보관
2. 메모리(Redis) 사용 -> 100배 빠름
3. TTL 설정으로 자동 무효화
4. 전략 선택 중요(Cache Aside, Read-Through 등)

---
# 내가 생각한 한 줄 정의
>많이 쓰는거 미리 빼 두기
