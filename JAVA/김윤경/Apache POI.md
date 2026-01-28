# Apache POI

- 자바로 엑셀(.xlsx), 워드(.docx), 파워포인트(.pptx) 같은 오피스 파일을 만들고 읽는 라이브러리

### Apache POI로 할 수 있는 기능
- 엑셀 파일 생성
  - 새로운 .xlsx 파일 만들기
  - 시트 여러 개 생성
- 셀에 값 쓰기
  - 문자열
  - 숫자(BigDecimal 금액)
  - 날짜
- 엑셀 스타일 꾸미기
  - 폰트 굵게
  - 배경색
  - 정렬
  - 금액 포맷(₩, 콤마)
- 함수 넣기
  - SUM
  - AVERAGE
  - 자동 합계
- 대량 데이터 출력
  - 정산 로그 전체 덤프
 
### POI정산 엑셀을 만드는 흐름 (Spring)

1. 정산 로그/정산 항목 리스트 조회 (List<SettlementItem>)

2. Workbook 생성 (XSSFWorkbook)

3. Sheet 만들고 헤더 행 작성

4. 데이터 행 반복 작성

5. HTTP 응답으로 내려주기 <br>
   Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet <br>
   Content-Disposition: attachment; filename="settlement_2026-01.xlsx"

### 예시
```
Workbook wb = new XSSFWorkbook();
Sheet sheet = wb.createSheet("정산");

Row row = sheet.createRow(0);
row.createCell(0).setCellValue("매출");
row.createCell(1).setCellValue(100000);

FileOutputStream out = new FileOutputStream("settlement.xlsx");
wb.write(out);
wb.close();

```
-> 엑셀 파일 생성.

- settlement를 적용해서 예시를 생각해보면

```
@GetMapping("/settlements/{id}/excel")
public void downloadSettlementExcel(@PathVariable Long id, HttpServletResponse response) throws IOException {
    List<SettlementItem> items = settlementService.findItems(id);

    Workbook wb = new XSSFWorkbook();
    Sheet sheet = wb.createSheet("settlement_items");

    // 헤더
    String[] headers = {"날짜", "유형", "가맹점", "상품", "수량", "단가", "금액", "유통기한", "손실사유"};
    Row headerRow = sheet.createRow(0);
    for (int i = 0; i < headers.length; i++) headerRow.createCell(i).setCellValue(headers[i]);

    // 데이터
    int r = 1;
    for (SettlementItem it : items) {
        Row row = sheet.createRow(r++);
        row.createCell(0).setCellValue(it.getOccurredAt().toString());
        row.createCell(1).setCellValue(it.getType().name());
        row.createCell(2).setCellValue(it.getStoreName());
        row.createCell(3).setCellValue(it.getProductName());
        row.createCell(4).setCellValue(it.getQuantity());
        row.createCell(5).setCellValue(it.getUnitPrice().doubleValue());
        row.createCell(6).setCellValue(it.getAmount().doubleValue());
        row.createCell(7).setCellValue(it.getExpiryDate() == null ? "" : it.getExpiryDate().toString());
        row.createCell(8).setCellValue(it.getLossReason() == null ? "" : it.getLossReason().name());
    }

    // 응답
    response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
    response.setHeader("Content-Disposition", "attachment; filename=\"settlement_" + id + ".xlsx\"");
    wb.write(response.getOutputStream());
    wb.close();
}
```
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/04e68be3-5c12-4a17-9796-71cd4a07902a" />






-> 하지만 이 경우 숫자/돈은 double 대신 BigDecimal로 다루되, 엑셀로 쓸 때만 doubleValue()로 변환해야한다.

- 왜?
  - 돈 계산, 특히 큰 금액을 계산 할 때는 BigDecimal을 써야 정확하다.
  - 근데 엑셀 셀은 내부적으로 '숫자(double)' 기반이다.
  <br>
  
  ```
  cell.setCellValue(???)
  ```
- 이 메서드가 숫자 타입으로 받는 게 : double, Date, String -> BigDecimal을 직접 못 받음

- 그래서 계산은 'BigDecimal', 출력만 'double'로 한다.
- 정산 로직에서는
  ```
  BigDecimal amount;
  BigDecimal unitPrice;
  ```
  으로 정확하게 계산하고 저장하고

- 엑셀으로
  ```
  cell.setCellValue(amount.doubleValue());
  ```
  으로 표시용 변환을 한다.

- double로 바꾸면 오차가 챙기지 않을까?
  - 아주 미세한 오차는 생길 수 있다.
  - 하지만 이미 BigDecimal로 계산이 끝났고 엑셀은 “표시” 용도라 정산금액이 1원 단위까지 틀일 일은 거의 없다.






