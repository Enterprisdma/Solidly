"""
동그라미 메뉴 모듈

역할:
- Alt+Q+Enter 시 커서 주변에 3개의 동그라미 메뉴 표시
- 부드러운 확대 애니메이션
- 클릭 이벤트 처리

메뉴 구성:
1. 종료 (빨간색 ❌)
2. 다음 글 제안 (파란색 ✍️)
3. 논리 구조 검사 (초록색 🔍)

사용 예:
    menu = CircleMenu(overlay_window, x, y)
    menu.show()
"""

import customtkinter as ctk
import tkinter as tk
from typing import Callable, Optional
import config
import math


class CircleMenu:
    """동그라미 메뉴 클래스"""

    def __init__(self, parent, x: int, y: int):
        """
        동그라미 메뉴 초기화

        매개변수:
            parent: 부모 윈도우 (오버레이)
            x: 중심 X 좌표
            y: 중심 Y 좌표
        """
        self.parent = parent
        self.center_x = x
        self.center_y = y
        self.is_visible = False

        # 설정 로드
        self.radius = config.CIRCLE_MENU["radius"]
        self.animation_duration = config.CIRCLE_MENU["animation_duration"]
        self.menu_items = config.CIRCLE_MENU["menu_items"]

        # 콜백
        self.on_exit_callback: Optional[Callable] = None
        self.on_suggest_callback: Optional[Callable] = None
        self.on_analyze_callback: Optional[Callable] = None

        # 메뉴 버튼들
        self.buttons = []
        self.animation_id = None

    def set_callbacks(self, on_exit: Callable, on_suggest: Callable, on_analyze: Callable):
        """
        콜백 함수 설정

        매개변수:
            on_exit: 종료 버튼 클릭 시
            on_suggest: 제안 버튼 클릭 시
            on_analyze: 분석 버튼 클릭 시
        """
        self.on_exit_callback = on_exit
        self.on_suggest_callback = on_suggest
        self.on_analyze_callback = on_analyze

    def _create_circle_button(self, item: dict, angle: float, delay: int) -> ctk.CTkButton:
        """
        동그라미 버튼 생성

        매개변수:
            item: 메뉴 아이템 정보
            angle: 배치 각도 (라디안)
            delay: 애니메이션 지연 시간 (ms)

        반환값:
            생성된 버튼
        """
        # 원형 배치 위치 계산
        distance = self.radius * 1.5  # 중심으로부터의 거리
        x = self.center_x + int(distance * math.cos(angle))
        y = self.center_y + int(distance * math.sin(angle))

        # 버튼 생성
        button = ctk.CTkButton(
            self.parent,
            text=f"{item['icon']}\n{item['name']}",
            width=self.radius * 2,
            height=self.radius * 2,
            corner_radius=self.radius,
            fg_color=item['color'],
            hover_color=self._darken_color(item['color']),
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self._on_button_click(item['name'])
        )

        # 초기에는 숨김 (애니메이션 준비)
        button.place(x=x, y=y, anchor="center")
        button.place_forget()

        return button

    def _darken_color(self, hex_color: str) -> str:
        """
        색상을 어둡게 만들기 (호버 효과용)

        매개변수:
            hex_color: HEX 색상 코드

        반환값:
            어두워진 색상
        """
        # 간단한 구현 (RGB 값에서 20% 감소)
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _on_button_click(self, button_name: str):
        """
        버튼 클릭 이벤트 처리

        매개변수:
            button_name: 클릭된 버튼 이름
        """
        # 메뉴 숨기기
        self.hide()

        # 해당 콜백 실행
        if button_name == "종료" and self.on_exit_callback:
            self.on_exit_callback()
        elif button_name == "다음 글 제안" and self.on_suggest_callback:
            self.on_suggest_callback()
        elif button_name == "논리 구조 검사" and self.on_analyze_callback:
            self.on_analyze_callback()

    def show(self):
        """메뉴 표시 (애니메이션과 함께)"""
        if self.is_visible:
            return

        self.is_visible = True
        self.buttons.clear()

        # 3개의 버튼을 삼각형 배치 (위쪽부터 시계방향)
        angles = [
            -math.pi / 2,          # 위 (종료)
            math.pi / 6,           # 오른쪽 아래 (제안)
            5 * math.pi / 6        # 왼쪽 아래 (분석)
        ]

        # 버튼 생성
        for i, item in enumerate(self.menu_items):
            button = self._create_circle_button(item, angles[i], i * 50)
            self.buttons.append(button)

        # 애니메이션 시작
        self._animate_show(0, 0)

    def _animate_show(self, step: int, max_steps: int = 10):
        """
        확대 애니메이션

        매개변수:
            step: 현재 애니메이션 단계
            max_steps: 전체 애니메이션 단계 수
        """
        if step > max_steps:
            return

        # Easing function (ease-out)
        progress = step / max_steps
        scale = self._ease_out_back(progress)

        # 각 버튼의 위치와 크기 조정
        angles = [-math.pi / 2, math.pi / 6, 5 * math.pi / 6]

        for i, button in enumerate(self.buttons):
            distance = self.radius * 1.5 * scale
            x = self.center_x + int(distance * math.cos(angles[i]))
            y = self.center_y + int(distance * math.sin(angles[i]))

            # 크기 조정
            size = int(self.radius * 2 * scale)
            button.configure(width=size, height=size, corner_radius=size // 2)

            # 위치 조정
            button.place(x=x, y=y, anchor="center")

            # 투명도 조정 (옵션)
            # button.configure(fg_color=...)

        # 다음 프레임
        delay = self.animation_duration // max_steps
        self.animation_id = self.parent.after(
            delay,
            lambda: self._animate_show(step + 1, max_steps)
        )

    def _ease_out_back(self, t: float) -> float:
        """
        Ease-out-back 이징 함수 (약간 튕기는 효과)

        매개변수:
            t: 진행도 (0.0 ~ 1.0)

        반환값:
            변환된 값
        """
        c1 = 1.70158
        c3 = c1 + 1

        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)

    def hide(self):
        """메뉴 숨기기"""
        if not self.is_visible:
            return

        self.is_visible = False

        # 애니메이션 취소
        if self.animation_id:
            self.parent.after_cancel(self.animation_id)
            self.animation_id = None

        # 버튼 제거
        for button in self.buttons:
            button.place_forget()
            button.destroy()

        self.buttons.clear()

    def toggle(self):
        """메뉴 토글 (표시/숨기기)"""
        if self.is_visible:
            self.hide()
        else:
            self.show()

    def update_position(self, x: int, y: int):
        """
        메뉴 위치 업데이트

        매개변수:
            x: 새 X 좌표
            y: 새 Y 좌표
        """
        self.center_x = x
        self.center_y = y

        # 메뉴가 표시 중이면 재배치
        if self.is_visible:
            self.hide()
            self.show()
