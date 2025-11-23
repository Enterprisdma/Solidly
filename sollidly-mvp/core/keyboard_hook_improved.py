"""
개선된 키보드 후킹 모듈

개선 사항:
- keyboard 라이브러리 사용 (더 robust한 전역 후킹)
- pynput 실패 시 자동 fallback
- 관리자 권한 확인 및 안내

주요 기능:
1. start(): 키보드 후킹 시작
2. stop(): 키보드 후킹 중지
3. set_callback(): 단축키 감지 시 실행할 콜백 설정
"""

from typing import Callable, Optional
import config
import threading
import sys


class ImprovedKeyboardHook:
    """개선된 전역 키보드 후킹 클래스"""

    def __init__(self):
        """키보드 후크 초기화"""
        self.callback: Optional[Callable] = None
        self.exit_callback: Optional[Callable] = None
        self.is_running = False
        self.hook_method = None  # 'keyboard' or 'pynput'

        # 설정에서 단축키 로드
        self.hotkey_combo = config.HOTKEYS["toggle_menu"]  # ['ctrl', 'shift', 's']
        self.exit_combo = config.HOTKEYS["exit_app"]  # ['ctrl', 'shift', 'q']

        # 사용 가능한 라이브러리 확인
        self._detect_available_library()

    def _detect_available_library(self):
        """사용 가능한 키보드 라이브러리 감지"""
        # 1순위: keyboard 라이브러리 (더 robust)
        try:
            import keyboard
            self.hook_method = 'keyboard'
            print("✓ 키보드 후킹: keyboard 라이브러리 사용")
            return
        except ImportError:
            pass

        # 2순위: pynput
        try:
            from pynput import keyboard as pynput_keyboard
            self.hook_method = 'pynput'
            print("✓ 키보드 후킹: pynput 라이브러리 사용")
            return
        except ImportError:
            pass

        print("⚠ 경고: 키보드 후킹 라이브러리를 찾을 수 없습니다!")
        print("  pip install keyboard 또는 pip install pynput")
        self.hook_method = None

    def _check_admin_rights(self) -> bool:
        """관리자 권한 확인 (Windows)"""
        if sys.platform == 'win32':
            try:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                return False
        return True

    def set_callback(self, callback: Callable):
        """단축키 감지 시 실행할 콜백 설정"""
        self.callback = callback

    def set_exit_callback(self, callback: Callable):
        """종료 단축키 감지 시 실행할 콜백 설정"""
        self.exit_callback = callback

    def _format_hotkey_string(self, keys: list) -> str:
        """
        키 리스트를 keyboard 라이브러리 형식으로 변환

        예: ['ctrl', 'shift', 's'] -> 'ctrl+shift+s'
        """
        return '+'.join(keys)

    def _start_with_keyboard_lib(self):
        """keyboard 라이브러리를 사용한 후킹"""
        import keyboard

        # 관리자 권한 확인
        if not self._check_admin_rights():
            print("\n" + "=" * 60)
            print("⚠ 경고: 관리자 권한이 필요합니다!")
            print("=" * 60)
            print("전역 키보드 후킹을 위해 프로그램을 관리자 권한으로 실행하세요.")
            print("\n실행 방법:")
            print("1. 명령 프롬프트를 관리자 권한으로 실행")
            print("2. python main_new.py")
            print("=" * 60 + "\n")

        # 단축키 등록
        toggle_hotkey = self._format_hotkey_string(self.hotkey_combo)
        exit_hotkey = self._format_hotkey_string(self.exit_combo)

        def on_toggle():
            if self.callback:
                threading.Thread(target=self.callback, daemon=True).start()

        def on_exit():
            if self.exit_callback:
                threading.Thread(target=self.exit_callback, daemon=True).start()

        # 핫키 등록
        try:
            keyboard.add_hotkey(toggle_hotkey, on_toggle, suppress=False)
            keyboard.add_hotkey(exit_hotkey, on_exit, suppress=False)

            print(f"✓ 단축키 등록 완료:")
            print(f"  - {toggle_hotkey}: 메뉴 열기")
            print(f"  - {exit_hotkey}: 종료")

            self.is_running = True

        except Exception as e:
            print(f"✗ 단축키 등록 실패: {e}")
            print("  관리자 권한으로 프로그램을 실행해주세요.")

    def _start_with_pynput(self):
        """pynput을 사용한 후킹 (fallback)"""
        from pynput import keyboard

        pressed_keys = set()

        def parse_hotkey(keys: list):
            """단축키를 pynput Key 객체로 변환"""
            parsed_keys = set()
            for key_name in keys:
                key_name = key_name.lower()
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
                else:
                    try:
                        parsed_keys.add(keyboard.KeyCode.from_char(key_name))
                    except:
                        print(f"알 수 없는 키: {key_name}")
            return parsed_keys

        toggle_keys = parse_hotkey(self.hotkey_combo)
        exit_keys = parse_hotkey(self.exit_combo)

        def on_press(key):
            try:
                # 정규화
                if hasattr(key, 'char') and key.char:
                    key = keyboard.KeyCode.from_char(key.char.lower())

                pressed_keys.add(key)

                # 단축키 확인
                if toggle_keys.issubset(pressed_keys):
                    if self.callback:
                        threading.Thread(target=self.callback, daemon=True).start()
                    pressed_keys.clear()

                if exit_keys.issubset(pressed_keys):
                    if self.exit_callback:
                        threading.Thread(target=self.exit_callback, daemon=True).start()
                    pressed_keys.clear()

            except Exception as e:
                print(f"키 눌림 처리 오류: {e}")

        def on_release(key):
            try:
                if hasattr(key, 'char') and key.char:
                    key = keyboard.KeyCode.from_char(key.char.lower())
                if key in pressed_keys:
                    pressed_keys.remove(key)
            except Exception as e:
                print(f"키 떼기 처리 오류: {e}")

        # 리스너 시작
        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.listener.start()
        self.is_running = True

        print(f"✓ pynput 후킹 시작: {self.hotkey_combo}")

    def start(self):
        """키보드 후킹 시작"""
        if self.is_running:
            print("키보드 후킹이 이미 실행 중입니다.")
            return

        if self.hook_method is None:
            print("✗ 키보드 후킹을 시작할 수 없습니다. 라이브러리를 설치하세요.")
            return

        if self.hook_method == 'keyboard':
            self._start_with_keyboard_lib()
        elif self.hook_method == 'pynput':
            self._start_with_pynput()

    def stop(self):
        """키보드 후킹 중지"""
        if not self.is_running:
            return

        if self.hook_method == 'keyboard':
            import keyboard
            keyboard.unhook_all()

        elif self.hook_method == 'pynput':
            if hasattr(self, 'listener'):
                self.listener.stop()

        self.is_running = False
        print("키보드 후킹 중지")

    def is_active(self) -> bool:
        """후킹 활성 상태 확인"""
        return self.is_running
