# pytest 실패 로그를 LLM에 넘겨 원인 요약하기

- 블로그: https://automate-lab.tistory.com/33
- 재사용 모듈: `automate_lab.pytest_summary`

## 실행

```bash
pip install -e ".[testllm]"
export OPENAI_API_KEY=...
python summarize_pytest_failures.py
# or summarize an existing log:
python summarize_pytest_failures.py --log out/pytest.log --skip-run
```

실패 블록만 최대 8_000자로 잘라 LLM에 넘김. 통과면 모델 호출 없음.
