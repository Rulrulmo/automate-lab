# automate-lab

[실무 자동화 공방](https://automate-lab.tistory.com) 글에서 뽑은 **재사용 자동화 조각** 모음입니다.

- **모듈** (`src/automate_lab/`): `import`해서 쓰는 코드
- **글별 폴더** (`posts/NN-slug/`): 그 글의 예제 + README(티스토리 링크)

## 글 ↔ 경로

| 글 | posts 경로 |
| --- | --- |
| [CSV 폴더 감시 /18](https://automate-lab.tistory.com/18) | [`posts/18-csv-watch`](posts/18-csv-watch/) |
| [HTTP 재시도 /20](https://automate-lab.tistory.com/20) | [`posts/20-retry-wrapper`](posts/20-retry-wrapper/) |
| [Structured Outputs /21](https://automate-lab.tistory.com/21) | [`posts/21-structured-outputs`](posts/21-structured-outputs/) |
| [다운로드 폴더 정리 /22](https://automate-lab.tistory.com/22) | [`posts/22-download-sort`](posts/22-download-sort/) |
| [CSV 헤더 LLM 매핑 /23](https://automate-lab.tistory.com/23) | [`posts/23-csv-header-map`](posts/23-csv-header-map/) |
| [윈도우 작업 스케줄러 /24](https://automate-lab.tistory.com/24) | [`posts/24-windows-task-scheduler`](posts/24-windows-task-scheduler/) |
| [영수증 OCR+LLM /25](https://automate-lab.tistory.com/25) | [`posts/25-receipt-ocr`](posts/25-receipt-ocr/) |
| [PDF 순서 병합 /26](https://automate-lab.tistory.com/26) | [`posts/26-pdf-merge-pypdf`](posts/26-pdf-merge-pypdf/) |
| [git diff 커밋 초안 /27](https://automate-lab.tistory.com/27) | [`posts/27-git-diff-commit-message`](posts/27-git-diff-commit-message/) |
| [watchdog CSV inbox /28](https://automate-lab.tistory.com/28) | [`posts/28-watchdog-csv-inbox`](posts/28-watchdog-csv-inbox/) |
| [SMTP 배치 리포트 /29](https://automate-lab.tistory.com/29) | [`posts/29-smtp-script-report`](posts/29-smtp-script-report/) |
| [CSV 인코딩 판별 /30](https://automate-lab.tistory.com/30) | [`posts/30-csv-encoding-detect`](posts/30-csv-encoding-detect/) |
| [git log 릴리스 노트 /31](https://automate-lab.tistory.com/31) | [`posts/31-git-log-release-notes`](posts/31-git-log-release-notes/) |
| [엑셀 시트→CSV /32](https://automate-lab.tistory.com/32) | [`posts/32-xlsx-sheets-to-csv`](posts/32-xlsx-sheets-to-csv/) |
| [pytest 실패 LLM 요약 /33](https://automate-lab.tistory.com/33) | [`posts/33-pytest-failure-llm-summary`](posts/33-pytest-failure-llm-summary/) |

## 모듈

| 패키지 | posts |
| --- | --- |
| `automate_lab.xlsx_split` | `32-xlsx-sheets-to-csv` |
| `automate_lab.pytest_summary` | `33-pytest-failure-llm-summary` |
| (기존 모듈 표는 README 상단 글↔경로와 동일) | |

## 설치

```bash
pip install -e ".[watch,structured,receipts,pdf,csv,xlsx,testllm]"
```

## 관련

- 블로그: https://automate-lab.tistory.com
- GitHub: [@Rulrulmo](https://github.com/Rulrulmo)
