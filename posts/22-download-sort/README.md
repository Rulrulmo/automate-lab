# 다운로드 폴더 정리, 파이썬으로 확장자·키워드 규칙 자동 분류하기

- 블로그: https://automate-lab.tistory.com/22
- 재사용 모듈: `automate_lab.sort_downloads`

## 실행

```bash
pip install -e .
python sort_downloads.py --dry-run
python sort_downloads.py
```

기본: `~/Downloads` → `~/SortedDownloads`. 규칙은 스크립트 상단 `EXT_MAP` / `KEYWORD_RULES`.
