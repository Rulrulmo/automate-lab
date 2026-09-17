# 엑셀·CSV 중복 행 제거하기, pandas drop_duplicates로 키 기준 정리

- 블로그: https://automate-lab.tistory.com/40
- 재사용 모듈: `automate_lab.csv_dedupe`

## 실행

```bash
pip install -e ".[xlsx]"
python csv_drop_duplicates.py --input in/orders.csv --keys order_id,sku --keep first --outdir out/dedup --report
```

키 기준 `drop_duplicates`. `dtype=str` + strip. `--report`면 제거된 중복 행만 `duplicates_report.csv`.
