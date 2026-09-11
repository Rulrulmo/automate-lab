# 스크립트 결과를 메일로 받기, 파이썬 smtplib·Gmail 앱 비밀번호

- 블로그: https://automate-lab.tistory.com/29
- 재사용 모듈: `automate_lab.mail_report` (표준 라이브러리만)

## 실행

```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=you@gmail.com
export SMTP_PASS='앱비밀번호'   # 커밋 금지
export MAIL_TO=you@gmail.com
python send_report_mail.py
```

제목 `[OK]`/`[FAIL]`, 본문 요약, 선택 첨부(2MB 상한). 비밀번호는 로그에 남기지 않음.
