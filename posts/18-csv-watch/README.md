# 다운로드 폴더에 새 CSV가 오면 파이썬이 바로 처리하기

- 블로그: https://automate-lab.tistory.com/18
- 재사용 모듈: `automate_lab.watch` (`src/automate_lab/watch.py`)

## 실행

```bash
pip install -e ".[watch]"
python -m automate_lab.watch --watch ~/Downloads --done ~/Downloads/processed_csv
```

또는 이 폴더의 스크립트:

```bash
pip install watchdog
python watch_downloads.py --watch ~/Downloads --done ~/Downloads/processed_csv
```

`process_csv`만 업무 로직으로 바꾸면 됩니다. 크기 안정화 후 처리하는 패턴은 글과 동일합니다.
