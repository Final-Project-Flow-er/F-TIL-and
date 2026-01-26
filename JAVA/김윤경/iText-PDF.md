# Pdf 생성 iText
- iText는 자바(Java) 및 .NET 환경에서 프로그래밍 방식으로 PDF 문서를 손쉽게 생성, 수정, 조작할 수 있는 강력한 라이브러리
- Maven/Gradle 의존성을 추가하여 간단한 텍스트부터 HTML, 이미지, 테이블이 포함된 복잡한 PDF를 생성할 수 있으며,
  <br> PDF 표준을 준수하여 대규모 문서 처리에도 적합하다. 
 
```
// PDF Writer와 Document 객체 생성
PdfWriter writer = new PdfWriter("example.pdf");
PdfDocument pdf = new PdfDocument(writer);
Document document = new Document(pdf);

// 문서에 내용 추가
document.add(new Paragraph("Hello, World!"));

// 문서 닫기
document.close();
```

- 예시
```
PdfWriter writer = new PdfWriter(outputStream);
PdfDocument pdf = new PdfDocument(writer);
Document document = new Document(pdf);
```

```
Table table = new Table(4); // 컬럼 수

table.addCell("가맹점");
table.addCell("정산일");
table.addCell("총 금액");
table.addCell("주문 건수");

for (Settlement s : settlements) {
    table.addCell(s.getStoreName());
    table.addCell(s.getDate().toString());
    table.addCell(s.getTotalAmount().toString());
    table.addCell(String.valueOf(s.getOrderCount()));
}

document.add(table);
document.close();
```

- 한글 폰트
```
PdfFont font = PdfFontFactory.createFont(
    "fonts/NotoSansKR-Regular.ttf",
    PdfEncodings.IDENTITY_H,
    true
);

document.setFont(font);
```

# MinIO

- AWS S3랑 유사한 사설 파일 저장소이다.
- PDF, 이미지, 엑셀, 첨부파일 등을 DB에 저장하지 않고 MinIO에 저장하고 DB에는 '파일 경로(URL)'만 저장하는 구조이다.
- 정산 PDF를 로컬에 두면 서버를 재시작 할 때 위험하고 확장이 어렵다 -> MinIO에 저장하는게 실무적이다.


## 버킷 관리, 버킷 생성
- 버킷 : 폴더와 유사한 개념이다. PDF 저장소를 만드는 것과 동일하다.

```
boolean exists = minioClient.bucketExists(
    BucketExistsArgs.builder().bucket(bucketName).build()
);

if (!exists) {
    minioClient.makeBucket(
        MakeBucketArgs.builder().bucket(bucketName).build()
    );
}
```

## 파일 업로드 : putObject()
- putObject()에서 PDF 저장됨

```
minioClient.putObject(
    PutObjectArgs.builder()
        .bucket(bucketName)
        .object("settlements/daily_2026-01-20.pdf") // 저장 경로
        .stream(inputStream, size, -1)
        .contentType("application/pdf")
        .build()
);
```
- -> MinIO 서버에 PDF가 저장됨





