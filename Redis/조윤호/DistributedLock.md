DistributedLock 분산 락

### 📝 공부 내용

# 분산락


> 분산 락(Distributed Lock)이란 여러 서버나 여러 프로세스가 동시에 실행되는 환경에서 하나의 공유 자원에 대해 동시에 접근하지 못하도록 제어하기 위한 동기화 메커니즘

---

# 1. 이와 비슷한 Spin Lock은?

>스핀 락은 루프를 돌면서 락을 획들할 때까지 계속 접근을 시도하는 방식

---

# 2. 분산락 vs 스핀락

분산 락은 해제 시까지 대기를 하지만, 스핀 락은 루프를 돌며 계속 락 획득을 시도한다.

---

# 3. 분산락 예시코드
```java
@Transactional
public void decrease(Long inventoryId, int amount) {

    RLock lock= redissonClient.getLock("lock:inventory:" + inventoryId);

    lock.lock();
    try {
        Inventoryinventory= inventoryRepository.findById(inventoryId)
                .orElseThrow();

        inventory.decrease(amount);

    }finally {
        lock.unlock();
    }
}
```

RLock은 Redis로 부터 "lock:inventory:" + inventoryId로 되어 있는 분산 락 객체를 가져오고 lock.lock()을 통해 한 번에 하나의 클라이언트만 통과하도록 잠근 다음 코드를 실행시키고 lock.unlock()을 통해 키를 다시 풀어준다.
