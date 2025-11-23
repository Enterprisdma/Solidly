"""
개선된 텍스트 모니터링 모듈

개선 사항:
- Windows UI Automation을 사용한 비침습적 텍스트 가져오기
- 클립보드를 사용하지 않음 (사용자 입력 방해 없음)
- 더 안정적인 텍스트 캡처

주요 기능:
1. get_active_window(): 활성 윈도우 정보 가져오기
2. get_cursor_position(): 커서 위치 가져오기
3. capture_text_non_invasive(): 비침습적 텍스트 캡처
4. start_monitoring(): 모니터링 시작
"""

import win32gui
import win32api
import win32con
import win32process
import pyautogui
import threading
import time
from typing import Callable, Optional, Tuple
import config


class ImprovedTextMonitor:
    """개선된 텍스트 모니터링 클래스"""

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
        self.is_typing = False
        self.typing_timeout = 3.0  # 타이핑 감지 타임아웃

    def get_active_window(self) -> dict:
        """
        현재 활성화된 윈도우 정보 가져오기

        반환값:
            윈도우 정보 딕셔너리
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

        반환값:
            (x, y) 좌표 튜플
        """
        try:
            return pyautogui.position()
        except Exception as e:
            print(f"커서 위치 가져오기 오류: {e}")
            return (0, 0)

    def capture_text_via_window_message(self, hwnd) -> str:
        """
        Windows 메시지를 통한 텍스트 캡처 (비침습적)

        WM_GETTEXT 메시지를 사용하여 읽기 전용으로 텍스트 가져오기
        사용자 입력을 방해하지 않음

        매개변수:
            hwnd: 윈도우 핸들

        반환값:
            캡처된 텍스트
        """
        try:
            import ctypes
            from ctypes import wintypes

            # WM_GETTEXT 메시지 상수
            WM_GETTEXT = 0x000D
            buffer_size = 65536  # 64KB

            # 텍스트 버퍼 생성
            buffer = ctypes.create_unicode_buffer(buffer_size)

            # WM_GETTEXT 메시지 전송
            length = ctypes.windll.user32.SendMessageW(
                hwnd,
                WM_GETTEXT,
                buffer_size,
                ctypes.byref(buffer)
            )

            if length > 0:
                return buffer.value
            else:
                return ""

        except Exception as e:
            print(f"WM_GETTEXT 캡처 오류: {e}")
            return ""

    def capture_text_via_uiautomation(self, hwnd) -> str:
        """
        UI Automation을 통한 텍스트 캡처 (고급)

        더 복잡한 에디터에서도 작동

        매개변수:
            hwnd: 윈도우 핸들

        반환값:
            캡처된 텍스트
        """
        try:
            import comtypes.client as cc

            # UI Automation 초기화
            UIAutomationClient = cc.GetModule('UIAutomationCore.dll')
            uia = cc.CreateObject("{ff48dba4-60ef-4201-aa87-54103eef594e}", interface=UIAutomationClient.IUIAutomation)

            # 핸들로부터 Element 가져오기
            element = uia.ElementFromHandle(hwnd)

            # ValuePattern 시도 (텍스트 필드)
            try:
                value_pattern = element.GetCurrentPattern(UIAutomationClient.UIA_ValuePatternId)
                text = value_pattern.CurrentValue
                return text
            except:
                pass

            # TextPattern 시도 (리치 텍스트)
            try:
                text_pattern = element.GetCurrentPattern(UIAutomationClient.UIA_TextPatternId)
                text_range = text_pattern.DocumentRange
                text = text_range.GetText(-1)
                return text
            except:
                pass

            return ""

        except Exception as e:
            print(f"UI Automation 캡처 오류: {e}")
            return ""

    def capture_text_smart(self, hwnd) -> str:
        """
        스마트 텍스트 캡처 (여러 방법 시도)

        1. WM_GETTEXT (가장 빠르고 안전)
        2. UI Automation (복잡한 컨트롤)
        3. 실패 시 빈 문자열

        매개변수:
            hwnd: 윈도우 핸들

        반환값:
            캡처된 텍스트
        """
        # 방법 1: WM_GETTEXT
        text = self.capture_text_via_window_message(hwnd)
        if text:
            return text

        # 방법 2: UI Automation
        text = self.capture_text_via_uiautomation(hwnd)
        if text:
            return text

        return ""

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
            "한글", "hwp", "word", "메모장", "notepad",
            "sublime", "vscode", "code", "atom", "notepad++", "editplus"
        ]

        for keyword in editor_keywords:
            if keyword in title or keyword in class_name:
                return True

        return False

    def detect_typing(self) -> bool:
        """
        사용자가 현재 타이핑 중인지 감지

        반환값:
            타이핑 중이면 True
        """
        current_time = time.time()

        # 최근에 텍스트가 변경되었으면 타이핑 중
        if current_time - self.last_change_time < self.typing_timeout:
            return True

        return False

    def set_text_change_callback(self, callback: Callable):
        """텍스트 변경 콜백 설정"""
        self.text_change_callback = callback

    def set_cursor_change_callback(self, callback: Callable):
        """커서 위치 변경 콜백 설정"""
        self.cursor_change_callback = callback

    def _monitoring_loop(self):
        """모니터링 루프 (별도 스레드에서 실행)"""
        print("개선된 텍스트 모니터링 시작...")

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

                    # 타이핑 중인지 확인
                    if not self.detect_typing():
                        # 타이핑 멈춤 - 텍스트 캡처
                        current_time = time.time()
                        if current_time - self.last_change_time >= self.debounce_time:
                            # 비침습적 텍스트 캡처
                            hwnd = window_info["hwnd"]
                            captured_text = self.capture_text_smart(hwnd)

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
        """마지막으로 캡처된 텍스트 가져오기"""
        return self.last_text

    def force_capture(self, hwnd) -> str:
        """즉시 텍스트 캡처 (debounce 무시)"""
        return self.capture_text_smart(hwnd)
