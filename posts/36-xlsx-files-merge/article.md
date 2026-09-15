지점별로 받은 엑셀 파일을 한 장에 모을 때, 복사·붙여넣기보다 신경 쓰이는 것은 열 순서입니다. 서울 파일은 상품·수량인데 부산 파일은 수량·상품이면, 위치만 보고 붙였을 때 숫자와 이름이 뒤섞일 수 있습니다.

이번에는 **폴더 안의 XLSX 파일을 열 이름으로 맞춰 한 시트에 합치고, 각 행에 원본 파일명을 남기는 파이썬 예제**를 실행해 봅니다. 같은 명령을 다시 실행해도 지정한 결과 파일은 입력에서 제외합니다.

## 어떤 합치기인가요?

이번 작업은 같은 종류의 표를 아래로 쌓는 것입니다. 고객번호를 기준으로 다른 표의 주소나 금액을 옆에 붙이는 작업이라면 [VLOOKUP 대신 pandas merge 사용하기](https://automate-lab.tistory.com/34)가 맞습니다. 원본이 CSV라면 [여러 CSV를 한 엑셀로 합치는 예제](https://automate-lab.tistory.com/16)를 참고하세요.

엑셀 안에서만 파일을 취합하고 끝낸다면 Power Query도 선택지입니다. 여기서는 결과를 다른 파이썬 작업과 연결하거나 같은 명령을 반복 실행해야 하는 경우를 다룹니다. 읽기와 쓰기는 openpyxl로 처리하며, 엑셀 프로그램을 직접 실행하지 않습니다.

## 준비: 예제 저장소와 실행 환경

Python 3.10 이상이 필요합니다. 아래 명령은 저장소를 내려받은 후 그 폴더 안에서 실행합니다. Git이 없다면 [GitHub 저장소](https://github.com/Rulrulmo/automate-lab)의 Code 메뉴에서 Download ZIP으로 내려받고 압축을 풀어도 됩니다.

```bash
git clone https://github.com/Rulrulmo/automate-lab.git
cd automate-lab
python -m venv .venv
```

Windows 명령 프롬프트에서는 다음과 같이 가상환경을 켭니다.

```text
.venv\Scripts\activate.bat
```

macOS·Linux에서는 다음 명령을 사용합니다. 시스템에 따라 가상환경 생성 명령의 python을 python3로 바꿔야 할 수 있습니다.

```bash
source .venv/bin/activate
```

가상환경을 켠 뒤 필요한 패키지를 설치합니다.

```bash
python -m pip install -e ".[xlsx]"
```

기존 저장소의 xlsx 설치 묶음을 그대로 사용합니다. 이 합치기 모듈 자체는 openpyxl로 동작합니다. 전체 구현과 샘플 생성기는 [이번 글의 GitHub 폴더](https://github.com/Rulrulmo/automate-lab/tree/main/posts/36-xlsx-files-merge)에 있습니다.

## 열 순서가 다른 샘플 두 개 만들기

회사 파일 대신 예제 데이터를 먼저 사용합니다.

```bash
python posts/36-xlsx-files-merge/make_sample.py
```

sample_xlsx 폴더에 다음 두 파일이 생깁니다. 각 파일의 시트 이름은 sales입니다.

**01_seoul.xlsx**

| product | qty |
| --- | --- |
| A | 3 |
| B | 2 |

**02_busan.xlsx**

| qty | product |
| --- | --- |
| 4 | A |
| 1 | C |

부산 파일의 열 순서를 일부러 뒤집었습니다. 샘플 생성기는 기존 파일이 있으면 덮어쓰지 않고 중단합니다. 두 번째부터는 샘플 생성 과정을 생략하세요.

## 실행: 엑셀 여러 개를 한 파일로 합치기

```bash
python -m automate_lab.xlsx_merge --input sample_xlsx --out sample_xlsx/merged.xlsx
```

실제 샘플 실행에서 확인한 결과입니다. 마지막 저장 경로는 실행한 컴퓨터에 따라 달라집니다.

```text
files=2 rows=4
  01_seoul.xlsx: 2 rows
  02_busan.xlsx: 2 rows
```

merged.xlsx의 merged 시트는 다음과 같습니다.

| product | qty | _source_file |
| --- | --- | --- |
| A | 3 | 01_seoul.xlsx |
| B | 2 | 01_seoul.xlsx |
| A | 4 | 02_busan.xlsx |
| C | 1 | 02_busan.xlsx |

열 이름으로 위치를 다시 계산했기 때문에 부산의 수량 4가 product 열로 들어가지 않습니다. _source_file로 필터를 걸면 어느 파일에서 들어온 행인지 확인할 수 있습니다.

기본값은 각 파일의 첫 번째 시트입니다. 첫 시트가 표지인 파일이라면, 모든 파일에 있는 시트 이름을 지정하세요.

```bash
python -m automate_lab.xlsx_merge --input sample_xlsx --out sample_xlsx/merged.xlsx --sheet sales
```

한 파일의 모든 시트를 자동으로 합치는 기능은 아닙니다. 시트를 CSV로 나눠야 한다면 [엑셀 시트별 CSV 저장](https://automate-lab.tistory.com/32)을 참고하세요.

## 코드의 핵심: 열 위치를 이름으로 다시 찾기

전체 구현은 [xlsx_merge.py](https://github.com/Rulrulmo/automate-lab/blob/main/src/automate_lab/xlsx_merge.py)에 있습니다. 검증을 통과한 뒤 각 파일에서 열 순서를 계산하는 부분은 다음과 같습니다.

```python
order = [names.index(name) for name in headers]
```

headers는 첫 파일의 열 이름이고, names는 지금 읽는 파일의 열 이름입니다. 샘플의 부산 파일에서는 order가 [1, 0]이 됩니다. 현재 행의 두 번째 값을 product로, 첫 번째 값을 qty로 가져오는 방식입니다. 각 행의 마지막에는 path.name을 붙입니다.

다른 스크립트에서도 같은 함수를 사용할 수 있습니다.

```python
from pathlib import Path
from automate_lab.xlsx_merge import merge_xlsx

summary = merge_xlsx(
    Path("sample_xlsx"),
    Path("sample_xlsx/merged.xlsx"),
    sheet="sales",
)
print(summary["rows_by_file"])
```

## 재실행할 때 결과가 두 배가 되지 않게

입력 폴더 안에 결과 파일을 저장하면, 다음 실행에서 그 파일까지 다시 읽기 쉽습니다. 예제는 --out으로 지정한 파일의 실제 경로를 비교해 입력에서 제외합니다. ~$로 시작하는 엑셀 잠금 파일도 제외합니다.

같은 명령을 다시 실행하면 원본 두 개를 다시 읽고 결과 파일을 교체합니다. 기존 결과 뒤에 계속 추가하는 방식이 아닙니다. 다만 merged_backup.xlsx처럼 다른 이름으로 복사한 결과를 입력 폴더에 넣으면 입력으로 취급됩니다. 실무에서는 입력과 출력 폴더를 나누는 편이 관리하기 쉽습니다.

중복 데이터 행을 자동 삭제하지도 않습니다. 상품과 수량이 같아도 서로 다른 정상 거래일 수 있으므로, 거래번호 같은 기준을 정한 뒤 별도 처리해야 합니다.

## 오류가 나면 확인할 것

| 메시지 | 확인할 내용 |
| --- | --- |
| No input .xlsx files found | 입력 폴더 바로 아래에 XLSX가 있는지 확인합니다. 하위 폴더와 XLS는 읽지 않습니다. |
| header mismatch | 파일마다 열 이름이 같은지 봅니다. 수량과 판매수량은 다른 이름입니다. |
| duplicate or reserved header | 중복 열 이름 또는 예약 이름 _source_file을 수정합니다. |
| headers must be nonempty text | 1행을 헤더로 사용합니다. 빈 헤더, 숫자 헤더, 표 위의 제목 행을 확인합니다. |
| missing sheet | --sheet로 지정한 시트가 모든 파일에 있는지 확인합니다. |
| formula found | 수식이 있습니다. 원본의 복사본에서 수식을 값으로 내보낸 뒤 합칩니다. |
| Excel error found | 원본에 #DIV/0! 같은 오류 셀이 있습니다. 먼저 오류를 수정합니다. |
| Permission denied | 결과 파일을 엑셀에서 열어 놓았는지, 저장 폴더에 쓰기 권한이 있는지 확인합니다. |

헤더의 앞뒤 공백은 제거하지만 이름을 추측해 바꾸지는 않습니다. 데이터 중간에 반복된 제목 행이 들어가면 일반 데이터로 취급하므로 입력을 정리해야 합니다. 수식은 자동 계산하지 않으며, 계산된 값이 오래됐을 가능성 때문에 이 예제에서는 수식 입력 자체를 중단합니다.

## 검증 범위와 제한

이번 예제는 Python 3.14.3, openpyxl 3.1.5에서 테스트 10개를 통과했습니다. 열 재정렬, 원본 파일 추적, 반복 실행, 헤더 오류, 시트 지정, 빈 데이터, 수식·오류 셀 차단, 수식처럼 보이는 문자열 보존을 확인했습니다.

```bash
python -m pip install -e ".[xlsx,testllm]"
python -m pytest -q tests/test_xlsx_merge.py
```

원본 파일은 수정하지 않습니다. 입력 검증을 마친 뒤 임시 파일로 저장하고 결과를 교체하므로, 검증 실패 시 이전 결과가 유지됩니다.

셀 서식·차트·병합 셀·매크로·암호화 파일은 지원 대상이 아닙니다. 텍스트로 저장된 001은 유지하지만, 숫자 1을 표시 형식으로 001처럼 보이게 만든 셀은 그 표시 형식까지 복사하지 않습니다. 모든 데이터 행을 메모리에 모으므로 대용량 파일은 별도 처리가 필요합니다.

먼저 샘플 4행이 위 표처럼 나오는지 확인한 뒤, 같은 구조의 실무 파일 복사본으로 적용해 보세요. 합친 뒤에는 파일별 행 수와 _source_file을 확인하는 습관이 취합 누락을 찾는 데 도움이 됩니다.

참고: [openpyxl 공식 튜토리얼](https://openpyxl.readthedocs.io/en/stable/tutorial.html)
