# automate-lab

[실무 자동화 공방](https://automate-lab.tistory.com) 글에서 뽑은 **재사용 자동화 조각** 모음입니다.

- **모듈** (`src/automate_lab/`): `import`해서 쓰는 코드
- **글별 폴더** (`posts/NN-slug/`): 그 글의 예제 + README(티스토리 링크) — 블로그·X에 붙일 경로

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

## 모듈

| 패키지 | 하는 일 | posts |
| --- | --- | --- |
| `automate_lab.retry` | HTTP 재시도 (지수 백오프 + 지터, 429·5xx만) | `20-retry-wrapper` |
| `automate_lab.watch` | 다운로드 폴더 CSV 감시 | `18-csv-watch` |
| `automate_lab.structured` | Structured Outputs 로그 분류 | `21-structured-outputs` |
| `automate_lab.sort_downloads` | 확장자·키워드로 Downloads 정리 | `22-download-sort` |
| `automate_lab.header_map` | 동의어 + LLM 헤더 표준화 | `23-csv-header-map` |
| `automate_lab.scheduled` | 스케줄 잡 UTF-8 + 파일 로그 | `24-windows-task-scheduler` |
| `automate_lab.receipts` | 영수증 OCR→LLM→엑셀 | `25-receipt-ocr` |

## 설치

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[watch,structured,receipts]"
```

## 레이아웃

```
src/automate_lab/
posts/
  18-csv-watch/
  20-retry-wrapper/
  21-structured-outputs/
  22-download-sort/
  23-csv-header-map/
  24-windows-task-scheduler/
  25-receipt-ocr/
```

새 글: `posts/NN-slug/README.md`에 티스토리 URL을 넣고, 재사용되면 `src/`에도 올린 뒤 위 표를 갱신합니다.

## 관련

- 블로그: https://automate-lab.tistory.com
- GitHub: [@Rulrulmo](https://github.com/Rulrulmo)
