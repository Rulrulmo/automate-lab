# API가 가끔 죽어도 스크립트가 이어지게, 파이썬 재시도 래퍼

- 블로그: https://automate-lab.tistory.com/20
- 재사용 모듈: `automate_lab.retry` (`src/automate_lab/retry.py`)

## 사용

```python
from automate_lab.retry import urllib_request_with_retry, post_json

status, body = urllib_request_with_retry("https://httpbin.org/status/200")
```

Slack 웹훅 예제 (환경 변수 `SLACK_WEBHOOK_URL` 필요):

```bash
python slack_with_retry.py
```

재시도 대상: 429·500·502·503·504·타임아웃. 그 외 4xx는 즉시 실패.
