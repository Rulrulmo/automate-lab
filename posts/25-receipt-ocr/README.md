# OCR+LLM으로 영수증 금액 추출해 엑셀에 저장하기

- 블로그: https://automate-lab.tistory.com/25
- 재사용 모듈: `automate_lab.receipts`

## 설치

```bash
pip install -e ".[receipts]"
# Tesseract + kor/eng language packs must be on PATH for image OCR
export OPENAI_API_KEY=...
```

## 실행

```bash
mkdir -p inbox done failed
# put pdf/png/jpg into inbox/
python process_inbox.py --inbox inbox --xlsx receipts.xlsx
```

흐름: 텍스트 PDF는 pdfplumber → 부족하면 OCR → LLM JSON 스키마 → openpyxl append. `confidence < 0.7` 또는 amount 없으면 `review` 시트.
