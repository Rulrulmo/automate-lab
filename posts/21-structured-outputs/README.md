# LLM 응답을 JSON 스키마에 고정하기, Structured Outputs로 분류 자동화

- 블로그: https://automate-lab.tistory.com/21
- 재사용 모듈: `automate_lab.structured` (`src/automate_lab/structured.py`)

## 실행

```bash
pip install -e ".[structured]"
export OPENAI_API_KEY=...
# optional: export OPENAI_MODEL=gpt-4.1-mini
python run_classify.py
```

스키마는 모양만 보장합니다. 팀 정책은 `apply_policy`에서 한 번 더 덮습니다.
