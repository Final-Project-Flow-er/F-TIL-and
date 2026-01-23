# Spring Batch의 용어
스프링 배치에서 사용하는 주요 용어들과 의미는 다음과 같다.
- Job
  - Job은 전체 배치 처리 과정을 추상화한 개념으로, 하나 또는 그 이상의 Step을 포함하며, 스프링 배치 계층에서 가장 상위에 위치한다.
  - 각 Job은 고유한 이름을 가지며, 이 이름은 실행에 필요한 파라미터와 함께 JobInstance를 구별하는 데 사용된다.
- JobInstance
  - JobInstance는 특정 Job의 실제 실행 인스턴스를 의미한다. 예를 들어, "매일 아침 8시에 데이터를 처리"하는 Job을 구성한다고 가정하면, 1/1, 1/2 등 매일 실행될 때마다 새로운 JobInstance가 생성된다.
  - 한 번 생성도니 JobInstance는 해당 날짜의 데이터를 처리하는 데 사용되며, 실패했을 경우 같은 JobInstance를 다시 실행하여 작업을 완료할 수 있다.
- JobParameters
  - JobParameters는 JobInstance를 생성하고 구별하는 데 사용되는 파라미터이다.
  - Job이 실행될 때 필요한 파라미터를 공급하며, JobInstance를 구별하는 역할도 한다.
  - 스프링 배치는 String, Double, Long, Date 이렇게 4가지 타입의 파라미터를 지원한다.
- JobExecution
  - JobExecution은 JobInstance의 한 번의 시행 시도를 나타낸다.
  - 예를 들어, 1/1에 JobInstance가 실패했을 때 재시도하면, JobInstance에 대한 새로운 JobExecution이 생성된다.
  - JobExecution은 실행 상태, 시작 시간, 종료 시간, 생성 시간 등 JobInstance의 실행에 대한 세부 정보를 담고 있다.
- Step
  - Step은 Job의 하위 단계로서 실제 배치 처리 작업이 이루어지는 단위이다.
  - 한 개 이상의 Step으로 Job이 구성되며, 각 Step은 순차적으로 처리된다.
  - 각 Step 내부에서는 ItemReader, ItemProcessor, ItemWriter를 사용하는 chunk 방식 또는 Tasklet 하나를 가질 수 있다.
- StepExecution
  - StepExecution은 Step의 한 번의 실행을 나타내며, Step의 실행 상태, 실행 시간 등의 정보를 포함한다.
  - JobExecution과 유사하게, 각 Step의 실행 시도마다 새로운 StepExecution이 생성된다.
  - 또한, 읽은 아이템의 수, 쓴 아이템의 수, 커밋 횟수, 스킵한 아이템의 수 등의 Step 실행에 대한 상세 정보도 포함한다.
- ExecutionContext
  - ExecutionContext는 Step 간 또는 Job 실행 도중 데이터를 공유하는 데 사용되는 저장소이다.
  - JobExecutionContext와 StepExecutionContext 두 종류가 있으며, 범위와 저장 시점에 따라 적절하게 사용된다.
  - Job이나 Step이 실패했을 경우, ExecutionContext를 통해 마지막 실행 상태를 재구성하여 재시도 또는 복구 작업을 수행할 수 있다.
- JobRepository
  - JobRepository는 배치 작업에 관련된 모든 정보를 저장하고 관리하는 메커니즘이다.
  - Job 실행 정보(JobExecution), Step 실행 정보(StepExecution), Job 파라미터(JobParameters) 등을 저장하고 관리한다.
  - Job이 실행될 때, JobRepository는 새로운 JobExecution과 StepExecution을 생성하고, 이를 통해 실행 상태를 추적한다.
- JobLauncher
  - JobLauncher는 Job과 JobParameters를 받아 Job을 실행하는 역할을 한다.
  - 이는 전반적인 Job의 생명 주기를 관리하며, JobRepository를 통해 실행 상태를 유지한다.
- ItemReader
  - ItemReader는 배치 작업에서 처리할 아이템을 읽어오는 역할읋 한다.
  - 여러 형식의 데이터 소스(예:데이터 베이스, 파일, 메시지 큐 등)로부터 데이터를 읽어오는 다양한 ItemReader 구현체가 제공된다.
- ItemProcessor
  - ItemProcessor는 ItemReader로부터 읽어온 아이템을 처리하는 역할을 한다.
  - 이는 선택적인 부분으로서, 필요에 따라 사용할 수 있으며, 데이터 필터링, 변환 등의 작업을 수행할 수 있다.
- ItemWriter
  - ItemWriter는 ItemProcessor에서 처리된 데이터를 최종적으로 기록하는 역할을 한다.
  - ItemWriter 역시 다양한 형태의 구현체를 통해 데이터 베이스에 기록하거나, 파일을 생성하거나, 메시지를 발행하는 등 다양한 방식으로 데이터를 쓸 수 있다.
- Tasklet
  - Tasklet은 간단한 단일 작업, 예를 들어 리소스의 정리 또는 시스템 상태의 체크 등을 수행할 때 사용된다.
  - 이는 스프링 배치의 Step 내에서 단일 작업을 수행하기 위한 인터페이스로, 일반적으로 ItemReader, ItemProcessor, ItemWriter의 묶음을 가지는 Chunk 기반 처리 방식과는 다르다.
  - Tasklet의 execute 메소드는 Step의 모든 처리가 끝날 때까지 계속 호출된다.
- JobOperator
  - JobOperator는 외부 인터페이스로 Job의 실행과 중지, 재시작 등의 배치 작업 흐름 제어를 담당한다.
  - 이 인터페이스를 통해 JobLauncher와 JobRepository에 대한 직접적인 접근 없이도 배치 작업을 수행하고 상태를 조회할 수 있다.
- JobExplorer
  - JobExplorer는 Job의 실행 이력을 조회하는 데 사용된다.
  - JobRepository에서 제공하는 정보와 유사하지만, JobRepository는 주로 Job의 실행 도중인 상태에 대해 업데이트 하고 관리하는 반면, JobExplorer는 주로 읽기 전용 접근에 초점을 맞추고 있다.

# 메타 테이블
스프링 배치는 배치 작업의 상태를 관리하기 위한 메타 데이터를 저장하는 아래 6개의 테이블들을 자동으로 생성한다.
또한 배치 작업을 수행하면 자동으로 생성된 테이블들의 컬럼 값들이 채워진다.
<img width="621" height="560" alt="{E82A40D1-1BEA-4D44-9398-EC725F9CA463}" src="https://github.com/user-attachments/assets/502ffb02-ffb7-4c4d-b4d9-d00deaffe64a" />

1. BATCH_JOB_INSTANCE
   <img width="620" height="215" alt="{D3F7E13B-6D29-4DAB-B529-C4C1878F6BE2}" src="https://github.com/user-attachments/assets/e58fe0aa-1b8d-49ea-b708-85cb56ba5101" />
  BATCH_JOB_INSTANCE 테이블은 JobInstance와 관련된 모든 정보를 가지며, 전체 계층 구조의 최상위 역할을 한다.
  - JOB_INSTANCE_ID : 실행된 JobInstance의 ID
  - VERSION : 배치 테이블의 낙관적 락 전략을 위해 사용되는 값
  - JOB_NAME : 실행된 Job의 이름으로, null이 아니어야 함.
  - JOB_KEY : JobParameter로 생성된 JobInstance의 키(Job 중복 수행 체크를 위한 고유키)
2. BATCH_JOB_EXECUTION
  <img width="937" height="438" alt="{8685B72E-7CF2-4873-90A1-817B0EC61D3C}" src="https://github.com/user-attachments/assets/a06ddcb2-8169-453a-8f23-c6ea525846a6" />
  BATCH_JOB_EXECUTION 테이블은 JobExecution와 관련된 모든 정보가 들어있다.
  JobExecution은 JobInstance가 실행될 때마다 시작 시간, 종료 시간, 종료 코드 등 다양한 정보를 가지고 있다.
  - JOB_EXECUTION_ID : 실행된 JobExecution의 ID
  - VERSION : 배치 테이블의 낙관적 락 전략을 위해 사용되는 값
  - JOB_INSTANCE_ID : BATCH_JOB_INSTANCE 테이블의 외래 키
  - CREATE_TIME : JobExecution이 생성된 시간
  - START_TIME : JobExecution이 실행된 시간
  - END_TIME : JobExecution이 종료된 시간(성공과 실패 여부에 상관없이 실행이 완료된 시간을 의미)
  - STATUS : JobExecution의 상태(BatchStatus의 Enum 타입)
  - EXIT_CODE : JobExecution의 종료 코드
  - EXIT_MESSAGE : JobExecution의 종료 메시지. 에러가 발생한 경우 에러 메시지
  - LAST_UPDATED : JobExecution이 수정된 시간
3. BATCH_JOB_EXECUTION_PARAMS
  <img width="939" height="244" alt="{17426E10-E4CF-4D09-A3D2-9A5E4B6A095B}" src="https://github.com/user-attachments/assets/04aa5658-bef0-4546-a6de-e4201a72bc0a" />
  BATCH_JOB_EXECUTION_PARAMS 테이블은 JobParameters와 관련된 모든 정보가 들어있다.
  - JOB_EXECUTION_ID : 실행된 JobExecution의 ID(BATCH_JOB_EXECUTION 테이블의 외래 키)
  - TYPE_CD : JobParameter의 타입 코드(string, date, long, double)
  - KEY_NAME : JobParameter의 이름
  - STRING_VAL : JobParameter의 String 값(TYPE_CD가 String일 때 값이 존재)
  - DATETIME : JobParameter의 Date 값(TYPE_CD가 Date일 때 값이 존재)
  - LONG_VAL : JobParameter의 Long 값(TYPE_CD가 Long일 때 값이 존재)
  - DOUBLE_VAL : JobParameter의 Double 값(TYPE_CD가 Double일 때 값이 존재)
  - IDENTIFYING : JobInstance의 키의 생성에 포함되었는지 여부
4. BATCH_JOB_EXECUTION_CONTEXT
    <img width="687" height="247" alt="{408C80A5-DA0F-4A5E-A3C5-B2895AD629B8}" src="https://github.com/user-attachments/assets/8ab6efb4-37a2-4e7f-84c9-70fad87929f1" />
  BATCH_JOB_EXECUTION_CONTEXT 테이블은 작업의 실행 컨텍스트와 관련된 모든 정보가 들어있다.
  각 JobExecution마다 정확히 하나의 JobExecutionContext가 있다.
  이 ExecutionContext 데이터는 일반적으로 JobInstance가 실패 시 중단된 위치에서 다시 시작할 수 있는 정보를 저장하고 있다.
  - JOB_EXECUTION_ID : 실행된 JobExecution의 ID
  - SHORT_CONTEXT : 문자열로 저장된 JobExecutionContext 정보
  - SERIALIZED_CONTEXT : 직렬화하여 저장된 JobExecutionContext 정보
5. BATCH_STEP_EXECUTION
  <img width="935" height="697" alt="{6260D12B-A57C-471C-AEC7-F0D3E2E22AC7}" src="https://github.com/user-attachments/assets/f4bba998-346d-4c08-8a9e-2b80c8e9c75b" />
  BATCH_STEP_EXECUTION 테이블은 StepExecution 객체와 관련된 모든 정보가 저장된다.
  BATCH_JOB_EXECUTION 테이블과 유사하며, 생성된 각 JobExecution에 대해 항상 단계당 하나 이상의 항목이 존재한다.
  STEP의 EXECUTION 정보인 읽은 수, 키멋 수, 스킵 수 등 다양한 정보를 추가로 담고 있다.
  - STEP_EXECUTION_ID : 실행된 StepExecution의 ID
  - VERSION : 배치 테이블의 낙관적 락 전략을 위해 사용되는 값
  - STEP_NAME : 실행된 StepExecution의 Step 이름
  - JOB_EXECUTION_ID : 실행된 JobExecution의 ID
  - START_TIME : StepExecution이 시작된 시간
  - END_TIME : StepExecution이 종료된 시간(성공과 실패 여부에 상관없이 실행이 완료된 시간을 의미)
  - STATUS : StepExecution의 상태(BatchStatus의 Enum 타입)
  - COMMIT_COUNT : StepExecution 실행 중, 커밋한 횟수
  - READ_COUNT : StepExecution 실행 중, 읽은 데이터 수
  - FILTER_COUNT : StepExecution 실행 중, 필터링된 데이터 수
  - WRITE_COUNT : StepExecution 실행 중, 작성 및 커밋된 데이터 수
  - READ_SKIP_COUNT : StepExecution 실행 중, 읽기를 스킵한 데이터 수
  - WIRTE_SKIP_COUNT : StepExecution 실행 중, 작성을 스킵한 데이터 수
  - PROCESS_SKIP_COUNT : StepExecution 실행 중, 처리를 스킵한 데이터 수
  - EXIT_CODE : StepExecution의 종료 코드
  - ROLLBACK_COUNT : StepExecution 실행 중, 롤백 횟수
  - EXIT_MESSAGE : StepExecution의 종료 메시지. 에러가 발생한 경우 에러 메시지
  - LAST_UPDATED : StepExecution이 수정된 시간
6. BATCH_STEP_EXECUTION_CONTEXT
  <img width="700" height="260" alt="{E92AEC91-763A-48AD-8FF3-565582747D1B}" src="https://github.com/user-attachments/assets/9e65985e-926c-4f22-810b-fc2ad291b275" />
  BATCH_STEP_EXECUTION_CONTEXT 테이블은 StepExecutionContext와 관련된 모든 정보가 저장되며, 스텝 실행 당 정확히 하나의 ExecutionContext가 있으며, 특정 스텝 실행을 위해 유지되어야 하는 모든 데이터가 포함되어 있다.
  이 ExecutionContext 데이터는 일반적으로 JobInstance가 실패 시 중단된 위치에서 다시 시작할 수 있는 정보를 저장하고 있다.
  - STEP_EXECUTION_ID : 실행된 StepExecution의 ID
  - SHORT_CONTEXT : 문자열로 저장된 StepExecutionContext 정보
  - SERAILZED_CONTEXT : 직렬화하여 저장된 StepExecutionContext 정보
