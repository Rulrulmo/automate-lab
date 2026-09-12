# 릴리스 노트 초안 만들기, git log만 LLM에 넘기기

- 블로그: https://automate-lab.tistory.com/31
- 재사용 모듈: `automate_lab.release_notes`
- 관련: [`posts/27-git-diff-commit-message`](../27-git-diff-commit-message/)

## 실행

```bash
# 프롬프트만 (네트워크 없음)
python git_log_for_notes.py --range 'v1.4.0..HEAD' --version 1.5.0

# LLM 초안까지
export OPENAI_API_KEY=...
python git_log_for_notes.py --range 'v1.4.0..HEAD' --version 1.5.0 --call-llm
```

git log oneline만 전달. 저장소 전체·diff 기본 업로드 없음. 초안은 사람이 확정.
