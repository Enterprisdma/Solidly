# Sollidly MVP - AI 기반 한국어 글쓰기 보조 도구

## 프로젝트 개요

Sollidly(솔리드리)는 실시간으로 문법 오류를 탐지하고, 논리 구조를 분석하며, 다음 문장을 제안하는 AI 기반 네이티브 데스크톱 애플리케이션입니다.

## 주요 기능

- **실시간 문법 검사**: 타이핑 후 자동으로 맞춤법, 띄어쓰기, 문법 오류 탐지
- **오류 수정 제안**: 발견된 오류에 대한 구체적인 수정 방안 제시
- **AI 문장 제안**: 현재 맥락을 분석하여 다음에 올 수 있는 문장 제안
- **문서 저장/불러오기**: 작성한 글을 로컬 데이터베이스에 저장
- **다크 모드**: 현대적인 UI/UX

## 기술 스택

| 분야 | 기술/도구 |
|------|----------|
| 애플리케이션 개발 | Python 3.10+ |
| GUI 프레임워크 | CustomTkinter |
| AI 모델 | OpenAI GPT API |
| 자연어 처리 | py-hanspell (한국어 맞춤법) |
| 로컬 데이터베이스 | SQLite |
| 패키징 | PyInstaller (향후) |

## 설치 방법

### 1. 사전 요구사항

- Python 3.10 이상
- pip (Python 패키지 관리자)
- OpenAI API 키 (선택사항, AI 기능 사용 시 필요)

### 2. 프로젝트 클론

```bash
git clone <repository-url>
cd sollidly-mvp
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

설치되는 패키지:
- customtkinter: 현대적인 UI 프레임워크
- openai: OpenAI GPT API 클라이언트
- py-hanspell: 한국어 맞춤법 검사
- python-dotenv: 환경 변수 관리
- Pillow: 이미지 처리

### 4. API 키 설정 (선택사항)

AI 기능(문법 검사, 문장 제안)을 사용하려면 OpenAI API 키가 필요합니다.

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일을 열어서 실제 API 키 입력
# OPENAI_API_KEY=실제_API_키_입력
```

OpenAI API 키 발급: https://platform.openai.com/api-keys

**주의**: API 키가 없어도 프로그램은 실행되지만, AI 기능은 제한됩니다. 기본 맞춤법 검사는 py-hanspell로 작동합니다.

## 실행 방법

```bash
python main.py
```

## 프로젝트 구조

```
sollidly-mvp/
├── main.py                 # 메인 실행 파일
├── config.py               # 전역 설정
├── requirements.txt        # 의존성 목록
├── .env.example            # 환경 변수 예시
├── .gitignore              # Git 제외 목록
├── README.md               # 프로젝트 문서
│
├── ai/                     # AI 모듈
│   ├── grammar_checker.py  # 문법 검사
│   └── sentence_suggester.py # 문장 제안
│
├── ui/                     # UI 모듈
│   └── editor_window.py    # 메인 에디터 창
│
└── database/               # 데이터베이스 모듈
    └── db_manager.py       # DB 관리
```

## 사용 방법

### 기본 사용

1. 프로그램을 실행하면 메인 에디터 창이 열립니다
2. 텍스트 영역에 글을 작성합니다
3. 타이핑 후 2초가 지나면 자동으로 문법 검사가 실행됩니다
4. 왼쪽 사이드바에서 발견된 오류를 확인할 수 있습니다

### 주요 기능 사용

#### 문법 검사
- **자동**: 타이핑 중지 후 2초 뒤 자동 실행
- **수동**: 상단 툴바의 "문법 검사" 버튼 클릭

#### 문장 제안
1. 텍스트를 작성합니다
2. "문장 제안" 버튼을 클릭합니다
3. 오른쪽 패널에 3가지 제안이 표시됩니다
4. 원하는 제안의 "적용" 버튼을 클릭하여 텍스트에 추가합니다

#### 문서 저장/불러오기
- **저장**: 툴바의 "저장" 버튼 또는 Ctrl+S
- **불러오기**: 툴바의 "불러오기" 버튼 또는 Ctrl+O
- **새 문서**: 툴바의 "새 문서" 버튼 또는 Ctrl+N

### 단축키

| 단축키 | 기능 |
|--------|------|
| Ctrl+S | 문서 저장 |
| Ctrl+O | 문서 불러오기 |
| Ctrl+N | 새 문서 |

## 코드 설명

### main.py
- 애플리케이션의 진입점
- 의존성 및 API 키 확인
- 메인 윈도우 실행

### config.py
- 전역 설정 관리
- API 키 로드 (환경 변수)
- UI 색상, AI 모델 설정

### ai/grammar_checker.py
- `check_basic_grammar()`: py-hanspell을 사용한 기본 맞춤법 검사
- `check_ai_grammar()`: OpenAI GPT를 사용한 AI 문법 검사
- `check_all()`: 모든 검사 통합 실행

### ai/sentence_suggester.py
- `suggest_next_sentence()`: 다음 문장 3가지 제안
- `analyze_logic()`: 논리 구조 분석 (향후 기능)

### database/db_manager.py
- SQLite 데이터베이스 관리
- 문서 저장/불러오기/삭제
- 사용자 설정 저장
- 문법 오류 로그 (학습 데이터)

### ui/editor_window.py
- CustomTkinter 기반 메인 UI
- 텍스트 에디터, 툴바, 사이드바
- 이벤트 핸들링 및 백그라운드 작업

## 유지보수 가이드

### 새로운 기능 추가

1. **새로운 AI 기능 추가**
   - `ai/` 폴더에 새 모듈 생성
   - config.py에 관련 설정 추가
   - ui/editor_window.py에서 호출

2. **UI 변경**
   - ui/editor_window.py 수정
   - config.COLORS에서 색상 조정

3. **데이터베이스 스키마 변경**
   - database/db_manager.py의 create_tables() 수정

### 문제 해결

#### 프로그램이 실행되지 않음
```bash
# 의존성 재설치
pip install -r requirements.txt --force-reinstall
```

#### API 키 오류
- .env 파일이 프로젝트 루트에 있는지 확인
- API 키 형식이 올바른지 확인
- OpenAI 계정에 크레딧이 있는지 확인

#### 문법 검사가 작동하지 않음
- 인터넷 연결 확인 (py-hanspell은 네이버 API 사용)
- API 키 설정 확인

## 향후 개발 계획

- [ ] 논리 구조 시각화 (그래프)
- [ ] 더 많은 글쓰기 스타일 제안
- [ ] 음성 입력 (STT)
- [ ] 협업 기능
- [ ] 문서 템플릿
- [ ] 실행 파일 배포 (PyInstaller)
- [ ] macOS/Linux 호환성 테스트

## 라이선스

이 프로젝트는 교육 목적으로 만들어졌습니다.

## 문의

프로젝트 관련 문의: 이기후 (1-3반, 1318번)

## 참고 자료

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [CustomTkinter Documentation](https://customtkinter.tomschimansky.com/)
- [py-hanspell GitHub](https://github.com/ssut/py-hanspell)
