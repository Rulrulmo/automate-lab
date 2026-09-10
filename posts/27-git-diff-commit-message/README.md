# git diff만 넘겨 LLM으로 커밋 메시지 초안 만들기

- 블로그: https://automate-lab.tistory.com/27
- 재사용 모듈: `automate_lab.commit_msg`

## 실행

```bash
pip install -e .
export OPENAI_API_KEY=...
git add -p
python commit_msg_draft.py --staged
# 초안을 읽고 사람이 git commit
```

`.env`·pem·lock 등 가드에 걸리면 exit 2/3. `git commit`은 하지 않음.
