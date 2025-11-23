"""
메인 에디터 윈도우

역할:
- 텍스트 입력 인터페이스 제공
- 실시간 문법 검사 표시
- 제안 팝업 표시
- 툴바 및 메뉴 제공

주요 컴포넌트:
1. CTkTextbox: 텍스트 에디터
2. 사이드 패널: 오류 목록, 제안 표시
3. 툴바: 저장, 불러오기, 설정 버튼

유지보수 방법:
- UI 색상 변경: config.COLORS 수정
- 새로운 버튼 추가: _create_toolbar() 메서드에 버튼 추가
- 단축키 추가: _setup_bindings() 메서드 수정
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
from typing import Optional
import config
from ai.grammar_checker import GrammarChecker
from ai.sentence_suggester import SentenceSuggester
from database.db_manager import DatabaseManager


class EditorWindow(ctk.CTk):
    """메인 에디터 윈도우 클래스"""
    
    def __init__(self):
        """에디터 윈도우 초기화"""
        super().__init__()
        
        # 윈도우 설정
        self.title(config.WINDOW_TITLE)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        
        # CustomTkinter 테마 설정
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 모듈 초기화
        self.grammar_checker = GrammarChecker()
        self.sentence_suggester = SentenceSuggester()
        self.db_manager = DatabaseManager()
        
        # 상태 변수
        self.current_doc_id = None
        self.is_checking = False
        self.last_check_text = ""
        
        # UI 생성
        self._create_ui()
        self._setup_bindings()
        
        # 환영 메시지
        self._show_welcome_message()
    
    def _create_ui(self):
        """UI 컴포넌트 생성"""
        
        # 메인 컨테이너 (Grid 레이아웃)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 1. 툴바 생성
        self._create_toolbar()
        
        # 2. 사이드바 생성 (왼쪽)
        self._create_sidebar()
        
        # 3. 메인 에디터 생성 (중앙)
        self._create_editor()
        
        # 4. 제안 패널 생성 (오른쪽)
        self._create_suggestion_panel()
        
        # 5. 상태바 생성 (하단)
        self._create_statusbar()
    
    def _create_toolbar(self):
        """툴바 생성"""
        toolbar = ctk.CTkFrame(self, height=50, corner_radius=0)
        toolbar.grid(row=0, column=0, columnspan=3, sticky="ew", padx=0, pady=0)
        
        # 버튼들
        btn_new = ctk.CTkButton(
            toolbar,
            text="새 문서",
            width=100,
            command=self._new_document
        )
        btn_new.pack(side="left", padx=5, pady=10)
        
        btn_save = ctk.CTkButton(
            toolbar,
            text="저장",
            width=100,
            command=self._save_document
        )
        btn_save.pack(side="left", padx=5, pady=10)
        
        btn_load = ctk.CTkButton(
            toolbar,
            text="불러오기",
            width=100,
            command=self._load_document
        )
        btn_load.pack(side="left", padx=5, pady=10)
        
        btn_check = ctk.CTkButton(
            toolbar,
            text="문법 검사",
            width=100,
            command=self._manual_grammar_check,
            fg_color=config.COLORS["primary"]
        )
        btn_check.pack(side="left", padx=5, pady=10)
        
        btn_suggest = ctk.CTkButton(
            toolbar,
            text="문장 제안",
            width=100,
            command=self._show_suggestions,
            fg_color=config.COLORS["success"]
        )
        btn_suggest.pack(side="left", padx=5, pady=10)
    
    def _create_sidebar(self):
        """사이드바 생성 (문서 목록 및 오류 표시)"""
        sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        sidebar.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        sidebar.grid_propagate(False)
        
        # 제목
        label = ctk.CTkLabel(
            sidebar,
            text="문법 오류",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.pack(pady=10, padx=10)
        
        # 오류 목록 (스크롤 가능한 프레임)
        self.error_frame = ctk.CTkScrollableFrame(sidebar)
        self.error_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 초기 메시지
        self.no_error_label = ctk.CTkLabel(
            self.error_frame,
            text="오류가 없습니다",
            text_color="gray"
        )
        self.no_error_label.pack(pady=20)
    
    def _create_editor(self):
        """메인 텍스트 에디터 생성"""
        editor_frame = ctk.CTkFrame(self, corner_radius=0)
        editor_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        editor_frame.grid_rowconfigure(0, weight=1)
        editor_frame.grid_columnconfigure(0, weight=1)
        
        # 텍스트 박스
        self.text_editor = ctk.CTkTextbox(
            editor_frame,
            font=ctk.CTkFont(size=14),
            wrap="word",
            undo=True
        )
        self.text_editor.grid(row=0, column=0, sticky="nsew")
        
        # 플레이스홀더 텍스트
        self.text_editor.insert("1.0", "여기에 글을 작성하세요...")
        self.text_editor.bind("<Key>", self._on_text_change)
    
    def _create_suggestion_panel(self):
        """제안 패널 생성 (오른쪽)"""
        panel = ctk.CTkFrame(self, width=300, corner_radius=0)
        panel.grid(row=1, column=2, sticky="nsew", padx=0, pady=0)
        panel.grid_propagate(False)
        
        # 제목
        label = ctk.CTkLabel(
            panel,
            text="AI 제안",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.pack(pady=10, padx=10)
        
        # 제안 프레임
        self.suggestion_frame = ctk.CTkScrollableFrame(panel)
        self.suggestion_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 초기 메시지
        info_label = ctk.CTkLabel(
            self.suggestion_frame,
            text="'문장 제안' 버튼을 클릭하여\n다음 문장을 제안받으세요",
            text_color="gray",
            wraplength=250
        )
        info_label.pack(pady=20)
    
    def _create_statusbar(self):
        """상태바 생성"""
        statusbar = ctk.CTkFrame(self, height=30, corner_radius=0)
        statusbar.grid(row=2, column=0, columnspan=3, sticky="ew")
        
        self.status_label = ctk.CTkLabel(
            statusbar,
            text="준비됨",
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # 글자 수 표시
        self.char_count_label = ctk.CTkLabel(
            statusbar,
            text="0자",
            anchor="e"
        )
        self.char_count_label.pack(side="right", padx=10, pady=5)
    
    def _setup_bindings(self):
        """키보드 단축키 설정"""
        # Ctrl+S: 저장
        self.bind("<Control-s>", lambda e: self._save_document())
        
        # Ctrl+N: 새 문서
        self.bind("<Control-n>", lambda e: self._new_document())
        
        # Ctrl+O: 열기
        self.bind("<Control-o>", lambda e: self._load_document())
    
    def _show_welcome_message(self):
        """환영 메시지 표시"""
        welcome = """Sollidly에 오신 것을 환영합니다!

AI 기반 한국어 글쓰기 보조 도구입니다.

주요 기능:
- 실시간 문법 검사
- 다음 문장 제안
- 논리 구조 분석

시작하려면 텍스트를 입력하세요."""
        
        self.text_editor.delete("1.0", "end")
        self.text_editor.insert("1.0", welcome)
        self._update_status("환영합니다!")
    
    def _on_text_change(self, event=None):
        """텍스트 변경 이벤트 처리"""
        # 글자 수 업데이트
        text = self.text_editor.get("1.0", "end-1c")
        char_count = len(text)
        self.char_count_label.configure(text=f"{char_count}자")
        
        # 실시간 문법 검사 (일정 시간 후)
        if hasattr(self, '_check_timer'):
            self.after_cancel(self._check_timer)
        
        self._check_timer = self.after(2000, self._auto_grammar_check)
    
    def _auto_grammar_check(self):
        """자동 문법 검사 (타이핑 후 2초 뒤)"""
        text = self.text_editor.get("1.0", "end-1c").strip()
        
        # 텍스트가 변경되지 않았으면 스킵
        if text == self.last_check_text or not text:
            return
        
        self.last_check_text = text
        self._update_status("문법 검사 중...")
        
        # 백그라운드에서 검사
        threading.Thread(
            target=self._perform_grammar_check,
            args=(text,),
            daemon=True
        ).start()
    
    def _manual_grammar_check(self):
        """수동 문법 검사 (버튼 클릭)"""
        text = self.text_editor.get("1.0", "end-1c").strip()
        
        if not text:
            messagebox.showwarning("경고", "검사할 텍스트를 입력하세요.")
            return
        
        self._update_status("문법 검사 중...")
        
        threading.Thread(
            target=self._perform_grammar_check,
            args=(text,),
            daemon=True
        ).start()
    
    def _perform_grammar_check(self, text: str):
        """문법 검사 수행 (백그라운드)"""
        errors = self.grammar_checker.check_all(text)
        
        # UI 업데이트는 메인 스레드에서
        self.after(0, lambda: self._display_errors(errors))
    
    def _display_errors(self, errors: list):
        """오류 목록 표시"""
        # 기존 오류 제거
        for widget in self.error_frame.winfo_children():
            widget.destroy()
        
        if not errors:
            self.no_error_label = ctk.CTkLabel(
                self.error_frame,
                text="오류가 없습니다!",
                text_color="green"
            )
            self.no_error_label.pack(pady=20)
            self._update_status("문법 검사 완료 - 오류 없음")
        else:
            for i, error in enumerate(errors):
                self._create_error_item(error, i)
            
            self._update_status(f"문법 검사 완료 - {len(errors)}개 오류 발견")
    
    def _create_error_item(self, error: dict, index: int):
        """개별 오류 아이템 생성"""
        frame = ctk.CTkFrame(self.error_frame, corner_radius=5)
        frame.pack(fill="x", padx=5, pady=5)
        
        # 오류 유형
        type_label = ctk.CTkLabel(
            frame,
            text=f"[{error.get('type', '기타')}]",
            font=ctk.CTkFont(weight="bold"),
            text_color=config.COLORS["error"]
        )
        type_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        # 원본 텍스트
        original_label = ctk.CTkLabel(
            frame,
            text=f"원본: {error.get('original', '')}",
            wraplength=200,
            anchor="w"
        )
        original_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        # 수정안
        if error.get('correction'):
            correction_label = ctk.CTkLabel(
                frame,
                text=f"수정: {error['correction']}",
                wraplength=200,
                anchor="w",
                text_color=config.COLORS["success"]
            )
            correction_label.pack(anchor="w", padx=10, pady=(5, 10))
    
    def _show_suggestions(self):
        """문장 제안 표시"""
        text = self.text_editor.get("1.0", "end-1c").strip()
        
        if not text:
            messagebox.showwarning("경고", "먼저 텍스트를 입력하세요.")
            return
        
        self._update_status("문장 제안 생성 중...")
        
        threading.Thread(
            target=self._generate_suggestions,
            args=(text,),
            daemon=True
        ).start()
    
    def _generate_suggestions(self, text: str):
        """문장 제안 생성 (백그라운드)"""
        suggestions = self.sentence_suggester.suggest_next_sentence(
            text,
            num_suggestions=config.SUGGESTION["max_suggestions"]
        )
        
        self.after(0, lambda: self._display_suggestions(suggestions))
    
    def _display_suggestions(self, suggestions: list):
        """제안 표시"""
        # 기존 제안 제거
        for widget in self.suggestion_frame.winfo_children():
            widget.destroy()
        
        if not suggestions:
            label = ctk.CTkLabel(
                self.suggestion_frame,
                text="제안을 생성할 수 없습니다",
                text_color="gray"
            )
            label.pack(pady=20)
            self._update_status("제안 생성 실패")
            return
        
        for i, suggestion in enumerate(suggestions, 1):
            self._create_suggestion_item(suggestion, i)
        
        self._update_status(f"{len(suggestions)}개 제안 생성 완료")
    
    def _create_suggestion_item(self, suggestion: str, index: int):
        """개별 제안 아이템 생성"""
        frame = ctk.CTkFrame(self.suggestion_frame, corner_radius=5)
        frame.pack(fill="x", padx=5, pady=5)
        
        # 제안 번호
        num_label = ctk.CTkLabel(
            frame,
            text=f"제안 {index}",
            font=ctk.CTkFont(weight="bold")
        )
        num_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # 제안 내용
        text_label = ctk.CTkLabel(
            frame,
            text=suggestion,
            wraplength=250,
            anchor="w",
            justify="left"
        )
        text_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        # 적용 버튼
        apply_btn = ctk.CTkButton(
            frame,
            text="적용",
            width=80,
            height=28,
            command=lambda s=suggestion: self._apply_suggestion(s)
        )
        apply_btn.pack(anchor="e", padx=10, pady=(0, 10))
    
    def _apply_suggestion(self, suggestion: str):
        """제안 적용"""
        current_text = self.text_editor.get("1.0", "end-1c")
        new_text = current_text.rstrip() + " " + suggestion
        
        self.text_editor.delete("1.0", "end")
        self.text_editor.insert("1.0", new_text)
        
        self._update_status("제안이 적용되었습니다")
    
    def _new_document(self):
        """새 문서 생성"""
        if messagebox.askyesno("확인", "새 문서를 만들시겠습니까?\n저장하지 않은 내용은 사라집니다."):
            self.text_editor.delete("1.0", "end")
            self.current_doc_id = None
            self._update_status("새 문서")
    
    def _save_document(self):
        """문서 저장"""
        text = self.text_editor.get("1.0", "end-1c").strip()
        
        if not text:
            messagebox.showwarning("경고", "저장할 내용이 없습니다.")
            return
        
        # 제목 입력 다이얼로그
        title = ctk.CTkInputDialog(
            text="문서 제목을 입력하세요:",
            title="문서 저장"
        ).get_input()
        
        if title:
            if self.current_doc_id:
                self.db_manager.update_document(self.current_doc_id, title, text)
                messagebox.showinfo("성공", "문서가 업데이트되었습니다.")
            else:
                doc_id = self.db_manager.save_document(title, text)
                self.current_doc_id = doc_id
                messagebox.showinfo("성공", "문서가 저장되었습니다.")
            
            self._update_status(f"'{title}' 저장됨")
    
    def _load_document(self):
        """문서 불러오기"""
        docs = self.db_manager.get_all_documents()
        
        if not docs:
            messagebox.showinfo("알림", "저장된 문서가 없습니다.")
            return
        
        # 문서 목록 다이얼로그
        doc_list = "\n".join([f"{d['id']}. {d['title']}" for d in docs])
        messagebox.showinfo("저장된 문서", doc_list)
        
        # ID 입력
        doc_id_str = ctk.CTkInputDialog(
            text="불러올 문서 ID를 입력하세요:",
            title="문서 불러오기"
        ).get_input()
        
        if doc_id_str and doc_id_str.isdigit():
            doc = self.db_manager.get_document(int(doc_id_str))
            
            if doc:
                self.text_editor.delete("1.0", "end")
                self.text_editor.insert("1.0", doc['content'])
                self.current_doc_id = doc['id']
                self._update_status(f"'{doc['title']}' 불러옴")
            else:
                messagebox.showerror("오류", "문서를 찾을 수 없습니다.")
    
    def _update_status(self, message: str):
        """상태바 업데이트"""
        self.status_label.configure(text=message)
    
    def on_closing(self):
        """윈도우 닫기 이벤트"""
        if messagebox.askokcancel("종료", "Sollidly를 종료하시겠습니까?"):
            self.db_manager.close()
            self.destroy()
