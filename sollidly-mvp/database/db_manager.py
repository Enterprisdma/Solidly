"""
데이터베이스 관리 모듈

역할:
- SQLite 데이터베이스 초기화
- 사용자 설정 저장/로드
- 작성 기록 저장/조회

주요 테이블:
1. settings: 사용자 설정 (테마, 자동 저장 등)
2. documents: 저장된 문서들
3. grammar_logs: 문법 오류 기록 (학습용)

유지보수 방법:
- 새로운 테이블 추가: create_tables() 메서드에 CREATE TABLE 추가
- 데이터 조회: execute_query() 메서드 사용
- 트랜잭션: commit() 자동 처리
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import config


class DatabaseManager:
    """데이터베이스 관리 클래스"""
    
    def __init__(self, db_path: str = config.DB_PATH):
        """
        데이터베이스 매니저 초기화
        
        매개변수:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """데이터베이스 연결"""
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
    
    def create_tables(self):
        """필요한 테이블 생성"""
        
        # 사용자 설정 테이블
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 문서 저장 테이블
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 문법 오류 로그 테이블 (학습 데이터)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS grammar_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_text TEXT NOT NULL,
                error_type TEXT NOT NULL,
                correction TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.connection.commit()
    
    def save_setting(self, key: str, value: str):
        """
        설정 저장
        
        매개변수:
            key: 설정 키 (예: "theme", "auto_save")
            value: 설정 값
        """
        self.cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (key, value, datetime.now()))
        self.connection.commit()
    
    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        """
        설정 불러오기
        
        매개변수:
            key: 설정 키
            default: 기본값 (설정이 없을 때 반환)
        
        반환값:
            설정 값 또는 기본값
        """
        self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = self.cursor.fetchone()
        return result[0] if result else default
    
    def save_document(self, title: str, content: str) -> int:
        """
        문서 저장
        
        매개변수:
            title: 문서 제목
            content: 문서 내용
        
        반환값:
            저장된 문서의 ID
        """
        self.cursor.execute("""
            INSERT INTO documents (title, content)
            VALUES (?, ?)
        """, (title, content))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_document(self, doc_id: int) -> Optional[Dict]:
        """
        문서 불러오기
        
        매개변수:
            doc_id: 문서 ID
        
        반환값:
            문서 딕셔너리 또는 None
        """
        self.cursor.execute("""
            SELECT id, title, content, created_at, updated_at
            FROM documents WHERE id = ?
        """, (doc_id,))
        result = self.cursor.fetchone()
        
        if result:
            return {
                "id": result[0],
                "title": result[1],
                "content": result[2],
                "created_at": result[3],
                "updated_at": result[4]
            }
        return None
    
    def get_all_documents(self) -> List[Dict]:
        """
        모든 문서 목록 가져오기
        
        반환값:
            문서 딕셔너리 리스트
        """
        self.cursor.execute("""
            SELECT id, title, created_at, updated_at
            FROM documents
            ORDER BY updated_at DESC
        """)
        results = self.cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "title": row[1],
                "created_at": row[2],
                "updated_at": row[3]
            }
            for row in results
        ]
    
    def update_document(self, doc_id: int, title: str, content: str):
        """
        문서 업데이트
        
        매개변수:
            doc_id: 문서 ID
            title: 새 제목
            content: 새 내용
        """
        self.cursor.execute("""
            UPDATE documents
            SET title = ?, content = ?, updated_at = ?
            WHERE id = ?
        """, (title, content, datetime.now(), doc_id))
        self.connection.commit()
    
    def delete_document(self, doc_id: int):
        """
        문서 삭제
        
        매개변수:
            doc_id: 삭제할 문서 ID
        """
        self.cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        self.connection.commit()
    
    def log_grammar_error(self, original: str, error_type: str, correction: str = None):
        """
        문법 오류 기록 (학습 데이터로 활용)
        
        매개변수:
            original: 원본 텍스트
            error_type: 오류 유형
            correction: 수정 내용
        """
        self.cursor.execute("""
            INSERT INTO grammar_logs (original_text, error_type, correction)
            VALUES (?, ?, ?)
        """, (original, error_type, correction))
        self.connection.commit()
    
    def close(self):
        """데이터베이스 연결 종료"""
        if self.connection:
            self.connection.close()
