# 윈도우 작업 스케줄러로 파이썬 매일 자동 실행, 경로·UTF-8 함정 피하기

- 블로그: https://automate-lab.tistory.com/24
- 재사용 모듈: `automate_lab.scheduled` (UTF-8 강제 + 파일 로그 래퍼)

## Task Scheduler Action 예시

| 항목 | 값 |
| --- | --- |
| Program | `C:\...\.venv\Scripts\python.exe` (절대 경로) |
| Arguments | `C:\...\posts\24-windows-task-scheduler\run_daily.py` |
| Start in | 프로젝트 루트 절대 경로 |

배치 래퍼:

```bat
@echo off
set PYTHONUTF8=1
"C:\Users\you\projects\automate-lab\.venv\Scripts\python.exe" ^
  "C:\Users\you\projects\automate-lab\posts\24-windows-task-scheduler\run_daily.py" ^
  >> "C:\Users\you\projects\automate-lab\logs\run.log" 2>&1
```

## 로컬 확인

```bash
python run_daily.py
echo %ERRORLEVEL%   # Windows — 0 이어야 함
```

체크리스트·함정은 블로그 본문 참고. 실제 매일 돌릴 작업은 `run_daily.py`의 `job()`만 바꾸면 됨.
