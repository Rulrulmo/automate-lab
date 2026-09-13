# 엑셀 여러 시트를 CSV로 쪼개기, pandas로 시트별 저장

- 블로그: https://automate-lab.tistory.com/32
- 재사용 모듈: `automate_lab.xlsx_split`

## 실행

```bash
pip install -e ".[xlsx]"
python split_xlsx_to_csv.py --src in/report.xlsx --out out/sheets
```

시트 이름을 안전한 파일명으로 바꾸고 `utf-8-sig` CSV로 저장. 빈 시트는 기본 스킵.
