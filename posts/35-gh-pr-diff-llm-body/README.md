# PR 본문 초안 만들기, gh pr diff만 LLM에 넘기기

- 블로그: https://automate-lab.tistory.com/35
- 재사용 모듈: `automate_lab.pr_body`
- 관련: [`posts/27-git-diff-commit-message`](../27-git-diff-commit-message/), [`posts/33-pytest-failure-llm-summary`](../33-pytest-failure-llm-summary/)

## 실행

```bash
pip install -e .
export OPENAI_API_KEY=...
# PR이 이미 있을 때
python draft_pr_body.py --pr 123
# 프롬프트만
python draft_pr_body.py --pr 123 --dry-run
```

`gh pr diff` mid만 최대 12_000자로 전달. 시크릿 패턴 경고 후 LLM. 초안은 사람이 확정.
