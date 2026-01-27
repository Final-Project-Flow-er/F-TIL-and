# QueryDSL

# 1. QueryDSL이란?
>자바 코드로 SQL/JPQL을 안전하게 작성하게 해주는 도구

---
# 2. JPQL 대신 사용하는 이유
JPQL은 문자열이므로 문법이 틀려도 알지 못 한다. 그래서 런타입 중에 메소드가 호출되어 JPQL이 파싱되어야 문법 오류를 발견할 수 있다.

---

# 3. Q클래스
## 3.1 사용 이유는?
QueryDSL이 JPQL을 생성할 수 있도록 필요한 데이터를 세팅해여 전달을 해야하는데 그러면 Entity정보가 필요하다. 하지만 Entity는 JPA에서 지원하는 모듈인데 QueryDSL은 JPA와 분리되어 있으므로 Entity를 사용하게 된다면 JPA에 종속이 되어 버린다. 이런 현상을 막고자 Entity정보를 담고 있는 Q클래스를 사용한다.

## 3.2 Q클래스란?
> 엔티티를 QueryDSL에서 쓰기 위해 자동 생성되는 쿼리 전용 메타 모델 클래스

---

# 4. Repository 사용법

## 4.1 구현
```java
public interface MemberRepository
extends JpaRepository<Member, Long>, MemberRepositoryCustom {
}
```
MemberRepository에 MemberRepositoryCustom을 상속받는다.

```java
public interface MemberRepositoryCustom {
    List<Member>search(MemberSearchCond cond);
}
```
MemberRepositoryCustom 인터페이스에 QueryDSL 메소드를 선언한다.

```java
public class MemberRepositoryImpl implements MemberRepositoryCustom {

private final JPAQueryFactory queryFactory;

@Override
public List<Member>search(MemberSearchCond cond) {
return queryFactory
            .selectFrom(member)
            .where(
                ageGoe(cond.getAge()),
                nameEq(cond.getName())
            )
            .fetch();
    }
}
// MemberSearchCond는 Request클래스
```
MemberRepositoryImpl은 MemberRepositoryCustom 인터페이스의 구현 클래스이다.

## Service 사용
```
@RequiredArgsConstructor
@Service
public class MemberService {

    private final MemberRepository memberRepository;

    public List<Member> searchMembers(MemberSearchCond cond) {
        return memberRepository.search(cond);
    }
}
```