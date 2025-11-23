"""
문법 검사 모듈

역할:
- 한국어 맞춤법 검사 (py-hanspell 사용)
- AI 기반 문법 오류 탐지 (OpenAI GPT 사용)
- 오류 수정 제안 생성

주요 기능:
1. check_grammar(): 텍스트 문법 검사
2. get_corrections(): 오류에 대한 수정 제안
3. explain_error(): 오류 설명 제공

유지보수 방법:
- API 키는 config.py에서 관리
- 새로운 오류 유형 추가: ERROR_TYPES 딕셔너리 수정
- 프롬프트 개선: _build_grammar_prompt() 메서드 수정
"""

from typing import List, Dict, Optional
from hanspell import spell_checker
import config

# OpenAI API 사용 (설치된 경우)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class GrammarChecker:
    """문법 검사 클래스"""
    
    # 오류 유형 정의
    ERROR_TYPES = {
        "spelling": "맞춤법 오류",
        "spacing": "띄어쓰기 오류",
        "grammar": "문법 오류",
        "expression": "어색한 표현",
        "logic": "논리적 오류"
    }
    
    def __init__(self):
        """문법 검사기 초기화"""
        self.client = None
        
        # OpenAI 클라이언트 초기화
        if OPENAI_AVAILABLE and config.OPENAI_API_KEY:
            try:
                self.client = OpenAI(api_key=config.OPENAI_API_KEY)
            except Exception as e:
                print(f"OpenAI 클라이언트 초기화 실패: {e}")
    
    def check_basic_grammar(self, text: str) -> List[Dict]:
        """
        기본 문법 검사 (py-hanspell 사용)
        
        매개변수:
            text: 검사할 텍스트
        
        반환값:
            오류 리스트 [{"type": "오류유형", "original": "원본", "correction": "수정", "position": 위치}]
        """
        if not text.strip():
            return []
        
        errors = []
        
        try:
            # hanspell 라이브러리로 맞춤법 검사
            result = spell_checker.check(text)
            
            # 결과 파싱
            if result.errors:
                for i, error in enumerate(result.errors):
                    errors.append({
                        "type": "spelling",
                        "original": error[0] if isinstance(error, tuple) else str(error),
                        "correction": error[1] if isinstance(error, tuple) and len(error) > 1 else "",
                        "explanation": "맞춤법 오류",
                        "position": i  # 간단한 위치 정보
                    })
        
        except Exception as e:
            print(f"기본 문법 검사 오류: {e}")
        
        return errors
    
    def check_ai_grammar(self, text: str) -> List[Dict]:
        """
        AI 기반 문법 검사 (OpenAI GPT 사용)
        
        매개변수:
            text: 검사할 텍스트
        
        반환값:
            오류 리스트
        """
        if not self.client or not text.strip():
            return []
        
        errors = []
        
        try:
            # 프롬프트 생성
            prompt = self._build_grammar_prompt(text)
            
            # API 호출
            response = self.client.chat.completions.create(
                model=config.AI_CONFIG["model"],
                messages=[
                    {"role": "system", "content": "당신은 한국어 문법 전문가입니다. 정확하고 간결하게 답변합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.AI_CONFIG["temperature_grammar"],
                max_tokens=config.AI_CONFIG["max_tokens"]
            )
            
            # 응답 파싱
            result_text = response.choices[0].message.content
            errors = self._parse_ai_response(result_text)
        
        except Exception as e:
            print(f"AI 문법 검사 오류: {e}")
        
        return errors
    
    def _build_grammar_prompt(self, text: str) -> str:
        """
        문법 검사용 프롬프트 생성
        
        매개변수:
            text: 검사할 텍스트
        
        반환값:
            프롬프트 문자열
        """
        prompt = f"""다음 한국어 텍스트의 문법 오류를 찾아 수정해주세요:

[텍스트]
{text}

다음 형식으로 답변해주세요 (오류가 없으면 "오류 없음"이라고만 답변):

1. 오류 유형: [맞춤법/문법/띄어쓰기/표현]
   원문: [오류가 있는 부분]
   수정안: [올바른 표현]
   설명: [왜 수정이 필요한지 간단히]

2. ...
"""
        return prompt
    
    def _parse_ai_response(self, response: str) -> List[Dict]:
        """
        AI 응답 파싱
        
        매개변수:
            response: AI 응답 텍스트
        
        반환값:
            파싱된 오류 리스트
        """
        errors = []
        
        if "오류 없음" in response:
            return errors
        
        # 간단한 파싱 (실제로는 더 정교한 파싱 필요)
        lines = response.split('\n')
        current_error = {}
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("오류 유형:"):
                if current_error:
                    errors.append(current_error)
                current_error = {"type": "grammar"}
            
            elif line.startswith("원문:"):
                current_error["original"] = line.replace("원문:", "").strip()
            
            elif line.startswith("수정안:"):
                current_error["correction"] = line.replace("수정안:", "").strip()
            
            elif line.startswith("설명:"):
                current_error["explanation"] = line.replace("설명:", "").strip()
        
        if current_error:
            errors.append(current_error)
        
        return errors
    
    def check_all(self, text: str) -> List[Dict]:
        """
        전체 문법 검사 (기본 + AI)
        
        매개변수:
            text: 검사할 텍스트
        
        반환값:
            모든 오류 리스트
        """
        all_errors = []
        
        # 기본 검사
        basic_errors = self.check_basic_grammar(text)
        all_errors.extend(basic_errors)
        
        # AI 검사 (API 키가 있을 때만)
        if self.client:
            ai_errors = self.check_ai_grammar(text)
            all_errors.extend(ai_errors)
        
        return all_errors
    
    def get_error_type_name(self, error_type: str) -> str:
        """
        오류 유형 코드를 한국어 이름으로 변환
        
        매개변수:
            error_type: 오류 유형 코드
        
        반환값:
            한국어 오류 유형 이름
        """
        return self.ERROR_TYPES.get(error_type, "기타 오류")
