"""
환영 화면 (초기 설정)

역할:
- 솔리드리 로고 표시
- 시작하기 버튼 애니메이션
- OpenAI API 키 입력
- 환영 메시지 표시

사용 예:
    welcome = WelcomeWindow()
    api_key = welcome.run()  # API 키 반환 (또는 None)
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional
import config
import os


class WelcomeWindow(ctk.CTk):
    """초기 설정 윈도우"""

    def __init__(self):
        """윈도우 초기화"""
        super().__init__()

        # 윈도우 설정
        self.title("Sollidly - 환영합니다")
        self.geometry("600x500")
        self.resizable(False, False)

        # 다크 모드
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 상태
        self.current_step = 0  # 0: 로고, 1: API 키, 2: 환영 메시지
        self.api_key = ""
        self.completed = False

        # 중앙 정렬
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 메인 프레임
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0)

        # 첫 화면 표시
        self._show_logo_screen()

    def _show_logo_screen(self):
        """로고 화면"""
        # 기존 위젯 제거
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # 로고 (큰 텍스트)
        logo_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        logo_frame.pack(pady=50)

        # "Sollidly" 텍스트 로고
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="✍️ Sollidly",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="#4A90E2"
        )
        logo_label.pack()

        # 부제목
        subtitle = ctk.CTkLabel(
            logo_frame,
            text="AI 기반 글쓰기 보조 도구",
            font=ctk.CTkFont(size=16),
            text_color="#888888"
        )
        subtitle.pack(pady=10)

        # 시작하기 버튼 (애니메이션)
        self.start_button = ctk.CTkButton(
            self.main_frame,
            text="시작하기",
            font=ctk.CTkFont(size=18, weight="bold"),
            width=200,
            height=50,
            corner_radius=25,
            fg_color="#4A90E2",
            hover_color="#3A7FC2",
            command=self._on_start_clicked
        )

        # 버튼 초기 위치 (아래)
        self.start_button.pack(pady=(100, 0))
        self.start_button.place_forget()  # 일단 숨김

        # 애니메이션 시작
        self._animate_button_appear()

    def _animate_button_appear(self):
        """버튼 나타나기 애니메이션 (밑에서 떠오르면서 페이드인)"""
        # 버튼을 화면 밖 아래에 배치
        window_height = 500
        button_start_y = window_height + 50
        button_end_y = 350

        # 애니메이션 단계
        steps = 20
        current_step = [0]  # mutable을 위해 리스트 사용

        def animate_step():
            if current_step[0] < steps:
                # Ease-out 함수
                progress = current_step[0] / steps
                eased = 1 - (1 - progress) ** 3

                # Y 위치 계산
                current_y = button_start_y - (button_start_y - button_end_y) * eased

                # 버튼 위치 업데이트
                self.start_button.place(
                    relx=0.5,
                    y=current_y,
                    anchor="center"
                )

                current_step[0] += 1
                self.after(20, animate_step)
            else:
                # 애니메이션 완료 - pack으로 전환
                self.start_button.place_forget()
                self.start_button.pack(pady=(100, 0))

        animate_step()

    def _on_start_clicked(self):
        """시작하기 버튼 클릭"""
        self.current_step = 1
        self._show_api_key_screen()

    def _show_api_key_screen(self):
        """API 키 입력 화면"""
        # 기존 위젯 제거
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # 제목
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="OpenAI API 키 설정",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(30, 10))

        # 설명
        desc_label = ctk.CTkLabel(
            self.main_frame,
            text="OpenAI API 키를 입력하지 않으면\n논리 구조 체킹 등 AI 기능이 제한됩니다.",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
            justify="center"
        )
        desc_label.pack(pady=10)

        # API 키 입력
        self.api_key_entry = ctk.CTkEntry(
            self.main_frame,
            width=400,
            height=40,
            placeholder_text="sk-...",
            font=ctk.CTkFont(size=14),
            show="*"  # 비밀번호처럼 숨김
        )
        self.api_key_entry.pack(pady=20)

        # 기존 API 키 로드 (있으면)
        if config.OPENAI_API_KEY:
            self.api_key_entry.insert(0, config.OPENAI_API_KEY)

        # 버튼 프레임
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(pady=30)

        # 건너뛰기 버튼
        skip_button = ctk.CTkButton(
            button_frame,
            text="건너뛰기",
            width=150,
            height=40,
            fg_color="gray",
            hover_color="darkgray",
            command=self._on_skip_clicked
        )
        skip_button.pack(side="left", padx=10)

        # 계속하기 버튼
        continue_button = ctk.CTkButton(
            button_frame,
            text="계속하기",
            width=150,
            height=40,
            fg_color="#4A90E2",
            hover_color="#3A7FC2",
            command=self._on_continue_clicked
        )
        continue_button.pack(side="left", padx=10)

        # Enter 키로도 계속 가능
        self.api_key_entry.bind("<Return>", lambda e: self._on_continue_clicked())

    def _on_skip_clicked(self):
        """건너뛰기"""
        self.api_key = ""
        self._save_api_key("")
        self._show_welcome_message()

    def _on_continue_clicked(self):
        """계속하기"""
        api_key = self.api_key_entry.get().strip()
        self.api_key = api_key
        self._save_api_key(api_key)
        self._show_welcome_message()

    def _save_api_key(self, api_key: str):
        """API 키 .env 파일에 저장"""
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

        # 기존 .env 읽기
        env_lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                env_lines = f.readlines()

        # OPENAI_API_KEY 업데이트 또는 추가
        found = False
        for i, line in enumerate(env_lines):
            if line.startswith("OPENAI_API_KEY="):
                env_lines[i] = f"OPENAI_API_KEY={api_key}\n"
                found = True
                break

        if not found:
            env_lines.append(f"OPENAI_API_KEY={api_key}\n")

        # .env 파일 쓰기
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(env_lines)

        # config 업데이트
        config.OPENAI_API_KEY = api_key

    def _show_welcome_message(self):
        """환영 메시지 (페이드아웃)"""
        # 기존 위젯 제거
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # 메시지
        message_label = ctk.CTkLabel(
            self.main_frame,
            text="이제 멋진 글을 만들어 보세요!",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#4A90E2"
        )
        message_label.pack(pady=(150, 20))

        # 단축키 안내
        hotkey_text = f"Ctrl+Shift+S로 도움을 요청할 수 있습니다"
        hotkey_label = ctk.CTkLabel(
            self.main_frame,
            text=hotkey_text,
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        )
        hotkey_label.pack()

        # 2초 후 페이드아웃
        self.after(2000, lambda: self._fadeout_and_close(message_label, hotkey_label))

    def _fadeout_and_close(self, *widgets):
        """페이드아웃 애니메이션 후 종료"""
        # CustomTkinter는 알파 투명도를 직접 지원하지 않으므로
        # 윈도우 전체를 페이드아웃
        alpha = 1.0
        steps = 20

        def fade_step(current_alpha):
            if current_alpha > 0:
                self.attributes("-alpha", current_alpha)
                self.after(30, lambda: fade_step(current_alpha - (1.0 / steps)))
            else:
                self.completed = True
                self.destroy()

        fade_step(alpha)

    def run(self) -> Optional[str]:
        """
        윈도우 실행 및 API 키 반환

        반환값:
            입력된 API 키 (또는 None)
        """
        self.mainloop()
        return self.api_key if hasattr(self, 'api_key') else None


# 테스트용
if __name__ == "__main__":
    window = WelcomeWindow()
    api_key = window.run()
    print(f"API 키: {api_key}")
