# CSV 헤더가 제각각일 때 LLM으로 표준 컬럼 매핑하기

- 블로그: https://automate-lab.tistory.com/23
- 재사용 모듈: `automate_lab.header_map`

## 실행

```bash
pip install -e .
export OPENAI_API_KEY=...
python map_headers.py input.csv
```

사전(`SYNONYMS`)으로 먼저 맞추고, 남은 헤더만 LLM에 보냅니다. `unmapped`가 있으면 종료 코드 2 + `*.mapping.json` 검수 파일.
