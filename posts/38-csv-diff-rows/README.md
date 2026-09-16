# 두 CSV 차이 찾기, pandas로 추가·삭제·변경 행 비교하기

- 블로그: https://automate-lab.tistory.com/38
- 재사용 모듈: `automate_lab.csv_diff`

## 실행

```bash
pip install -e ".[xlsx]"
python csv_diff_rows.py --left in/yesterday.csv --right in/today.csv --keys id --outdir out/diff --excel
```

키 기준 `added` / `removed` / `changed`. `dtype=str` + strip. 중복 키는 경고 후 first만 비교.
