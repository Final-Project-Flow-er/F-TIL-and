## Jira란?
이슈(할 일, 기능 등)를 티켓으로 관리하는 협업 도구

## 주요 기능
| 기능     | 설명                        |
| ------ | ------------------------- |
| 이슈(티켓) | 할 일, 기능, 버그 하나하나를 카드처럼 관리 |
| 상태 관리  | 해야 할 일 → 진행 중 → 완료 |
| 담당자    | 누가 이 작업 맡았는지              |
| 스프린트   | 일정 단위(이번 주/스프린트)로 작업 묶기      |
| 히스토리   | 작업 변경 이력 추적               |

## Jira의 장점  
- 커밋 메시지에 이슈 번호를 적으면 Jira와 GitHub 자동 연결
- PR 생성 시 Jira 이슈에 PR 링크 자동 표시
- PR merge 시 이슈 상태 자동 변경 가능

## Jira와 Github 연결 방법
1. Jira 프로젝트 생성 -> 이 때 생성하는 키가 이슈 번호가 됨 (예: `FLOW-7`)
2. Jira에서 GitHub for Jira 앱 설치 후 Github 조직 연결
3. Github 조직에 Atlassian 앱 설치
4. GitHub Repository → Settings → Secrets and variables → Actions에 아래 시크릿 등록  
   -> `JIRA_API_TOKEN`, `JIRA_BASE_URL`, `JIRA_USER_EMAIL`
5. `.github/workflows` 디렉토리에 Jira 연동 GitHub Actions yml 파일 생성

## Jira와 GitHub 자동화 흐름
위의 작업을 수행하여 GitHub Actions 자동화가 설정된 경우
1. GitHub에서 Issue 생성 (제목 또는 본문에 Epic 키와 번호를 기입)  
2. GitHub Actions가 실행되어 Jira Task 자동 생성
3. 생성된 Jira Task를 Epic에 연결
4. Jira 이슈 기준으로 GitHub 브랜치를 생성하여 작업
5. GitHub Issue가 닫히면 Jira 이슈 상태가 자동으로 완료 처리됨
