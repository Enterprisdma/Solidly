"""
오버레이 윈도우 모듈

역할:
- 투명한 전체 화면 오버레이 윈도우
- 텍스트 에디터 위에 표시
- 문법 오류 하이라이트
- 동그라미 메뉴 표시

주요 기능:
1. 투명 배경 (클릭 통과 가능)
2. 항상 위에 표시
3. 문법 오류 위치에 빨간색 밑줄
4. Alt+Q+Enter 시 동그라미 메뉴 표시

사용 예:
    overlay = OverlayWindow()
    overlay.show_errors(errors)
    overlay.show_menu(x, y)
"""

import customtkinter as ctk
import tkinter as tk
from typing import List, Dict, Optional
import config
from ui.circle_menu import CircleMenu


class OverlayWindow(ctk.CTk):
    """투명 오버레이 윈도우 클래스"""

    def __init__(self):
        """오버레이 윈도우 초기화"""
        super().__init__()

        # 윈도우 설정
        self.title("Sollidly Overlay")

        # 전체 화면 크기
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")

        # 투명 설정
        self.attributes("-alpha", config.OVERLAY["opacity"])  # 완전 투명 배경
        self.attributes("-topmost", config.OVERLAY["topmost"])  # 항상 위

        # 윈도우 장식 제거
        self.overrideredirect(True)

        # 배경색 (투명이지만 설정 필요)
        self.configure(bg_color="black")

        # 클릭 통과 설정 (Windows only)
        try:
            import win32gui
            import win32con
            hwnd = int(self.wm_frame(), 16)
            styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            styles |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
        except Exception as e:
            print(f"클릭 통과 설정 실패: {e}")

        # 캔버스 (문법 오류 표시용)
        self.canvas = tk.Canvas(
            self,
            bg="black",
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        # 동그라미 메뉴
        self.circle_menu: Optional[CircleMenu] = None

        # 상태 변수
        self.error_markers = []
        self.is_menu_visible = False

    def show_errors(self, errors: List[Dict], cursor_x: int = 100, cursor_y: int = 100):
        """
        문법 오류 표시

        매개변수:
            errors: 오류 리스트
            cursor_x: 커서 X 좌표
            cursor_y: 커서 Y 좌표
        """
        # 기존 마커 제거
        self.clear_errors()

        # 새 마커 그리기 (커서 주변에 오류 개수만큼 표시)
        for i, error in enumerate(errors[:5]):  # 최대 5개만 표시
            # 오류 마커 위치 (커서 아래쪽)
            marker_x = cursor_x
            marker_y = cursor_y + 20 + (i * 25)

            # 빨간색 밑줄
            line = self.canvas.create_line(
                marker_x, marker_y,
                marker_x + 100, marker_y,
                fill=config.COLORS["error"],
                width=2
            )
            self.error_markers.append(line)

            # 오류 텍스트 (작게 표시)
            text = self.canvas.create_text(
                marker_x, marker_y + 10,
                text=error.get('type', '오류'),
                fill=config.COLORS["error"],
                font=("맑은 고딕", 8),
                anchor="nw"
            )
            self.error_markers.append(text)

    def clear_errors(self):
        """모든 오류 마커 제거"""
        for marker in self.error_markers:
            self.canvas.delete(marker)
        self.error_markers.clear()

    def show_menu(self, x: int, y: int):
        """
        동그라미 메뉴 표시

        매개변수:
            x: 메뉴 중심 X 좌표
            y: 메뉴 중심 Y 좌표
        """
        # 클릭 통과 비활성화 (메뉴 클릭 가능하도록)
        self._disable_click_through()

        # 배경 약간 보이게
        self.attributes("-alpha", 0.1)

        # 메뉴가 없으면 생성
        if not self.circle_menu:
            self.circle_menu = CircleMenu(self, x, y)
            self.circle_menu.set_callbacks(
                on_exit=self._on_menu_exit,
                on_suggest=self._on_menu_suggest,
                on_analyze=self._on_menu_analyze
            )
        else:
            self.circle_menu.update_position(x, y)

        # 메뉴 표시
        self.circle_menu.show()
        self.is_menu_visible = True

    def hide_menu(self):
        """동그라미 메뉴 숨기기"""
        if self.circle_menu:
            self.circle_menu.hide()

        # 클릭 통과 재활성화
        self._enable_click_through()

        # 배경 완전 투명
        self.attributes("-alpha", config.OVERLAY["opacity"])

        self.is_menu_visible = False

    def _disable_click_through(self):
        """클릭 통과 비활성화 (메뉴 클릭 가능)"""
        try:
            import win32gui
            import win32con
            hwnd = int(self.wm_frame(), 16)
            styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            styles &= ~win32con.WS_EX_TRANSPARENT  # 클릭 통과 제거
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
        except Exception as e:
            print(f"클릭 통과 비활성화 실패: {e}")

    def _enable_click_through(self):
        """클릭 통과 활성화"""
        try:
            import win32gui
            import win32con
            hwnd = int(self.wm_frame(), 16)
            styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            styles |= win32con.WS_EX_TRANSPARENT  # 클릭 통과 추가
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
        except Exception as e:
            print(f"클릭 통과 활성화 실패: {e}")

    def _on_menu_exit(self):
        """메뉴 - 종료"""
        print("종료 버튼 클릭")
        self.hide_menu()
        # 실제 종료는 main.py에서 처리

    def _on_menu_suggest(self):
        """메뉴 - 다음 글 제안"""
        print("다음 글 제안 버튼 클릭")
        self.hide_menu()
        # 제안 로직은 main.py에서 처리

    def _on_menu_analyze(self):
        """메뉴 - 논리 구조 검사"""
        print("논리 구조 검사 버튼 클릭")
        self.hide_menu()
        # 분석 로직은 main.py에서 처리

    def set_menu_callbacks(self, on_exit, on_suggest, on_analyze):
        """
        메뉴 콜백 설정

        매개변수:
            on_exit: 종료 콜백
            on_suggest: 제안 콜백
            on_analyze: 분석 콜백
        """
        self._on_menu_exit = on_exit
        self._on_menu_suggest = on_suggest
        self._on_menu_analyze = on_analyze

    def toggle_menu(self, x: int, y: int):
        """
        메뉴 토글

        매개변수:
            x: 메뉴 X 좌표
            y: 메뉴 Y 좌표
        """
        if self.is_menu_visible:
            self.hide_menu()
        else:
            self.show_menu(x, y)

    def update_cursor_position(self, x: int, y: int):
        """
        커서 위치 업데이트 (오류 표시 위치 조정용)

        매개변수:
            x: 커서 X 좌표
            y: 커서 Y 좌표
        """
        # 현재는 사용하지 않지만, 나중에 커서 따라다니는 UI 추가 가능
        pass

    def display_suggestion(self, suggestion: str, x: int, y: int):
        """
        문장 제안을 화면에 표시

        매개변수:
            suggestion: 제안 문장
            x: 표시 X 좌표
            y: 표시 Y 좌표
        """
        # 배경 약간 보이게
        self.attributes("-alpha", 0.3)
        self._disable_click_through()

        # 제안 박스 생성
        box_width = 400
        box_height = 100

        # 박스 배경
        box = self.canvas.create_rectangle(
            x, y,
            x + box_width, y + box_height,
            fill="#2C3E50",
            outline=config.COLORS["primary"],
            width=2,
            tags="suggestion_box"
        )

        # 제목
        title = self.canvas.create_text(
            x + 10, y + 10,
            text="💡 다음 글 제안",
            fill=config.COLORS["primary"],
            font=("맑은 고딕", 10, "bold"),
            anchor="nw",
            tags="suggestion_box"
        )

        # 제안 텍스트
        text = self.canvas.create_text(
            x + 10, y + 35,
            text=suggestion,
            fill="white",
            font=("맑은 고딕", 12),
            anchor="nw",
            width=box_width - 20,
            tags="suggestion_box"
        )

        # 3초 후 자동 제거
        self.after(3000, self.clear_suggestion)

    def clear_suggestion(self):
        """제안 박스 제거"""
        self.canvas.delete("suggestion_box")
        self.attributes("-alpha", config.OVERLAY["opacity"])
        self._enable_click_through()

    def close(self):
        """오버레이 윈도우 닫기"""
        self.destroy()
