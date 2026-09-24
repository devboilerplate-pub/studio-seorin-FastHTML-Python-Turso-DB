# Studio Seorin

FastHTML + Turso 기반 개인 크리에이터 포트폴리오.

Google/GitHub 로그인, 좋아요, 리뷰, 관리자 콘텐츠 관리를 지원합니다. 개발 단계에서는 Mock Repository / Mock Auth를 쓰고, 운영에서는 같은 서비스 인터페이스 뒤의 구현만 교체합니다.

## Stack

- FastHTML
- Turso (libSQL) / Mock store
- Authlib OAuth (Google, GitHub)
- Vercel

## Local

### 프로젝트 실행 방법 (사전 조건: 가상 환경 설정)

이 프로젝트를 안정적으로 실행하고 IDE에서 패키지들을 정상적으로 인식하게 하려면, 프로젝트 폴더 내에 **가상 환경(`.venv`)**을 먼저 생성하고 활성화하는 것을 강력히 권장합니다. (Windows 환경의 경우 `python3` 대신 `py` 명령어를 사용하시길 권장합니다.)

**1. 가상 환경 생성 및 활성화**
터미널을 열고 운영체제에 맞게 아래 명령어를 차례대로 입력하세요.

- **Windows (PowerShell)**:
  ```powershell
  py -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- **Windows (cmd)**:
  ```cmd
  py -m venv .venv
  .\.venv\Scripts\activate.bat
  ```
- **Mac/Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
*(터미널 입력창 맨 앞에 `(.venv)`가 표시되면 성공입니다. 가상 환경 활성화 후, IDE에서 해당 인터프리터를 선택하시면 이후 새 터미널에서 자동으로 적용됩니다.)*

**2. 패키지 설치 및 서버 구동**
가상 환경이 켜져 있는 상태에서 아래 명령어들을 실행합니다.

```bash
py -m pip install -r requirements.txt  # (Mac/Linux는 python3)
cp .env.example .env                   # (선택) 목업 모드로 실행 시 생략 가능
py main.py                             # (Mac/Linux는 python3)
```

기본 주소는 `http://localhost:5001` 입니다. `.env` 파일이 없거나 `USE_MOCK=true` 로 설정되어 있으면, 별도의 인증 키나 원격 DB 연결 없이 **목업 로그인 및 메모리 DB(Mock Store)**를 통해 모든 기능(좋아요, 리뷰, 관리자 화면 등)을 즉시 테스트할 수 있습니다.

- **관리자 목업 테스트**: 로그인 화면에서 `관리자(서린)로 입장` 버튼을 클릭하세요.

### 💡 패키지 설치 시 PATH 관련 경고(WARNING) 대처법
`pip install` 실행 시 터미널에 텍스트가 노란색으로 표시되며 다음과 같은 경고가 발생할 수 있습니다.
> `WARNING: The script uvicorn.exe is installed in 'C:\Users\...\Python...\Scripts' which is not on PATH.`

- **원인 및 영향**: 패키지 실행 파일(`uvicorn`, `dotenv` 등)이 설치된 폴더가 윈도우의 시스템 환경 변수(PATH)에 등록되지 않아서 발생하는 **단순 경고**입니다. 패키지 설치는 성공적으로 완료된 것이며 치명적인 오류(Error)가 아닙니다.
- **해결 방법**: 
  본 프로젝트는 `uvicorn` 명령어를 터미널에서 직접 타이핑하지 않고 스크립트 내부(`py main.py`)에서 알아서 구동하므로, **이 경고를 완전히 무시하고 바로 프로젝트를 실행하셔도 아무 문제 없이 완벽하게 작동**합니다.
  (※ 단, 추후 터미널에서 명령어들을 직접 사용하고 싶으시다면 윈도우 시작 메뉴에서 '환경 변수'를 검색하여 **시스템 환경 변수의 `Path` 항목**에 경고창에 뜬 경로를 수동으로 추가한 뒤 터미널을 껐다 켜시면 됩니다.)

## Production switch

`.env` 에서 아래를 채운 뒤 `USE_MOCK=false` 로 전환합니다.

- `TURSO_DATABASE_URL`
- `TURSO_AUTH_TOKEN`
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`
- `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET`
- `ADMIN_EMAILS`
- `SECRET_KEY`
- `SITE_URL`

콜백 URL:

- `{SITE_URL}/auth/callback/google`
- `{SITE_URL}/auth/callback/github`

## Vercel 배포 시 주의사항 및 점검 내역 (Deploy)

본 프로젝트는 Vercel의 서버리스(Serverless) 환경에 배포하기 적합하도록 구성되어 있습니다.

### 호환성 검토 완료 사항
- **데이터베이스 (Turso DB)**: Vercel 서버리스 환경은 호출 시 파일 시스템이 초기화되므로 로컬 SQLite 파일 사용이 불가합니다. 하지만 원격 데이터베이스인 Turso를 사용하고 있어 완벽하게 호환됩니다.
- **세션 관리**: Starlette의 `SessionMiddleware`를 사용하여 상태를 저장하지 않는(Stateless) Vercel 환경에서도 쿠키 기반으로 안정적인 세션 처리가 가능합니다.
- **라우팅 및 정적 파일 최적화 적용 완료**: 
  - Vercel의 최신 Zero-config(rewrites) 방식으로 `vercel.json`을 수정하여 레거시 빌더 경고를 방지했습니다.
  - Vercel 환경에서 발생할 수 있는 경로 이슈를 막기 위해 `main.py` 내 `static` 폴더 참조를 절대 경로로 수정해 두었습니다.

### ⚠️ 배포 시 사용자가 직접 해야 할 일 (중요)

프로젝트를 Vercel과 연동(GitHub 연결 또는 CLI 배포)한 후, **Vercel Dashboard의 [Settings] > [Environment Variables] 메뉴에서 아래의 환경 변수들을 반드시 등록**하셔야 정상 작동합니다.

1. `USE_MOCK` : `false` 또는 `0` 으로 설정 (실제 DB 및 로그인 사용)
2. `SECRET_KEY` : 세션 암호화용 비밀 키
3. `TURSO_DATABASE_URL` : Turso DB 접속 URL
4. `TURSO_AUTH_TOKEN` : Turso 인증 토큰
5. `SITE_URL` : Vercel 배포 후 발급받은 도메인 주소 (예: `https://your-project.vercel.app`)
6. `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` : Google OAuth 로그인 키
7. `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` : GitHub OAuth 로그인 키
8. `ADMIN_EMAILS` : 관리자 권한을 부여할 이메일 주소 목록 (콤마 분리)

> **참고 (`runtime.txt` 관련)**: 
> `runtime.txt` 파일에 `python-3.11`로 선언되어 있습니다. 만약 Vercel 빌드 중 버전 관련 에러가 발생할 경우, 해당 파일을 삭제하고 Vercel의 최신 기본 버전(Python 3.12)으로 배포하셔도 됩니다. (FastHTML은 Python 3.10 이상에서 문제없이 구동됩니다)

## Structure

- `main.py` — FastHTML app
- `services/` — Store / Auth 인터페이스와 Mock, Turso 구현
- `routes/` — 페이지, 인증, 관리자
- `db/schema.sql` — Turso 스키마
- `db/seed.py` — 초기 작업/프로필
