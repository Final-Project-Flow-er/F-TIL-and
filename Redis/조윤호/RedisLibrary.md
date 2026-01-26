# Redis 라이브러리

# 1. Redis 라이브러리란?
> 애플리케이션 코드(Java, Python 등)에서 Redis 서버와 통신하기 위한 클라이언트

---

# 2. 라이브러리

## 2.1 Jedis
> 동기식 작업을 지원하는 레디스 클라이언트

* 간단하고 사용하기 쉬운 API
* 스레드 안전하지 않기 때문에 멀티 스레드 환경에서 사용하려면 제디스 풀을 사용해야 함
* 고성능 환경에선 한계

## 2.2 Lettuce
> Netty 기반의 Redis Client로, 요청을 논 블로킹으로 처리하여 높은 성능을 가짐

* 비동기/논블로킹 지원으로 높은 처리량 가능

### 2.2.1 비동기 vs 논 블로킹
비동기(Asynchronous) : 요청하고 끝나도 기다리지 않고 다른 일 처리
논블로킹(Non-blocking) : 요청 중에도 스레드가 멈추지 않음
(스레드는 프로세스 안에서 실제로 작업을 수행하는 실행 단위)

## 2.3 Redisson
> Redis를 단순 클라이언트가 아니라 분산 시스템 도구처럼 활용할 수 있게 해주는 라이브러리

* 분산 락(RLock), 세마포어, 카운트다운 래치 등 제공
* Redis를 이용한 고수준 데이터 구조(Map, Set, Queue 등) 지원

---

# 3. Spring Data Redis
>Spring Data Redis는 Jedis/Lettuce 같은 클라이언트를 지원하면서, RedisTemplate을 통해 편리하게 Redis를 다룰 수 있게 해주는 Spring 통합 라이브러리다.
---


(다음에 Spring Data Redis에 대해 올려야게따..)
