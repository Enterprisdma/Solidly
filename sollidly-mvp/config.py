"""
Sollidly 애플리케이션 설정 파일

이 파일은 애플리케이션의 전역 설정을 관리합니다.
- API 키 (환경변수에서 로드)
- UI 색상 테마
- 데이터베이스 경로
- AI 모델 설정
"""

import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# 데이터베이스 설정
DB_PATH = "sollidly.db"

# UI 설정
WINDOW_TITLE = "Sollidly - AI 글쓰기 보조 도구"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# 색상 테마 (CustomTkinter 다크 모드)
COLORS = {
    "primary": "#1f6aa5",      # 메인 파란색
    "error": "#d32f2f",        # 오류 빨간색
    "warning": "#f57c00",      # 경고 주황색
    "success": "#388e3c",      # 성공 초록색
    "bg_dark": "#1a1a1a",      # 배경 어두운색
    "bg_light": "#2b2b2b",     # 배경 밝은색
    "text": "#ffffff",         # 텍스트 흰색
    "text_secondary": "#b0b0b0" # 보조 텍스트
}

# AI 모델 설정
AI_CONFIG = {
    "model": "gpt-4",          # 사용할 GPT 모델
    "temperature_grammar": 0.2, # 문법 검사용 낮은 창의성
    "temperature_suggest": 0.7, # 문장 제안용 높은 창의성
    "max_tokens": 500,         # 최대 토큰 수
    "timeout": 30              # API 타임아웃 (초)
}

# 문법 검사 설정
GRAMMAR_CHECK = {
    "min_delay": 1.0,          # 최소 검사 지연 시간 (초)
    "highlight_color": COLORS["error"]
}

# 제안 기능 설정
SUGGESTION = {
    "max_suggestions": 3,      # 최대 제안 개수
    "auto_popup": True         # 자동 팝업 여부
}

# 오버레이 윈도우 설정
OVERLAY = {
    "opacity": 0.0,            # 배경 투명도 (0.0 = 완전 투명)
    "topmost": True,           # 항상 위
    "click_through": False,    # 클릭 통과 (False = 메뉴 클릭 가능)
    "update_interval": 100     # 업데이트 간격 (ms)
}

# 키보드 단축키 설정
HOTKEYS = {
    "toggle_menu": ["ctrl", "shift", "s"],  # Ctrl+Shift+S (Sollidly)
    "exit_app": ["ctrl", "shift", "q"]      # Ctrl+Shift+Q (Quit)
}

# 동그라미 메뉴 설정
CIRCLE_MENU = {
    "radius": 60,              # 동그라미 반지름
    "color": "#4A90E2",        # 동그라미 색상
    "animation_duration": 300, # 애니메이션 시간 (ms)
    "menu_items": [
        {"name": "종료", "icon": "❌", "color": "#E74C3C"},
        {"name": "다음 글 제안", "icon": "✍️", "color": "#3498DB"},
        {"name": "논리 구조 검사", "icon": "🔍", "color": "#2ECC71"}
    ]
}

# 텍스트 모니터링 설정
TEXT_MONITOR = {
    "check_interval": 0.5,     # 텍스트 변경 체크 간격 (초)
    "min_text_length": 10,     # 최소 텍스트 길이 (문법 검사 시작)
    "debounce_time": 2.0       # 타이핑 멈춘 후 검사 시작까지 시간 (초)
}
