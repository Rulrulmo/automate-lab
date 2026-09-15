# 파이썬으로 엑셀 파일 여러 개 합치기

열 순서가 달라도 이름으로 맞추고 `_source_file`에 원본 파일명을 남깁니다.
재사용 모듈: `automate_lab.xlsx_merge`.
블로그: https://automate-lab.tistory.com/36

## 실행 (저장소 루트에서)

```bash
python -m pip install -e ".[xlsx]"
python posts/36-xlsx-files-merge/make_sample.py
python -m automate_lab.xlsx_merge --input sample_xlsx --out sample_xlsx/merged.xlsx
```

첫 시트 대신 특정 시트만 읽으려면 `--sheet sales`를 추가합니다.
샘플 생성기는 기존 샘플을 덮어쓰지 않습니다. 두 번째부터는 합치기 명령만 실행하세요.

예상 출력: `files=2 rows=4`

| product | qty | _source_file |
| --- | --- | --- |
| A | 3 | 01_seoul.xlsx |
| B | 2 | 01_seoul.xlsx |
| A | 4 | 02_busan.xlsx |
| C | 1 | 02_busan.xlsx |

## 처리 규칙

- 폴더 바로 아래 XLSX만 파일명 순서로 읽습니다. 하위 폴더는 탐색하지 않습니다.
- 1행은 비어 있지 않은 고유한 텍스트 헤더여야 합니다. 앞뒤 공백만 제거합니다.
- 열 집합이 같으면 순서를 맞춥니다. 누락/추가 열, 중복 헤더는 오류로 중단합니다.
- `_source_file`은 예약 열 이름입니다. 원본에 있으면 중단합니다.
- 완전히 빈 행, `~$`로 시작하는 잠금 파일, 지정한 출력 파일은 제외합니다.
- 같은 출력 경로로 다시 실행하면 원본을 다시 합쳐 결과만 교체합니다.
- 입력에 수식이나 Excel 오류 셀이 있으면 중단합니다. 먼저 값으로 내보내세요.
- 문자열은 문자열로 저장합니다. 텍스트 `001`은 유지하지만 숫자 셀의 표시 형식 `000`은 보존하지 않습니다.
- 서식, 차트, 병합 셀, 매크로, XLS, 암호화 파일은 지원 대상이 아닙니다.
- 중복 데이터 행은 자동 삭제하지 않습니다. 같은 내용이라도 정상 거래일 수 있습니다.
- 모든 행을 메모리에 모으므로 대용량 처리에는 적합하지 않습니다.
- 입력 검증/저장 실패 시 기존 결과를 보존하도록 임시 파일 저장 후 교체합니다.

## 테스트

```bash
python -m pip install -e ".[xlsx,testllm]"
python -m pytest -q tests/test_xlsx_merge.py
```

관련 글: [CSV 합치기](https://automate-lab.tistory.com/16),
[시트별 CSV 분리](https://automate-lab.tistory.com/32),
[키 기준 조인](https://automate-lab.tistory.com/34).

공식 문서: [openpyxl tutorial](https://openpyxl.readthedocs.io/en/stable/tutorial.html).
