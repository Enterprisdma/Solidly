"""
Sollidly MVP - 메인 실행 파일

실행 방법:
    python main.py

역할:
- 애플리케이션 초기화
- 메인 윈도우 실행
- 예외 처리

유지보수 방법:
- 시작 시 초기화 작업: _initialize() 메서드 수정
- 전역 예외 처리: main() 함수의 try-except 블록 수정
"""

import subprocess
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def install_requirements():
    """requirements.txt 파일의 모든 패키지를 개별적으로 설치합니다."""
    import os
    requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")

    if not os.path.exists(requirements_path):
        print("requirements.txt 파일을 찾을 수 없습니다.")
        return

    print("=" * 50)
    print("requirements.txt의 패키지들을 설치합니다...")
    print("=" * 50)

    # 먼저 pip, setuptools, wheel 업그레이드
    print("\n빌드 도구 업그레이드 중...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("✓ 빌드 도구 업그레이드 완료!")
    except subprocess.CalledProcessError:
        print("⚠ 빌드 도구 업그레이드 실패 (계속 진행)")

    # requirements.txt 파일 읽기
    with open(requirements_path, 'r', encoding='utf-8') as f:
        packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    success_count = 0
    failed_packages = []

    for package in packages:
        print(f"\n[{packages.index(package) + 1}/{len(packages)}] {package} 설치 중...")

        # py-hanspell은 특별 처리
        if package.startswith('py-hanspell'):
            installed = False

            # 방법 1: GitHub에서 직접 설치 (pip install git+)
            print("  방법 1: GitHub에서 직접 설치 중...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "git+https://github.com/ssut/py-hanspell.git"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"✓ {package} 설치 완료! (GitHub 직접 설치)")
                success_count += 1
                installed = True
            except subprocess.CalledProcessError:
                print("  방법 1 실패, 다음 방법 시도...")

            # 방법 2: 리포지토리 클론 후 설치
            if not installed:
                print("  방법 2: 리포지토리 클론 후 설치 중...")
                import tempfile
                import shutil

                temp_dir = tempfile.mkdtemp()
                try:
                    # git clone
                    clone_result = subprocess.run(
                        ["git", "clone", "https://github.com/ssut/py-hanspell.git", temp_dir],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        cwd=os.path.dirname(temp_dir)
                    )

                    if clone_result.returncode == 0:
                        # pip install from cloned directory
                        install_result = subprocess.run(
                            [sys.executable, "-m", "pip", "install", "."],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            cwd=temp_dir
                        )

                        if install_result.returncode == 0:
                            print(f"✓ {package} 설치 완료! (리포지토리 클론)")
                            success_count += 1
                            installed = True
                        else:
                            print("  방법 2 실패 (설치 단계), 다음 방법 시도...")
                    else:
                        print("  방법 2 실패 (클론 단계), 다음 방법 시도...")
                except Exception:
                    print("  방법 2 실패 (예외 발생), 다음 방법 시도...")
                finally:
                    # 임시 디렉토리 삭제
                    try:
                        shutil.rmtree(temp_dir, ignore_errors=True)
                    except Exception:
                        pass

            # 방법 3: PyPI에서 일반 설치
            if not installed:
                print("  방법 3: PyPI에서 일반 설치 시도...")
                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", package],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    print(f"✓ {package} 설치 완료! (PyPI)")
                    success_count += 1
                    installed = True
                except subprocess.CalledProcessError:
                    pass

            if not installed:
                print(f"✗ {package} 설치 실패 - 모든 방법 시도 완료")
                print("  수동 설치가 필요합니다:")
                print("  1. git clone https://github.com/ssut/py-hanspell.git")
                print("  2. cd py-hanspell")
                print("  3. pip install .")
                failed_packages.append(package)
        else:
            # 일반 패키지 설치
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
                print(f"✓ {package} 설치 완료!")
                success_count += 1
            except subprocess.CalledProcessError:
                print(f"✗ {package} 설치 실패 (건너뜀)")
                failed_packages.append(package)

    print("\n" + "=" * 50)
    print(f"설치 완료: {success_count}/{len(packages)} 패키지")
    if failed_packages:
        print(f"실패한 패키지: {', '.join(failed_packages)}")
        print("\n실패한 패키지는 수동으로 설치해야 할 수 있습니다.")
    print("=" * 50)

# requirements.txt의 패키지 설치
install_requirements()

import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.editor_window import EditorWindow
import config


def check_dependencies():
    """
    필수 라이브러리 확인
    
    확인 항목:
    - customtkinter
    - openai (선택)
    - hanspell
    
    반환값:
        모든 필수 라이브러리가 설치됨: True
        누락된 라이브러리가 있음: False
    """
    missing = []
    
    try:
        import customtkinter
    except ImportError:
        missing.append("customtkinter")
    
    try:
        import hanspell
    except ImportError:
        missing.append("py-hanspell")
    
    try:
        from dotenv import load_dotenv
    except ImportError:
        missing.append("python-dotenv")
    
    if missing:
        print("=" * 50)
        print("필수 라이브러리가 누락되었습니다!")
        print("=" * 50)
        print("\n다음 명령어로 설치하세요:")
        print(f"pip install {' '.join(missing)}")
        print("\n또는:")
        print("pip install -r requirements.txt")
        print("=" * 50)
        return False
    
    return True


def check_api_keys():
    """
    API 키 확인 (경고만 표시)
    
    OpenAI API 키가 없어도 프로그램은 실행되지만
    AI 기능은 제한됩니다.
    """
    warnings = []
    
    if not config.OPENAI_API_KEY:
        warnings.append("OpenAI API 키가 설정되지 않았습니다.")
        warnings.append("AI 문법 검사 및 문장 제안 기능이 제한됩니다.")
    
    if warnings:
        print("\n" + "=" * 50)
        print("경고")
        print("=" * 50)
        for warning in warnings:
            print(f"- {warning}")
        print("\nAPI 키 설정 방법:")
        print("1. .env 파일을 프로젝트 폴더에 생성")
        print("2. 다음 내용 추가:")
        print("   OPENAI_API_KEY=your_api_key_here")
        print("=" * 50 + "\n")


def _initialize():
    """
    애플리케이션 초기화
    
    수행 작업:
    - 의존성 확인
    - API 키 확인
    - 데이터베이스 초기화 (자동)
    """
    print("Sollidly MVP 시작 중...")
    
    # 의존성 확인
    if not check_dependencies():
        sys.exit(1)
    
    # API 키 확인 (경고만)
    check_api_keys()
    
    print("초기화 완료!\n")


def main():
    """
    메인 함수
    
    애플리케이션 실행 진입점
    """
    try:
        # 초기화
        _initialize()
        
        # 메인 윈도우 생성 및 실행
        app = EditorWindow()
        
        # 닫기 이벤트 핸들러 등록
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # 메인 루프 시작
        print("애플리케이션 실행 중...")
        app.mainloop()
        
        print("애플리케이션 종료")
    
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
