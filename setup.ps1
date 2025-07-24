# Python 가상환경 설정 스크립트 (PowerShell)

Write-Host "Python 가상환경 설정 스크립트" -ForegroundColor Green
Write-Host ""

# Python 설치 확인
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python 버전 확인:" -ForegroundColor Yellow
    Write-Host $pythonVersion -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "Python이 설치되어 있지 않습니다." -ForegroundColor Red
    Write-Host "Python을 먼저 설치해주세요." -ForegroundColor Yellow
    Write-Host "Microsoft Store에서 Python을 검색하여 설치하거나" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/ 에서 다운로드하세요." -ForegroundColor Yellow
    Read-Host "아무 키나 눌러서 종료"
    exit 1
}

# 가상환경 생성
Write-Host "가상환경을 생성합니다..." -ForegroundColor Yellow
try {
    python -m venv env
    Write-Host "가상환경이 성공적으로 생성되었습니다!" -ForegroundColor Green
    Write-Host ""
    Write-Host "다음 명령어로 가상환경을 활성화하세요:" -ForegroundColor Cyan
    Write-Host ".\env\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "가상환경 활성화 후 다음 명령어로 패키지를 설치하세요:" -ForegroundColor Cyan
    Write-Host "pip install -r requirements.txt" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "가상환경 생성에 실패했습니다." -ForegroundColor Red
    Read-Host "아무 키나 눌러서 종료"
    exit 1
}

Read-Host "아무 키나 눌러서 종료" 