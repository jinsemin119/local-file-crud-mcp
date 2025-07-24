@echo off
echo Python 가상환경 설정 스크립트
echo.

REM Python 설치 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python이 설치되어 있지 않습니다.
    echo Python을 먼저 설치해주세요.
    echo Microsoft Store에서 Python을 검색하여 설치하거나
    echo https://www.python.org/downloads/ 에서 다운로드하세요.
    pause
    exit /b 1
)

echo Python 버전 확인:
python --version
echo.

REM 가상환경 생성
echo 가상환경을 생성합니다...
python -m venv env
if %errorlevel% neq 0 (
    echo 가상환경 생성에 실패했습니다.
    pause
    exit /b 1
)

echo 가상환경이 성공적으로 생성되었습니다!
echo.
echo 다음 명령어로 가상환경을 활성화하세요:
echo .\env\Scripts\activate.bat
echo.
echo 가상환경 활성화 후 다음 명령어로 패키지를 설치하세요:
echo pip install -r requirements.txt
echo.
pause 