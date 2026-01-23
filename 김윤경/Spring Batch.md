# Spring Batch

## Spring Batch란?

- 대량의 데이터를 일괄 처리(Batch Processing)하기 위한 경량 프레임워크
- 특정 시간에 많은 데이터를 효율적으로 처리하는 것이 목적
- 실시간 서비스 대비 개발 부담이 적다는 인식이 있으나, 대량 데이터 처리 시 성능 최적화 필수
- 로깅 및 추적, 트랜잭션 관리, 작업 처리 통계, 작업 재시작. 건너뛰기. 리소스 관리

## Spring Batch 구성 요소

- Job: 배치 처리 과정을 하나의 단위로 만든 객체. 배치 처리 과정에 있어 전체 계층의 최상단에 위치하며 1개 이상의 Step을 가짐. ex) “하루 정산 생성”, “월별 정산 마감” 같은 배치 작업 하나
  - JobRepository :
    <br> Spring Batch 내에서 사용되는 다양한 도메인 객체들의 기본적인 CRUD 작업에 이용.
    <br> Job을 생성하려면 기본적으로 필요.
    <br> Spring Batch 세팅 시 추가했던 @EnableBatchProcessing을 사용하면 자동으로 제공
  - start(), next() :
    <br> Step을 추가하기 위한 메서드
    <br> 이전 Step의 작업이 완료되어야만 다음 Step이 실행됨

- Step: Job 안의 실행 단계. 배치 작업을 정의 및 제어하고, 순차적인 단계를 캡슐화한 것. 개발자가 설계한 것에 따라 복잡해질 수도, 간단해질 수도 있음

  <img width="557" height="284" alt="image" src="https://github.com/user-attachments/assets/72a8f175-27ad-42ca-b1e7-2b508ec3fd1f" />

  
  - ItemReader, ItemProcessor, ItemWriter로 구성
    - ItemReader : 입력 데이터, 파일, DB 등등 다양한 소스로부터 item을 읽는 역할
    - ItemProcessor : 잉ㄹㄱ어온 데이터를 가공하는 역할
    - ItemWriter : DB 저장, 파일쓰기 전송

<img width="686" height="367" alt="image" src="https://github.com/user-attachments/assets/ae76a8e9-4031-4de6-bbe3-9ead27c618d6" />

- Step의 흐름은 위와 같은 사진임.
  - read()를 통해 item을 읽어온다. -> (ItemProcessor가 존재한다면) process()을 통해 item을 처리한다. -> write()를 통해 items을 사용한다.
 

## Spring Batch Architecture

<img width="471" height="425" alt="image" src="https://github.com/user-attachments/assets/76f41e2b-29bd-4e4f-b2af-19f2fe5f6b3e" />

- Application: 개발자가 작성한 모든 배치 Job과 코드들
- Core: 배치 작업을 시작하고 제어할 때 필요한 핵심 Runtime Classes (ex: JobLauncher, Job, Step)
- Infrastructure: 애플리케이션 개발자와 코어 프레임워크가 사용하는 공통 Reader, Writer, Service를 포함


