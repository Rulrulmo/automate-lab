다운로드 폴더에 보고서.pdf, 보고서_최종.pdf, 보고서_최종(1).pdf가 쌓이면 이름만 보고 같은 파일인지 판단하기 어렵습니다. 다른 이름으로 저장한 복사본도 있고, 이름은 비슷하지만 내용이 바뀐 파일도 있기 때문입니다.

이번에는 **파일 크기와 SHA-256을 비교해 중복 후보를 찾고, 검토할 목록을 CSV로 저장하는 파이썬 예제**를 실행합니다. 파일 삭제 기능은 넣지 않았습니다. 어느 사본을 남길지는 경로와 업무 용도를 확인한 뒤 결정해야 합니다.

## 파일 이름보다 내용을 비교하는 이유

이름과 확장자가 달라도 실제 바이트가 같을 수 있습니다. 반대로 크기가 같다는 이유만으로 같은 파일이라고 판단할 수도 없습니다. 예제는 먼저 크기로 묶고, 같은 크기의 파일이 두 개 이상 있을 때만 SHA-256을 계산합니다.

SHA-256은 파일 내용을 일정한 길이의 값으로 요약하는 해시입니다. 내용이 바뀌었는지 비교할 때 유용합니다. 다만 같은 해시가 나온 목록은 여기서 중복 후보라고 부릅니다. 별도 바이트 단위 대조까지 수행한 결과는 아닙니다.

폴더를 확장자별로 나누는 작업은 [다운로드 폴더 자동 분류](https://automate-lab.tistory.com/22), PDF를 하나로 합치는 작업은 [PDF 순서 지정 병합](https://automate-lab.tistory.com/26)을 참고하세요. 이번 글은 정리 전에 같은 내용의 사본을 찾는 단계입니다.

## 설치: Python 표준 라이브러리로 실행

Python 3.10 이상이 필요합니다. 실행 모듈은 pathlib, hashlib, csv 등 표준 라이브러리만 사용합니다. 아래는 예제 저장소를 처음 내려받는 경우입니다. 이미 저장소가 있다면 변경 사항을 보존하면서 최신 코드를 받아 사용하세요.

```bash
git clone https://github.com/Rulrulmo/automate-lab.git
cd automate-lab
python -m venv .venv
```

Windows 명령 프롬프트에서는 다음 명령으로 가상환경을 켭니다.

```text
.venv\Scripts\activate.bat
```

macOS·Linux에서는 다음 명령을 사용합니다. 환경에 따라 가상환경 생성 명령의 python을 python3로 바꿔야 합니다.

```bash
source .venv/bin/activate
python -m pip install -e .
```

Windows에서도 가상환경을 켠 다음 python -m pip install -e .를 실행합니다. Git이 없다면 [저장소](https://github.com/Rulrulmo/automate-lab)의 Code 메뉴에서 Download ZIP을 선택해 압축을 풀어도 됩니다.

## 샘플 세 개로 먼저 확인하기

[이번 글의 예제 폴더](https://github.com/Rulrulmo/automate-lab/tree/main/posts/37-duplicate-files-report)에 샘플 생성기와 실행 설명을 넣었습니다. 저장소 루트에서 실행하세요.

```bash
python posts/37-duplicate-files-report/make_sample.py
```

duplicate_sample 폴더에 다음 파일이 생깁니다. 표의 내용 뒤에는 줄바꿈 한 개가 들어갑니다.

| 파일 | 내용 | 크기 |
| --- | --- | --- |
| report.txt | monthly report | 15바이트 |
| archive/report_copy.txt | monthly report | 15바이트 |
| different.txt | another report | 15바이트 |

세 파일의 크기는 같습니다. 첫 번째와 두 번째만 내용까지 같으므로, 크기 비교만으로 모두 중복이라고 처리하면 안 됩니다. 샘플 생성기는 기존 폴더가 있으면 중단하므로 두 번째 실행부터는 이 단계를 생략하세요.

## 실행: 하위 폴더까지 비교하고 CSV 저장

```bash
python -m automate_lab.duplicate_files --input duplicate_sample --out duplicates.csv
```

실제 샘플 실행 결과입니다.

```text
groups=1 candidate_files=2
report=duplicates.csv
```

duplicates.csv에는 group, size_bytes, sha256, relative_path 열이 생깁니다. 핵심 결과를 줄이면 다음과 같습니다.

| group | size_bytes | relative_path |
| --- | --- | --- |
| 1 | 15 | archive/report_copy.txt |
| 1 | 15 | report.txt |

different.txt는 같은 15바이트라도 내용이 달라 목록에 나오지 않습니다. CSV는 한글 경로를 엑셀에서 확인하기 쉽도록 UTF-8 BOM을 포함해 저장합니다.

입력 폴더는 읽기만 합니다. 보고서는 입력 폴더 밖에 저장해야 하며, 같은 이름의 보고서가 있으면 덮어쓰지 않고 중단합니다. 재실행할 때는 새 출력 이름을 사용하세요.

```bash
python -m automate_lab.duplicate_files --input duplicate_sample --out duplicates-02.csv
```

## 코드의 핵심: 큰 파일도 나눠 읽기

전체 코드는 [duplicate_files.py](https://github.com/Rulrulmo/automate-lab/blob/main/src/automate_lab/duplicate_files.py)에 있습니다. 해시 계산의 핵심은 아래와 같습니다.

```python
digest = hashlib.sha256()
with path.open("rb") as stream:
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(block)
```

파일 전체를 한 번에 메모리에 올리지 않고 1MiB씩 읽습니다. 최종 구현은 이 앞뒤에 파일 크기·수정 시각 등의 변경 검사도 붙입니다. 크기가 겹치지 않는 파일은 내용까지 읽지 않습니다. 다만 같은 크기의 파일이 많다면 그 파일들은 끝까지 읽어야 하므로, 대용량 폴더에서는 시간이 걸릴 수 있습니다.

다른 파이썬 작업에서는 함수로 호출할 수 있습니다.

```python
from pathlib import Path
from automate_lab.duplicate_files import find_duplicates

groups = find_duplicates(Path("duplicate_sample"))
for group in groups:
    print(group["size_bytes"], group["paths"])
```

## 중복 사진과 PDF에도 사용할 수 있나요?

완전히 같은 바이트의 복사본을 찾는 용도로는 사용할 수 있습니다. 하지만 사진을 다시 압축하거나 메타데이터를 바꾸면 해시가 달라질 수 있습니다. 같은 장면의 사진을 찾는 이미지 유사도 검색은 아닙니다.

PDF도 화면에 보이는 내용이 같더라도 내부 정보가 다르면 별개로 나올 수 있습니다. 압축파일 내부 문서, 문장 유사도, 엑셀 셀 값만 따로 비교하지 않습니다. 파일 이름이나 수정 시각이 다르다는 이유만으로 후보에서 빼지는 않습니다.

## 오류와 결과 해석

| 상황 | 확인할 내용 |
| --- | --- |
| groups=0 | 이번 검색 범위에 같은 크기·해시의 후보 그룹이 없다는 뜻입니다. 숨김 파일은 포함하지만 링크는 별도로 처리합니다. |
| Report already exists | 기존 CSV를 덮어쓰지 않습니다. 새 보고서 이름을 지정하세요. |
| Write the CSV outside the input folder | 입력 폴더 안의 파일을 보고서로 덮거나 다음 검색에 섞지 않도록 제한합니다. |
| Permission denied | 읽을 수 없는 파일이나 폴더가 있습니다. 검색 범위를 조정하고 접근 권한을 확인하세요. |
| File changed | 읽는 동안 파일 정보가 바뀌었습니다. 다운로드·동기화·편집이 끝난 뒤 다시 실행하세요. |

심볼릭 링크는 따라가지 않습니다. 여러 경로가 같은 실제 파일을 가리키는 하드 링크는 한 번만 계산합니다. 빈 파일도 서로 같은 후보로 잡힐 수 있습니다. 따라서 후보 크기를 단순 합산해 회수 가능한 디스크 공간이라고 해석하면 안 됩니다.

CSV 경로가 =, +, -, @ 등으로 시작하면 앞에 작은따옴표를 붙여 스프레드시트의 수식 해석을 줄입니다. 이 경우 표시용 경로와 실제 이름에 차이가 있으므로, CSV를 그대로 삭제 명령에 넘기면 안 됩니다.

## 실제 검증한 범위

Python 3.14.3에서 새 테스트 9개가 통과했습니다. 이름이 다른 복사본, 크기만 같은 다른 내용, 빈 파일, 링크 제외, 파일 변경 감지, CSV 출력, 기존 파일 보호, 읽기 오류 중단을 확인했습니다. 이전 엑셀 합치기 테스트까지 합쳐 19개가 통과했습니다.

```bash
python -m pip install -e ".[testllm]"
python -m pytest -q tests/test_duplicate_files.py
```

이 예제는 파일 잠금이나 파일시스템 스냅샷을 만들지 않습니다. 작업 도중 파일이 추가·삭제되거나 동기화되는 폴더의 전체 일관성을 보장하지 않으므로, 안정된 로컬 폴더에서 실행하세요. 읽기 오류는 중단하고, 보고서 쓰기 도중 디스크 오류가 발생하면 부분 CSV가 남을 수 있으므로 종료 코드와 완료 메시지를 확인해야 합니다.

먼저 작은 폴더로 후보 목록을 만든 뒤, 같은 그룹의 경로와 실제 용도를 확인하세요. 자동 삭제를 붙이기 전에 목록을 검토하는 단계만 자동화해도 사본 찾기에 드는 반복 작업을 줄일 수 있습니다.

참고: [Python hashlib 공식 문서](https://docs.python.org/3/library/hashlib.html)
