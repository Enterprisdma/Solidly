# Sollidly MVP - 빠른 시작 가이드

## 5분 안에 실행하기

### 1단계: Python 확인

```bash
python --version
```

Python 3.10 이상이 필요합니다. 없다면 https://www.python.org/downloads/ 에서 설치하세요.

### 2단계: 프로젝트 폴더로 이동

```bash
cd sollidly-mvp
```

### 3단계: 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

설치가 완료될 때까지 기다립니다 (약 1-2분 소요).

### 4단계: 실행!

```bash
python main.py
```

프로그램이 실행되면 환영 메시지가 표시됩니다.

## API 키 없이 사용하기

API 키가 없어도 프로그램은 정상 작동합니다.
단, AI 기능(고급 문법 검사, 문장 제안)은 제한됩니다.

기본 맞춤법 검사는 py-hanspell을 통해 작동합니다.

## API 키 설정하기 (선택사항)

AI 기능을 모두 사용하려면:

1. OpenAI 계정 생성: https://platform.openai.com/signup
2. API 키 발급: https://platform.openai.com/api-keys
3. 프로젝트 폴더에 `.env` 파일 생성:

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

4. `.env` 파일을 열어서 API 키 입력:

```
OPENAI_API_KEY=여기에_발급받은_키_입력
```

5. 프로그램 재실행

## 문제 해결

### 설치 오류 발생 시

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### "customtkinter" 모듈을 찾을 수 없다는 오류

```bash
pip install customtkinter
```

### 한국어 맞춤법 검사가 작동하지 않음

인터넷 연결을 확인하세요. py-hanspell은 네이버 맞춤법 검사 API를 사용합니다.

## 기본 사용법

1. 텍스트 영역에 글 작성
2. 자동 문법 검사 (타이핑 중지 후 2초)
3. "문장 제안" 버튼으로 다음 문장 받기
4. "저장" 버튼으로 문서 저장

## 다음 단계

더 자세한 내용은 `README.md`를 참고하세요.

즐거운 글쓰기 되세요!
