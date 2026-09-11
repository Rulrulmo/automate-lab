# 다운로드 폴더에 새 CSV가 오면 파이썬이 바로 처리하기, watchdog으로

- 블로그: https://automate-lab.tistory.com/28
- 관련: [`posts/18-csv-watch`](../18-csv-watch/) (초기 버전)
- 재사용 모듈: `automate_lab.csv_inbox`

## 실행

```bash
pip install -e ".[watch]"
# optional schema check with pandas:
pip install pandas

DRY_RUN=1 CSV_INBOX="$HOME/Downloads" python watch_csv_inbox.py
CSV_INBOX="$HOME/Downloads" python watch_csv_inbox.py
```

환경변수: `CSV_INBOX`, `CSV_DONE`, `CSV_QUARANTINE`, `DRY_RUN`, `STABLE_SEC`.
임시 확장자 스킵 + 크기 안정화 + DONE/quarantine 분리.
