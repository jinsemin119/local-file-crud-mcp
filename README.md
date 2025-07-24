# LocalCRUD Python 프로젝트

이 프로젝트는 Python 가상환경을 사용하는 개발 환경입니다.

## 환경 설정

### 1. Python 설치
Python이 설치되어 있지 않다면 다음 중 하나의 방법으로 설치하세요:

- **Microsoft Store**: Windows 검색에서 "Python"을 검색하여 설치
- **Python 공식 웹사이트**: https://www.python.org/downloads/ 에서 다운로드

### 2. 가상환경 생성 및 활성화

#### Windows PowerShell에서:
```powershell
# 가상환경 생성
python -m venv env

# 가상환경 활성화
.\env\Scripts\Activate.ps1
```

#### Windows Command Prompt에서:
```cmd
# 가상환경 생성
python -m venv env

# 가상환경 활성화
.\env\Scripts\activate.bat
```

### 3. 의존성 설치
가상환경이 활성화된 상태에서:
```bash
pip install -r requirements.txt
```

## 프로젝트 구조
```
LocalCRUD/
├── env/                 # 가상환경 폴더 (자동 생성됨)
├── requirements.txt     # Python 패키지 의존성
├── .gitignore          # Git 무시 파일 목록
└── README.md           # 프로젝트 설명서
```

## 개발 시작하기

1. 가상환경을 활성화합니다
2. 필요한 패키지를 설치합니다
3. 개발을 시작합니다!

## 유용한 명령어

```bash
# 가상환경 비활성화
deactivate

# 패키지 설치
pip install 패키지명

# 설치된 패키지 목록 확인
pip list

# requirements.txt 업데이트
pip freeze > requirements.txt
``` 


# 로컬 파일 CRUD MCP 프로젝트 개요

## 프로젝트 목표
사용자의 로컬 파일 시스템에 대한 완전한 CRUD(Create, Read, Update, Delete) 작업을 지원하는 Model Context Protocol(MCP) 서버를 개발합니다. 이를 통해 Claude와 같은 AI 어시스턴트가 사용자의 로컬 파일을 직접 조작할 수 있게 됩니다.

## MCP(Model Context Protocol)란?
MCP는 AI 어시스턴트와 외부 데이터 소스 및 도구를 연결하는 오픈 프로토콜입니다. USB-C처럼 표준화된 인터페이스를 제공하여 AI 모델이 다양한 데이터 소스와 도구에 접근할 수 있게 해줍니다.

**핵심 구조:**
- **MCP 호스트**: Claude Desktop, IDE 등 MCP를 통해 데이터에 접근하려는 프로그램
- **MCP 서버**: 특정 기능을 표준화된 프로토콜로 노출하는 경량 프로그램
- **데이터 소스**: 로컬 파일, 데이터베이스, 외부 API 등

## 구현된 핵심 기능

### 1. 파일 읽기 (`read_file`)
- 지정된 경로의 파일 내용을 읽어와 반환
- UTF-8 인코딩 지원

### 2. 파일 쓰기 (`write_file`)
- 새 파일 생성 또는 기존 파일 덮어쓰기
- 필요시 디렉토리 자동 생성
- UTF-8 인코딩으로 저장

### 3. 파일 추가 (`append_file`)
- 기존 파일 끝에 내용 추가
- 로그 파일 작성 등에 유용

### 4. 파일 수정 (`update_file`)
- 찾기/바꾸기 기능을 통한 부분 수정
- 정규식 지원으로 패턴 기반 치환

### 5. 파일 삭제 (`delete_file`)
- 지정된 파일 완전 삭제

### 6. 디렉토리 조회 (`list_files`)
- 디렉토리 내 파일 및 폴더 목록 반환
- 파일/디렉토리 타입 구분

### 7. 디렉토리 생성 (`create_directory`)
- 새 디렉토리 생성
- 중첩 디렉토리 자동 생성 지원

## 기술 스택

### 코어 기술
- **Python 3.8+**: 서버 런타임 환경
- **FastAPI**: 현대적이고 빠른 웹 프레임워크
- **Pydantic**: 데이터 검증 및 직렬화
- **aiofiles**: 비동기 파일 I/O

### 주요 의존성
```txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
aiofiles==23.2.1
aiohttp==3.9.1
```

### 아키텍처
- **Transport**: 
  - StdioServerTransport (표준 입출력 기반) - Claude Desktop 연동용
  - HTTP/WebSocket - 개발 및 테스트용
- **통신 방식**: JSON-RPC over stdio 또는 HTTP
- **인터페이스**: 표준화된 MCP 도구 스키마

## 프로젝트 구조

```
LocalCRUD/
├── mcp_server.py         # 메인 FastAPI MCP 서버 구현
├── run_mcp_server.py     # 서버 실행 스크립트
├── test_mcp_server.py    # MCP stdio 서버 테스트
├── test_web_api.py       # 웹 API 테스트
├── requirements.txt      # Python 패키지 의존성
├── setup.ps1            # PowerShell 설정 스크립트
├── setup.bat            # Command Prompt 설정 스크립트
└── README.md            # 프로젝트 문서
```

## 설치 및 실행

### 1. 가상환경 설정 및 의존성 설치
```bash
# 가상환경 생성 및 활성화
python -m venv env
.\env\Scripts\Activate.ps1  # Windows PowerShell
# 또는
.\env\Scripts\activate.bat  # Windows Command Prompt

# 의존성 설치
pip install -r requirements.txt
```

### 2. 서버 실행

#### MCP Stdio 서버 (Claude Desktop 연동용)
```bash
python run_mcp_server.py
# 또는
python mcp_server.py
```

#### 웹 서버 (개발/테스트용)
```bash
python run_mcp_server.py --web
# 또는
python mcp_server.py --web
```

### 3. Claude Desktop 연동
`claude_desktop_config.json`에 다음 설정 추가:
```json
{
  "mcpServers": {
    "local-file-crud": {
      "command": "python",
      "args": ["path/to/your/LocalCRUD/mcp_server.py"]
    }
  }
}
```

### 4. 테스트 실행
```bash
# MCP stdio 서버 테스트
python test_mcp_server.py

# 웹 API 테스트
python test_web_api.py
```

## 보안 고려사항

### 현재 구현
- 기본적인 파일시스템 접근 제어
- UTF-8 인코딩 강제로 바이너리 파일 오작동 방지

### 추가 보안 강화 필요사항
1. **경로 검증**: 허용된 디렉토리 외부 접근 차단
2. **파일 타입 제한**: 실행 파일 등 위험한 파일 타입 제한
3. **권한 관리**: 읽기 전용/쓰기 권한 세분화
4. **로깅**: 모든 파일 작업에 대한 감사 로그

```javascript
// 보안 강화 예시
const ALLOWED_PATHS = ['/home/user/documents', '/home/user/projects'];
const BLOCKED_EXTENSIONS = ['.exe', '.sh', '.bat'];

function validatePath(filepath) {
  const resolvedPath = path.resolve(filepath);
  return ALLOWED_PATHS.some(allowedPath => 
    resolvedPath.startsWith(path.resolve(allowedPath))
  );
}
```

## 사용 사례

### 개발 워크플로우
- **코드 생성**: AI가 직접 소스 파일 생성
- **설정 파일 관리**: 프로젝트 설정 파일 자동 생성/수정
- **문서 작성**: README, API 문서 자동 생성

### 콘텐츠 관리
- **마크다운 편집**: 블로그 포스트, 문서 작성
- **데이터 처리**: CSV, JSON 파일 조작
- **로그 분석**: 로그 파일 읽기 및 분석

### 시스템 관리
- **백업 파일 관리**: 자동화된 파일 백업
- **환경 설정**: 개발 환경 설정 파일 관리

## 확장 가능성

### 추가 기능 아이디어
1. **파일 검색**: 내용 기반 파일 검색
2. **압축/해제**: ZIP, TAR 파일 처리
3. **파일 변환**: 포맷 간 변환 (Markdown → HTML 등)
4. **버전 관리**: 파일 변경 이력 추적
5. **동기화**: 클라우드 스토리지 연동

### 성능 최적화
1. **스트리밍**: 대용량 파일 스트리밍 처리
2. **캐싱**: 자주 접근하는 파일 캐시
3. **배치 작업**: 여러 파일 동시 처리

## 에러 처리

현재 구현된 에러 처리:
- 파일 접근 권한 오류
- 존재하지 않는 파일/디렉토리
- 인코딩 오류
- 시스템 리소스 부족

## FastAPI 기반 구현의 장점

### 1. 성능 및 확장성
- **비동기 처리**: `async/await`를 통한 고성능 비동기 파일 I/O
- **자동 문서화**: FastAPI의 자동 API 문서 생성 (`/docs`, `/redoc`)
- **타입 안전성**: Pydantic을 통한 런타임 데이터 검증

### 2. 개발자 경험
- **자동 완성**: IDE에서 완벽한 타입 힌트 지원
- **실시간 문서**: API 변경 시 자동으로 문서 업데이트
- **테스트 용이성**: 웹 API와 stdio 모드 모두 지원

### 3. 유연한 배포
- **이중 모드**: 웹 서버와 stdio 서버 모두 지원
- **컨테이너화**: Docker 배포 용이
- **클라우드 친화적**: AWS Lambda, Google Cloud Functions 등에 배포 가능

### 4. 보안 및 안정성
- **입력 검증**: Pydantic 스키마를 통한 자동 검증
- **에러 처리**: 구조화된 에러 응답
- **로깅**: 상세한 로그 및 디버깅 정보

## 라이선스 및 배포

- **라이선스**: MIT
- **패키징**: PyPI 패키지로 배포 가능
- **글로벌 설치**: `pip install local-file-crud-mcp`

## 향후 로드맵

### Phase 1: 안정성 강화
- 포괄적인 에러 처리
- 단위 테스트 작성
- 성능 최적화

### Phase 2: 보안 강화
- 세밀한 권한 관리
- 감사 로깅
- 안전한 기본값 설정

### Phase 3: 기능 확장
- 고급 파일 작업
- 플러그인 시스템
- 웹 인터페이스

이 프로젝트는 AI와 로컬 파일 시스템 간의 완전한 브리지를 제공하여, 개발자가 AI의 도움으로 로컬 파일을 직접 조작할 수 있는 혁신적인 도구입니다.