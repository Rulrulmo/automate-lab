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

## 모듈

| 패키지 | 하는 일 | posts |
| --- | --- | --- |
| `automate_lab.retry` | HTTP 재시도 (지수 백오프 + 지터, 429·5xx만) | `20-retry-wrapper` |
| `automate_lab.watch` | 다운로드 폴더 CSV 감시 | `18-csv-watch` |
| `automate_lab.structured` | Structured Outputs 로그 분류 | `21-structured-outputs` |

## 설치

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[watch,structured]"
```

## 레이아웃

```
src/automate_lab/          # 재사용 모듈
posts/
  18-csv-watch/
  20-retry-wrapper/
  21-structured-outputs/
```

새 글: `posts/NN-slug/README.md`에 티스토리 URL을 넣고, 재사용되면 `src/`에도 올린 뒤 위 표를 갱신합니다.

## 관련

- 블로그: https://automate-lab.tistory.com
- GitHub: [@Rulrulmo](https://github.com/Rulrulmo)
