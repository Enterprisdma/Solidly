"""
텍스트 모니터링 모듈

역할:
- 외부 텍스트 에디터(한글, Word 등)의 텍스트 감지
- 커서 위치 추적
- 클립보드를 통한 텍스트 캡처
- 실시간 텍스트 변경 감지

주요 기능:
1. get_active_window(): 활성 윈도우 정보 가져오기
2. get_cursor_position(): 커서 위치 가져오기
3. capture_text(): 현재 텍스트 캡처
4. start_monitoring(): 모니터링 시작

사용 예:
    monitor = TextMonitor()
    monitor.set_text_change_callback(on_text_changed)
    monitor.start_monitoring()
"""

import win32gui
import win32api
import win32con
import pyautogui
import pyperclip
import threading
import time
from typing import Callable, Optional, Tuple
import config


class TextMonitor:
    """텍스트 모니터링 클래스"""

    def __init__(self):
        """텍스트 모니터 초기화"""
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.last_text = ""
        self.last_cursor_pos = (0, 0)
        self.text_change_callback: Optional[Callable] = None
        self.cursor_change_callback: Optional[Callable] = None

        # 설정 로드
        self.check_interval = config.TEXT_MONITOR["check_interval"]
        self.debounce_time = config.TEXT_MONITOR["debounce_time"]
        self.last_change_time = 0

    def get_active_window(self) -> dict:
        """
        현재 활성화된 윈도우 정보 가져오기

        반환값:
            윈도우 정보 딕셔너리 {
                "hwnd": 윈도우 핸들,
                "title": 윈도우 제목,
                "class_name": 윈도우 클래스명,
                "rect": (left, top, right, bottom)
            }
        """
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                title = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                rect = win32gui.GetWindowRect(hwnd)

                return {
                    "hwnd": hwnd,
                    "title": title,
                    "class_name": class_name,
                    "rect": rect
                }
        except Exception as e:
            print(f"활성 윈도우 가져오기 오류: {e}")

        return None

    def get_cursor_position(self) -> Tuple[int, int]:
        """
        현재 마우스 커서 위치 가져오기
        (텍스트 에디터의 캐럿 위치를 정확히 가져오기는 어려우므로 근사값 사용)

        반환값:
            (x, y) 좌표 튜플
        """
        try:
            return pyautogui.position()
        except Exception as e:
            print(f"커서 위치 가져오기 오류: {e}")
            return (0, 0)

    def capture_text_via_clipboard(self) -> str:
        """
        클립보드를 이용한 텍스트 캡처

        동작 방식:
        1. 현재 클립보드 백업
        2. Ctrl+A (전체 선택)
        3. Ctrl+C (복사)
        4. 클립보드에서 텍스트 읽기
        5. 원래 클립보드 복원
        6. Ctrl+Z (되돌리기 - 선택 해제)

        반환값:
            캡처된 텍스트
        """
        captured_text = ""

        try:
            # 1. 현재 클립보드 백업
            try:
                old_clipboard = pyperclip.paste()
            except:
                old_clipboard = ""

            # 2. 클립보드 초기화
            pyperclip.copy("")

            # 3. 전체 선택 (Ctrl+A)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)

            # 4. 복사 (Ctrl+C)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.2)

            # 5. 클립보드에서 텍스트 읽기
            try:
                captured_text = pyperclip.paste()
            except:
                captured_text = ""

            # 6. 클립보드 복원
            pyperclip.copy(old_clipboard)

            # 7. 선택 해제 (Escape 또는 방향키)
            pyautogui.press('escape')
            time.sleep(0.05)

        except Exception as e:
            print(f"클립보드 캡처 오류: {e}")

        return captured_text

    def is_text_editor(self, window_info: dict) -> bool:
        """
        활성 윈도우가 텍스트 에디터인지 확인

        매개변수:
            window_info: 윈도우 정보 딕셔너리

        반환값:
            텍스트 에디터 여부
        """
        if not window_info:
            return False

        title = window_info.get("title", "").lower()
        class_name = window_info.get("class_name", "").lower()

        # 텍스트 에디터 판별 키워드
        editor_keywords = [
            "한글",  # 한글과컴퓨터
            "hwp",
            "word",
            "메모장",
            "notepad",
            "sublime",
            "vscode",
            "code",
            "atom",
            "notepad++",
            "editplus"
        ]

        for keyword in editor_keywords:
            if keyword in title or keyword in class_name:
                return True

        return False

    def set_text_change_callback(self, callback: Callable):
        """
        텍스트 변경 콜백 설정

        매개변수:
            callback: 텍스트 변경 시 실행할 함수 (인자: new_text)
        """
        self.text_change_callback = callback

    def set_cursor_change_callback(self, callback: Callable):
        """
        커서 위치 변경 콜백 설정

        매개변수:
            callback: 커서 변경 시 실행할 함수 (인자: x, y)
        """
        self.cursor_change_callback = callback

    def _monitoring_loop(self):
        """모니터링 루프 (별도 스레드에서 실행)"""
        print("텍스트 모니터링 시작...")

        while self.is_monitoring:
            try:
                # 활성 윈도우 확인
                window_info = self.get_active_window()

                # 텍스트 에디터인 경우에만 모니터링
                if window_info and self.is_text_editor(window_info):
                    # 커서 위치 감지
                    cursor_pos = self.get_cursor_position()
                    if cursor_pos != self.last_cursor_pos:
                        self.last_cursor_pos = cursor_pos
                        if self.cursor_change_callback:
                            self.cursor_change_callback(cursor_pos[0], cursor_pos[1])

                    # 텍스트 변경 감지
                    current_time = time.time()
                    if current_time - self.last_change_time >= self.debounce_time:
                        # Debounce 시간이 지났으면 텍스트 캡처
                        captured_text = self.capture_text_via_clipboard()

                        if captured_text and captured_text != self.last_text:
                            self.last_text = captured_text
                            self.last_change_time = current_time

                            if self.text_change_callback:
                                self.text_change_callback(captured_text)

            except Exception as e:
                print(f"모니터링 루프 오류: {e}")

            # 대기
            time.sleep(self.check_interval)

        print("텍스트 모니터링 종료")

    def start_monitoring(self):
        """모니터링 시작"""
        if self.is_monitoring:
            print("모니터링이 이미 실행 중입니다.")
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        print("모니터링 중지됨")

    def get_last_text(self) -> str:
        """
        마지막으로 캡처된 텍스트 가져오기

        반환값:
            마지막 텍스트
        """
        return self.last_text

    def force_capture(self) -> str:
        """
        즉시 텍스트 캡처 (debounce 무시)

        반환값:
            캡처된 텍스트
        """
        return self.capture_text_via_clipboard()
