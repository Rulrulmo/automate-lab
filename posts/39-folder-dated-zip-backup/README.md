# 폴더를 날짜별 zip으로 백업하기, 파이썬 zipfile·pathlib

- 블로그: https://automate-lab.tistory.com/39
- 재사용 모듈: `automate_lab.folder_zip` (표준 라이브러리만)

## 실행

```bash
pip install -e .
python folder_dated_zip_backup.py --source ./project --backup-dir ./backups --name project --exclude "*.log,tmp" --keep 5
```

원본은 지우지 않음. zip 안 경로는 source 기준 상대 경로. `--keep`은 같은 이름 zip만 prune.
