# 파이썬 중복 파일 찾기: 내용 비교 후 CSV 저장

재사용 모듈: `automate_lab.duplicate_files`.
블로그 링크는 발행 확인 후 추가합니다.

저장소 루트에서 실행합니다. Python 3.10 이상, 실행 모듈은 표준 라이브러리만 사용합니다.

```bash
python -m pip install -e .
python posts/37-duplicate-files-report/make_sample.py
python -m automate_lab.duplicate_files --input duplicate_sample --out duplicates.csv
```

예상: `groups=1 candidate_files=2`. `report.txt`와 `archive/report_copy.txt`가
같은 15바이트 SHA-256 후보 그룹입니다. `different.txt`는 같은 크기지만 내용이 달라 제외됩니다.

- 입력 폴더와 하위 폴더를 읽고 크기가 같은 파일들에만 SHA-256을 계산합니다.
- 삭제 기능은 없습니다. 같은 해시를 가진 후보 목록을 CSV로 작성합니다.
- CSV는 입력 폴더 밖에 저장해야 하며 기존 파일을 덮어쓰지 않습니다.
- 읽기/폴더 접근 오류가 발생하면 중단합니다. 파일을 읽는 전후의 메타데이터 변경도 검사합니다.
- 심볼릭 링크는 건너뛰고 같은 실제 파일의 하드 링크는 한 번만 계산합니다.
- 비어 있는 파일도 후보입니다. 숨김 파일은 검색 대상에 포함됩니다.
- 실행 중 변경되는 폴더의 일관성을 보장하는 스냅샷이나 잠금 기능은 없습니다.
- 이미지 유사도, PDF의 보이는 내용, 압축파일 내부를 비교하지 않습니다.
- CSV의 relative_path가 =, +, -, @ 등으로 시작하면 Excel 수식 해석을 줄이기 위해 앞에 작은따옴표를 붙입니다.
- 출력 파일 작성 도중 디스크 오류가 나면 부분 CSV가 남을 수 있으므로 종료 코드와 완료 메시지를 확인하세요.

다시 실행하려면 `--out duplicates-02.csv`처럼 새 보고서 이름을 지정합니다.
샘플 생성기는 기존 폴더가 있으면 중단합니다.

```bash
python -m pip install -e ".[testllm]"
python -m pytest -q tests/test_duplicate_files.py
```

원리: [Python hashlib 공식 문서](https://docs.python.org/3/library/hashlib.html).
