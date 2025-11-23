"""
키보드 후킹 모듈

역할:
- 전역 키보드 단축키 감지
- Alt+Q+Enter 조합 감지
- 단축키 콜백 실행

주요 기능:
1. start(): 키보드 후킹 시작
2. stop(): 키보드 후킹 중지
3. set_callback(): 단축키 감지 시 실행할 콜백 설정

사용 예:
    hook = KeyboardHook()
    hook.set_callback(on_hotkey_pressed)
    hook.start()
"""

from pynput import keyboard
from typing import Callable, Optional, Set
import config
import threading


class KeyboardHook:
    """전역 키보드 후킹 클래스"""

    def __init__(self):
        """키보드 후크 초기화"""
        self.listener: Optional[keyboard.Listener] = None
        self.callback: Optional[Callable] = None
        self.pressed_keys: Set[keyboard.Key] = set()
        self.is_running = False

        # 설정에서 단축키 로드
        self.hotkey_combo = self._parse_hotkey(config.HOTKEYS["toggle_menu"])
        self.exit_combo = self._parse_hotkey(config.HOTKEYS["exit_app"])

    def _parse_hotkey(self, keys: list) -> Set:
        """
        단축키 문자열 리스트를 pynput Key 객체로 변환

        매개변수:
            keys: 키 이름 리스트 (예: ["alt", "q", "enter"])

        반환값:
            Key 객체 set
        """
        parsed_keys = set()

        for key_name in keys:
            key_name = key_name.lower()

            # 특수 키 매핑
            if key_name == "alt":
                parsed_keys.add(keyboard.Key.alt)
            elif key_name == "ctrl":
                parsed_keys.add(keyboard.Key.ctrl)
            elif key_name == "shift":
                parsed_keys.add(keyboard.Key.shift)
            elif key_name == "enter":
                parsed_keys.add(keyboard.Key.enter)
            elif key_name == "esc":
                parsed_keys.add(keyboard.Key.esc)
            elif key_name == "space":
                parsed_keys.add(keyboard.Key.space)
            else:
                # 일반 키 (a-z, 0-9 등)
                try:
                    parsed_keys.add(keyboard.KeyCode.from_char(key_name))
                except:
                    print(f"알 수 없는 키: {key_name}")

        return parsed_keys

    def set_callback(self, callback: Callable):
        """
        단축키 감지 시 실행할 콜백 설정

        매개변수:
            callback: 단축키 감지 시 실행할 함수
        """
        self.callback = callback

    def set_exit_callback(self, callback: Callable):
        """
        종료 단축키 감지 시 실행할 콜백 설정

        매개변수:
            callback: 종료 단축키 감지 시 실행할 함수
        """
        self.exit_callback = callback

    def _on_press(self, key):
        """
        키 눌림 이벤트 처리

        매개변수:
            key: 눌린 키
        """
        try:
            # KeyCode를 정규화 (대소문자 구분 없이)
            if hasattr(key, 'char') and key.char:
                key = keyboard.KeyCode.from_char(key.char.lower())

            self.pressed_keys.add(key)

            # 단축키 조합 확인
            if self.hotkey_combo.issubset(self.pressed_keys):
                if self.callback:
                    # 콜백을 별도 스레드에서 실행 (논블로킹)
                    threading.Thread(target=self.callback, daemon=True).start()
                    # 키 초기화 (중복 호출 방지)
                    self.pressed_keys.clear()

            # 종료 단축키 확인
            if self.exit_combo.issubset(self.pressed_keys):
                if hasattr(self, 'exit_callback') and self.exit_callback:
                    threading.Thread(target=self.exit_callback, daemon=True).start()
                    self.pressed_keys.clear()

        except Exception as e:
            print(f"키 눌림 처리 오류: {e}")

    def _on_release(self, key):
        """
        키 떼기 이벤트 처리

        매개변수:
            key: 떼진 키
        """
        try:
            # KeyCode를 정규화
            if hasattr(key, 'char') and key.char:
                key = keyboard.KeyCode.from_char(key.char.lower())

            if key in self.pressed_keys:
                self.pressed_keys.remove(key)

        except Exception as e:
            print(f"키 떼기 처리 오류: {e}")

    def start(self):
        """키보드 후킹 시작"""
        if self.is_running:
            print("키보드 후킹이 이미 실행 중입니다.")
            return

        self.is_running = True
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
        print(f"키보드 후킹 시작: {config.HOTKEYS['toggle_menu']}")

    def stop(self):
        """키보드 후킹 중지"""
        if self.listener:
            self.listener.stop()
            self.is_running = False
            print("키보드 후킹 중지")

    def is_active(self) -> bool:
        """
        후킹 활성 상태 확인

        반환값:
            활성 상태 여부
        """
        return self.is_running
