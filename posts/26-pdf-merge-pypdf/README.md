# 여러 PDF 하나로 합치기, 파이썬 pypdf로 순서 지정 병합

- 블로그: https://automate-lab.tistory.com/26
- 재사용 모듈: `automate_lab.pdf_merge`

## 설치·실행

```bash
pip install -e ".[pdf]"
python merge_pdfs.py --src inbox_pdfs --out out/merged.pdf --dry-run
python merge_pdfs.py --src inbox_pdfs --out out/merged.pdf --order cover.pdf,chapter1.pdf,chapter2.pdf
```

순서는 `--order` 콤마 리스트 또는 `--order-file` 한 줄 한 파일. 암호·빈·손상 PDF는 스킵하고 로그.
