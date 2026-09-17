# 로그에서 ERROR만 모아 CSV로 저장하기, 파이썬 pathlib

- 블로그: https://automate-lab.tistory.com/41
- 재사용 모듈: `automate_lab.log_errors` (표준 라이브러리만)

## 실행

```bash
pip install -e .
python log_error_to_csv.py --logs-dir logs --out out/errors.csv --date 20260917
python log_error_to_csv.py --file logs/app.log --out out/one.csv --max-msg 300
```

원본 로그는 읽기만. `ERROR`/`CRITICAL` 단어 경계 매칭. 인코딩 utf-8, 실패 시 replace.
