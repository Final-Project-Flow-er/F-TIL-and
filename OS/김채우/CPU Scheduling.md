CPU Scheduling

---
> 운영체제의 핵심 기능으로 여러 프로세스 중 어떤 프로세스에게 CPU를 할당하지 결정하는 것

---
# 1. 정의
여러 프로세스 중 어떤 프로세스에게 **CPU**를 할당할지 결정하는 것

---
# 2. 종류
## 2.1. 장기 스케쥴러(Long-term Schedular)
새로운 프로세스를 시스템에 받아들일지 결정
1. 하드디스크의 프로그램
2. 장기 스케쥴러 판단: 메모리에 올릴지 말지
   현대 운영체제에서는 메모리가 충분하기 때문에 잘 사용하지 않음
## 2.2. 중기 스 케쥴러(Medium-term Schedular)
메모리가 부족할 때 프로세스를 디스크로 내보냄(Swap)
1. 메모리 부족
2. 중기 스케쥴러: 어떤 프로세스를 디스크로 내보낼지 결정
3. 메모리에서 디스크로 Swap
## 2.3. 단기 스케쥴러(Short-term Schedular)
**Ready Queue**의 프로세스 중 누구에게 CPU를 줄지 결정
1. Ready Queue: P1, P2, P3, P4 대기
2. 단기 스케쥴러: P2 결정
3. CPU -> P2 실행
   이게 주로 다루는 CPU 스케쥴링

---
# 3. 스케쥴링 알고리즘
## 3.1. FCFS(First-Come First-Served)
선착순
가장 단순한 방식
Ready Queue에 P1, P2, P3이 있고
P1: 24ms, P2: 3ms, P3: 3ms의 실행 시간을 가질 때
순서대로 진행되면 P2, P3는 각각 24ms, 27ms의 대기 시간을 가짐
**문제점**: **Convoy Effect** (긴 프로세스 때문에 짧은 프로세스들이 대기)
## 3.2. SJF(Shortest Job First)
CPU 버스트 시간이 가장 짧은 프로세스 먼저
Ready Queue에 P1, P2, P3이 있고
P1: 24ms, P2: 3ms, P3: 3ms의 실행 시간을 가질 때
P2, P3, P1 순서대로 실행
**문제점**: **Starvation** (긴 프로세스가 무한 대기 가능)
## 3.3. Priority Scheduling
우선순위가 높은 프로세스 먼저
Ready Queue:
P1(우선순위 3, 0ms)
P2(우선순위 1, 5ms)
P3(우선순위 2, 2ms)
P2, P3, P1 순서대로 실행
**문제점**: **Starvation**
- 우선순위 낮은 프로세스가 무한 대기
- 해결: Aging (대기 시간이 길수록 우선순위 상승)
## 3.4. Round Robin(RR)
**실제로 가장 많이 사용**
각 프로세스에 동일한 시간 할당
시간 끝나면 다음 프로세스
Time Quantum = 4ms : 시간 지정
Ready Queue:
P1 - 24ms
P2 - 3ms
P3 - 3ms
P1 4ms동안 실행, 큐 맨 뒤로
P2 3ms동안 실행, 완료
P3 3ms동안 실행, 완료
P1 4ms동안 실행, 큐 맨 뒤로
... 반복
### 3.4.1. 장점
공평함
- 모두에게 기회 제공
  응답 시간 빠름
- 대화형 시스템에 적합
### 3.4.2. 주의해야 할 점
**Time Quantum 선택이 중요**
너무 작으면 Context Switch 오버헤드 상승
너무 크면 FCFS와 동일
적절한 값: 10~100ms
## 3.5. Multilevel Queue
다단계 큐
프로세스를 여러 큐로 분류해 각 큐는 다른 알고리즘 사용
1. System Process: 우선순위 높음 -> FCFS
2. Interactive Process: Round Robin -> 빠른 응답
3. Batch Process: 우선순위 낮음 -> FCFS
   System Process 큐부터 확인
   비어있으면 Interactive 큐
   비어있으면 Batch 큐
## 3.6. Multilevel Feedback Queue
다단계 피드백 큐
프로세스가 큐 사이를 이동 가능
Aging으로 Starvation 해결
1. Q0: Round Robin, 8ms -> 신규 프로세스
2. Q1: Round Robin, 16ms -> 8ms안에 완료 못하면 강등
3. Q2: FCFS -> 16ms 안에 완료 못하면 여기로
   P1 도착 -> Q0 8ms 사용, 완료 못함 -> Q1으로 강등
   P1 -> Q1, 16ms 사용, 완료 못함 -> Q2로 강등
   P1 -> Q2, FCFS 실행
   현대 운영체제가 사용하는 방식

---
# 5. 선점(Preemptive) vs 비선점(Non-preemptive)
## 5.1. 비선점
프로세스가 자발적으로 CPU를 반납할 때까지 빼앗지 못함
## 5.2. 선점
우선순위가 높은 프로세스가 도착하면 CPU를 빼앗을 수 있음
현대 운영체제는 대부분 선점형

---
# 6. Context Switch
문맥 교환
CPU가 한 프로세스에서 다른 프로세스로 전환할 때 발생
**오버헤드**: Context Switch가 너무 자주 발생하면 성능 저하

---
# 내가 생각한 한 줄 정의
> 한정된 자원을 현명하게 사용하기 위해 스케쥴을 조정하는것 

