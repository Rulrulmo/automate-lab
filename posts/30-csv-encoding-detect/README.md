# 한글 CSV가 깨질 때, 파이썬으로 CP949·UTF-8 자동 판별해 읽기

- 블로그: https://automate-lab.tistory.com/30
- 재사용 모듈: `automate_lab.csv_encoding`

## 실행

```bash
pip install -e ".[csv]"   # pandas 선택
python read_csv_auto.py sample.csv
```

후보 순서: `utf-8-sig` → `utf-8` → `cp949` → `euc-kr`. 성공한 encoding 이름을 함께 반환.
