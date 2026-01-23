# BigDecimal

- BigDecimal은 Java에서 숫자를 정밀하게 저장하고 표현할수 있는 방법
- 소수점을 저장할 수 있는, 크기가 가장 큰 타입인 double은 소수점 정밀도에 한계가 있어서 값이 유실될 수 있다.
- Java언어에서 돈과 소수점을 다룬다면 BigDecimal이 더 정확한 방법이다.
- 하지만 BigDecimal은 속도가 느리고 기본 타입보다 사용이 조금 불편하다.

## 기존 숫자 타입의 한계

- 정수타입 (int, long)
  - 장점 : 처리하는 속도가 빠르고, 메모리 사용이 적다.
  - 단점 : 소수점 표현이 불가능하기 때문에 센트/원 단위의 금액처리를 위해 별도 로직이 필요하다.

- 부동 소수점 타입(float, double)
  - 장점 : 소수점 표현이 가능하고 넓은 범위의 값을 표현할 수 있다.
  - 단점 : 이진 부동 소수점 방식으로 인한 정확도 문제가 있다.
    
``` 
double a = 0.1;
double b = 0.2;

System.out.println(a + b);
```
일때, 기대값으로는 0.3이지만 실제 출력은 0.30000000000000004 가 출력이 된다.
- 왜 이런 일이 생길까? -> 0.1, 0.2같은 10진 소슨 컴퓨터의 2진 부동 소수점으로 정확히 표현이 불가능하다. -> 근사값으로 저장이 된다.

```
0.1 ≈ 0.10000000000000000555...
0.2 ≈ 0.20000000000000001110...
```
이 둘을 더하면 0.30000000000000004 라는 값이 나온다.

- 그래서 금액 계산에는 BigDecimal을 사용하게 되는데
```
  BigDecimal price =
    BigDecimal.valueOf(0.1).add(BigDecimal.valueOf(0.2));
```
정확히 0.3 이라는 값이 나온다.


- 다음은 BigDecimal, double, int/long 비교표이다,

<img width="1032" height="278" alt="image" src="https://github.com/user-attachments/assets/dee12ae4-803c-46d3-83bb-7e9220a53ba3" />


## BigDecimal의 기본용어

- precision (정밀도) : 유효숫자 개수. 소수점 위치과 상관없이 의미 있는 숫자 총 개수
```
BigDecimal x = new BigDecimal("123.45");
x.precision(); // 5
```
 유효숫자 1, 2, 3, 4, 5 -> 총 5개

- scale (스케일) : 소수점 아래 자릿수. 소수점 오른쪽에 몇 자리가 있는지
```
  BigDecimal y = new BigDecimal("123.4500");
  y.scale(); // 4
```
소수점 아래 :4500 -> 4자리
- MathContext (계산 규칙 묶음) : BigDecimal 연산 시 적용할 규칠 세트
 - BigDecimal 연산 시 적용할 규칙 세트
 - 포함 내용: precision, roundingMode
```
MathContext mc = new MathContext(3, RoundingMode.HALF_UP);

BigDecimal a = new BigDecimal("123.456");
BigDecimal b = a.round(mc); // 123
```
-> 유효숫자 3개까지만 허용


- DECIMAL128 : 자바가 제공하는 표준 MathContext. IEEE 754 Decimal128 표준 기반
  - 자바가 제공하는 표준 MathContext
  - IEEE 754 Decimal128 표준 기반
  - 내부 설정 precision = 34, roundingMode = HALF_EVEN
```
BigDecimal a = new BigDecimal("1");
BigDecimal b = new BigDecimal("3");

a.divide(b, MathContext.DECIMAL128);
```
-> 0.3333333333333333333333333333333333 -> 유효숫자 34자리ㅈ까지 정확히 계싼

- roundingMode (반올림 방식) : 자리수를 줄여야 할 때 어떻게 반올림 할지
```
BigDecimal a = new BigDecimal("2.345");
a.setScale(2, RoundingMode.HALF_UP); // -> 2.35
```
- HALF_UP: 우리가 아는 반올림
- HALF_EVEN: 은행가 반올림 (통계/금융에서 사용)

- scale (setScale) : 소수점 아래 자릿수를 강제로 맞춤
```
BigDecimal a = new BigDecimal("10");
a.setScale(2); // ArithmeticException
a.setScale(2, RoundingMode.HALF_UP); // -> 10.00
```

- 기본 상수 : flot, double과 달리 초기화가 어려워 자주 쓰는 0, 1, 10은 쓰기 편하게 미리 상수로 정의되어 있다.
  - BigDecimal.ZERO -> 0
  - BigDecimal.ONE -> 1
  - BigDecimal.TEN ->10
 
## 초기화
- double 타입으로 부터 BigDecimal 타입을 초기화하는 가장 안전한 방법은 문자열의 형태로 생성자에 전달하여 초기화하는 것이다.
- double 타입의 값을 그대로 전달할 경우 앞서 사칙연산 결과에서 본 것과 같이 이진수의 근사치를 가지게 되어 예상과 다른 값을 얻을 수 있다.

```
// double 타입을 그대로 초기화하면 기대값과 다른 값을 가진다.
// 0.01000000000000000020816681711721685132943093776702880859375
new BigDecimal(0.01);

// 문자열로 초기화하면 정상 인식
0.01
new BigDecimal("0.01");

// 위와 동일한 결과, double#toString을 이용하여 문자열로 초기화
// 0.01
BigDecimal.valueOf(0.01);
```

## 비교연산

- BigDecimal은 기본 타입이 아닌 오브젝트이기 때문에 동등 비교 연산을 유의해야한다.
- 따라서 BigDecimal값을 비교하려면 아래와 같은 방법을 사용해야 한다.

- 방법 1. equals() 메서드 사용
  - 두 BigDecimal 객체의 값과 스케일이 정확히 같은지 확인한다. 스케일이 다르면 값이 같더라도 false를 반환한다.
```
BigDeciaml a = new BigDecimal("2.01");
BigDecimal b = new BigDecimal("2.010");
boolean isEqual = a.equals(b); // false (스케일이 다름)
```

- 방법 2. compareTo() 메서드 사용
  - 숫자 값만 비교하며 스케일은 무시한다.

```
BigDecimal a = new BigDecimal("2.01");
BigDecimal b = new BigDecimal("2.010");
int result = a.compareTo(b); // 0 (숫자 값은 같음)
```
- 반환값 0 : 값이 같음.
- 반환값 1 : 첫 번째 값이 더 큼
- 반환값 -1 : 두 번째 값이 더 큼

- 주의 할 점이 있다면? -> 숫자 값만 비교하고 싶다면 compareTo()를 사용하는 것이 일반적이다.
 <br> equlas()는 스케일까지 엄격히 비교하므로 주의가 필요하다.
<br> == 연산자는 절대 사용하지 말아야 한다.

```
BigDecimal sumOfFoo = fooList.stream() // 리스트를 스트림으로 변환
    .map(FooEntity::getFooBigDecimal) // FooEntity → 그 안의 BigDecimal 필드만 뽑아냄
    .filter(foo -> Objects.nonNull(foo)) // 값이 null인 경우 제거
    .reduce(BigDecimal.ZERO, BigDecimal::add); // 0부터 시작해서 하나씩 더함
```
- fooList 안에 있는 BigDecimal 필드들의 합계를 구함
- 왜 BigDecimal.ZERO를 쓸까? -> 합의 초기값(identity). 스트림이 비어 있어도 결과가 null이 아니라 0이 되게 함

```
foolist.stream()
    .sorted(Comparator.comparing(it -> it.getAmount()))
    .collect(Collectors.toList());
```
- amount(BigDecimal) 기준으로 오름차순 정렬된 새로운 리스트를 만듦
- sorted()는 원본 리스트를 건드리지 않음. 결과는 collect(Collectors.toList())로 새 리스트
- Comparator.comparing()은 내부적으로 BigDecimal.compareTo()를 사용함.
- 원본 유지와 정렬된 결과만 필요하면 stream().sorted().collect()를 사용함.

```
foolist.sort(Comparator.comparing(it -> it.getAmount()));
```
- 원본 foolist 자체가 정렬된다. 새 리스트를 만들지 않음
- 내부 동작 : List.sort()는 in-place 정렬, 메모리 사용이 적고 빠름
- 언제 쓰면 좋을까? -> 이미 리스트 하나만 쓰고 있고 원본 순서가 바뀌어도 괜찮을 때


## BigDecimal의 외부 연동

- MySQL과 BigDecimal -> MySQL은 BigDecimal 타입에 대응하는 Decimal 타입을 제공한다. 

- JPA에서의 BigDecimal -> JDBC에서 MySQL/MaridDB의 DECIMAL 타입은 ResultSet 인터페이스의 getBigDecimal(), getString() 2개 메서드로 가능하다.
  <br> JPA 또한 별도의 작업 없이 엔티티 필드에 BigDecimal 타입을 사용하여 처리하면 된다.

- JSON 문자열 변환 -> 외부 서비스 간의 API 요청-응답 처리에서도 BigDecimal을 고려해야 한다. JSON 스펙에서는 BigDecimal 타입의 표현 방법에 대해 명확히 규정하고 있지 않다.
  <br> 따라서 API 응답을 표현할 때 혹시 모를 소수점 이하에서의 데이터 유실을 확실하게 예방하려면 BigDecimal을 숫자가 아닌 문자열로 응답해야 한다.



