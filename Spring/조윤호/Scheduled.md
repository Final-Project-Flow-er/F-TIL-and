# Scheduled

# 1. @Scheduled란?

>정해진 시간이나 주기마다 메서드를 자동 실행

* @Scheduled은 싱글 스레드에서 실행되며, 만약 두 개이상의 @Scheduled이 있으면 별도의 병렬 스케줄링 설정을 하지 않으면 순차적으로 실행된다.

---

# 2. 사용 방법

@Scheduled을 활성화 하려면 애플리케이션에 @EnableScheduling을 추가해야 한다. 추가하게 되면 @Scheduled이 있는 메서드들이 자동으로 실행이 된다.

```
@EnableScheduling
@SpringBootApplication
public class DemoApplication {

    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }

}
```

---

# 3. 적용방법

```
@Slf4j
@Component
public class SchedulingTest {

    @Scheduled(fixedDelay = 1000)
    public void scheduled() {
        log.info("Scheduler 실행");
    }
}
```

실행결과
```
2026-01-30T09:49:35.194+09:00  INFO 16236 --- [   scheduling-1] com.example.demo.SchedulingTest          : Scheduler 실행
2026-01-30T09:49:36.206+09:00  INFO 16236 --- [   scheduling-1] com.example.demo.SchedulingTest          : Scheduler 실행
2026-01-30T09:49:37.219+09:00  INFO 16236 --- [   scheduling-1] com.example.demo.SchedulingTest          : Scheduler 실행
```

---

# 4. cron
> 특정 시간, 요일, 날짜에 메소드를 실행하고 싶을 때 사용

## 4.1. 단위
```
초 분 시 일 월 요일
```
| 필드 | 의미 | 허용 범위 |
|------|------|-----------|
| 초   | 초 단위 | 0 ~ 59 |
| 분   | 분 단위 | 0 ~ 59 |
| 시   | 시 단위 | 0 ~ 23 |
| 일   | 일(day) | 1 ~ 31 |
| 월   | 월(month) | 1 ~ 12 |
| 요일 | 요일 | 1 ~ 7 (일 ~ 토) |

## 4.2. 특수문자

"*" : 모든 값을 의미

"?" : 특정한 값이 없음을 의미

"-" : 범위를 나타낼 때 사용 → 월요일부터 수요일까지 - MON-WED

"," : 특정 값을 여러 개 나열할 때 사용 → 월,수,금 - MON,WED,FRI

"/" : 시작 시간 /단위 → 0분부터 매 5분 - 0/5

"L" : 일에서 사용하면 마지막 일, 요일에서 사용하면 마지막 요일(토요일)

"W" : 가장 가까운 평일 → 15일에서 가장 가까운 평일 - 15W

"#" : 몇째 주의 무슨 요일을 표현 → 2번째주 수요일 - 3#2

### 4.2.1 "/" 의미
> / = 주기적으로 실행 (간격 지정)
```
시작값/간격
```
### 4.2.2 예시
1.
```
"*/5 * * * * ?"
```
결과
```
0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55초
```
2.
```
"10/5 * * * * ?"
```
결과
```
10, 15, 20, 25, 30, 35, 40, 45, 50, 55초
```


## 4.3. 예시
```
"0 0 * * * ?"   // 매 정각
"0 0 9 * * ?"   // 매일 오전 9시
"0 0 0 * * ?"   // 매일 자정
"0 0 0 ? * 2"    // 매주 월요일 자정
"0 */10 * * * ?" // 10분마다

```
