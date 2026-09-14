# 엑셀 VLOOKUP 대신 파이썬으로 조인하기, pandas merge

- 블로그: https://automate-lab.tistory.com/34
- 재사용 모듈: `automate_lab.table_merge`

## 실행

```bash
pip install -e ".[xlsx]"
python merge_tables.py --left in/orders.csv --right in/products.xlsx --on product_id --out out/merged.csv
```

기본 `how=left`, 키는 `dtype=str`로 읽어 `00123` 유지. `_merge`로 미매칭 확인.
