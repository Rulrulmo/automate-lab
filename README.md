# automate-lab

[실무 자동화 공방](https://automate-lab.tistory.com) 글에서 뽑은 **재사용 자동화 조각** 모음입니다.

글은 how-to, 이 저장소는 복붙 가능한 모듈·예제입니다. X 배포나 블로그에서 코드 링크가 필요할 때 여기를 가리키면 됩니다.

## 모듈

| 패키지 | 하는 일 | 블로그 |
| --- | --- | --- |
| `automate_lab.retry` | HTTP 재시도 (지수 백오프 + 지터, 429·5xx만) | [글 /20](https://automate-lab.tistory.com/20) |
| `automate_lab.watch` | 다운로드 폴더 CSV 감시 (크기 안정화 후 처리) | [글 /18](https://automate-lab.tistory.com/18) |
| `automate_lab.structured` | Structured Outputs 로그 분류 | [글 /21](https://automate-lab.tistory.com/21) |

## 설치

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[watch,structured]"
```

- 재시도만: 표준 라이브러리만 쓰므로 추가 설치 없음 (`pip install -e .`)
- CSV 감시: `watchdog`
- Structured Outputs: `openai`, `pydantic`

## 빠른 사용

```python
from automate_lab.retry import urllib_request_with_retry

status, body = urllib_request_with_retry("https://httpbin.org/status/200")
```

```bash
# CSV 감시 예제
python -m automate_lab.watch --watch ~/Downloads --done ~/Downloads/processed_csv
```

```bash
# 로그 분류 예제 (OPENAI_API_KEY 필요)
export OPENAI_API_KEY=...
python examples/run_classify.py
```

## 레이아웃

```
src/automate_lab/
  retry.py          # call_with_retry, urllib_request_with_retry
  watch.py          # CSV 폴더 감시 CLI
  structured.py     # LogClassification + classify_line
examples/
  slack_with_retry.py
  run_classify.py
```

새 글에서 나온 조각은 모듈로 옮기고, README 표에 블로그 URL을 추가합니다.

## 관련

- 블로그: https://automate-lab.tistory.com
- 작성: [자동화공방](https://automate-lab.tistory.com) / GitHub [@Rulrulmo](https://github.com/Rulrulmo)
