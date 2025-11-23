"""
문장 제안 모듈

역할:
- 현재 맥락을 분석하여 다음 문장 제안
- 여러 옵션 제공 (다양한 방향성)
- 논리 구조 분석 및 제안

주요 기능:
1. suggest_next_sentence(): 다음 문장 제안
2. analyze_logic(): 논리 구조 분석
3. get_writing_tips(): 글쓰기 팁 제공

유지보수 방법:
- 프롬프트 개선: _build_suggestion_prompt() 메서드 수정
- 제안 개수 변경: config.SUGGESTION["max_suggestions"] 조정
- 새로운 제안 타입 추가: SUGGESTION_TYPES 딕셔너리 수정
"""

from typing import List, Dict, Optional
import config

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class SentenceSuggester:
    """문장 제안 클래스"""
    
    # 제안 타입
    SUGGESTION_TYPES = {
        "continue": "이어가기",
        "elaborate": "구체화하기",
        "conclude": "결론짓기",
        "contrast": "대조하기",
        "example": "예시 들기"
    }
    
    def __init__(self):
        """문장 제안기 초기화"""
        self.client = None
        
        if OPENAI_AVAILABLE and config.OPENAI_API_KEY:
            try:
                self.client = OpenAI(api_key=config.OPENAI_API_KEY)
            except Exception as e:
                print(f"OpenAI 클라이언트 초기화 실패: {e}")
    
    def suggest_next_sentence(self, context: str, num_suggestions: int = 3) -> List[str]:
        """
        다음 문장 제안
        
        매개변수:
            context: 현재까지 작성된 텍스트
            num_suggestions: 제안 개수 (기본값: 3)
        
        반환값:
            제안 문장 리스트
        """
        if not self.client or not context.strip():
            return self._get_fallback_suggestions()
        
        try:
            prompt = self._build_suggestion_prompt(context, num_suggestions)
            
            response = self.client.chat.completions.create(
                model=config.AI_CONFIG["model"],
                messages=[
                    {"role": "system", "content": "당신은 창의적인 글쓰기 도우미입니다. 자연스럽고 논리적인 문장을 제안합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.AI_CONFIG["temperature_suggest"],
                max_tokens=config.AI_CONFIG["max_tokens"]
            )
            
            suggestions_text = response.choices[0].message.content
            suggestions = self._parse_suggestions(suggestions_text)
            
            return suggestions if suggestions else self._get_fallback_suggestions()
        
        except Exception as e:
            print(f"문장 제안 오류: {e}")
            return self._get_fallback_suggestions()
    
    def _build_suggestion_prompt(self, context: str, num: int) -> str:
        """
        문장 제안용 프롬프트 생성
        
        매개변수:
            context: 현재 텍스트
            num: 제안 개수
        
        반환값:
            프롬프트 문자열
        """
        prompt = f"""다음은 사용자가 작성 중인 글입니다:

[현재 글]
{context}

이 글의 맥락을 고려하여 다음에 올 수 있는 문장을 {num}가지 제안해주세요.
각 제안은 서로 다른 방향성을 가져야 합니다.

형식:
1. [첫 번째 제안 문장]
2. [두 번째 제안 문장]
3. [세 번째 제안 문장]

제안만 작성하고 다른 설명은 추가하지 마세요.
"""
        return prompt
    
    def _parse_suggestions(self, text: str) -> List[str]:
        """
        AI 응답에서 제안 문장 추출
        
        매개변수:
            text: AI 응답 텍스트
        
        반환값:
            제안 문장 리스트
        """
        suggestions = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # 숫자로 시작하는 줄 찾기
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # 번호 제거
                clean_line = line.lstrip('0123456789.-•) ').strip()
                if clean_line:
                    suggestions.append(clean_line)
        
        return suggestions
    
    def _get_fallback_suggestions(self) -> List[str]:
        """
        API 사용 불가 시 기본 제안
        
        반환값:
            기본 제안 리스트
        """
        return [
            "이와 관련하여 더 구체적인 예시를 들어보겠습니다.",
            "다른 관점에서 살펴보면 어떨까요?",
            "결론적으로 말하자면 이러한 점을 고려해야 합니다."
        ]
    
    def analyze_logic(self, text: str) -> Dict:
        """
        텍스트의 논리 구조 분석
        
        매개변수:
            text: 분석할 텍스트
        
        반환값:
            논리 분석 결과 딕셔너리
        """
        if not self.client or not text.strip():
            return self._get_basic_logic_analysis(text)
        
        try:
            prompt = self._build_logic_prompt(text)
            
            response = self.client.chat.completions.create(
                model=config.AI_CONFIG["model"],
                messages=[
                    {"role": "system", "content": "당신은 논리적 글쓰기 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.AI_CONFIG["temperature_grammar"],
                max_tokens=config.AI_CONFIG["max_tokens"]
            )
            
            analysis_text = response.choices[0].message.content
            return self._parse_logic_analysis(analysis_text)
        
        except Exception as e:
            print(f"논리 분석 오류: {e}")
            return self._get_basic_logic_analysis(text)
    
    def _build_logic_prompt(self, text: str) -> str:
        """
        논리 분석용 프롬프트 생성
        
        매개변수:
            text: 분석할 텍스트
        
        반환값:
            프롬프트 문자열
        """
        prompt = f"""다음 텍스트의 논리 구조를 분석해주세요:

[텍스트]
{text}

다음 항목들을 분석해주세요:
1. 주장: 글의 핵심 주장
2. 근거: 주장을 뒷받침하는 근거
3. 논리적 흐름: 문장 간 연결이 자연스러운지
4. 개선점: 논리적으로 보완이 필요한 부분

간단명료하게 답변해주세요.
"""
        return prompt
    
    def _parse_logic_analysis(self, text: str) -> Dict:
        """
        논리 분석 응답 파싱
        
        매개변수:
            text: AI 응답
        
        반환값:
            분석 결과 딕셔너리
        """
        return {
            "analysis": text,
            "has_issues": "개선" in text or "부족" in text,
            "suggestions": []
        }
    
    def _get_basic_logic_analysis(self, text: str) -> Dict:
        """
        기본 논리 분석 (API 없이)
        
        매개변수:
            text: 분석할 텍스트
        
        반환값:
            기본 분석 결과
        """
        sentences = text.split('.')
        sentence_count = len([s for s in sentences if s.strip()])
        
        return {
            "analysis": f"총 {sentence_count}개의 문장으로 구성되어 있습니다.",
            "has_issues": False,
            "suggestions": []
        }
    
    def get_writing_tips(self, context: str) -> List[str]:
        """
        현재 글에 대한 글쓰기 팁 제공
        
        매개변수:
            context: 현재 텍스트
        
        반환값:
            팁 리스트
        """
        tips = []
        
        # 간단한 규칙 기반 팁
        if len(context.strip()) < 50:
            tips.append("더 구체적인 내용을 추가해보세요.")
        
        sentences = context.split('.')
        if len(sentences) > 5:
            avg_length = sum(len(s) for s in sentences) / len(sentences)
            if avg_length > 100:
                tips.append("문장이 너무 길 수 있습니다. 짧게 나누는 것을 고려해보세요.")
        
        if not tips:
            tips.append("좋은 글입니다. 계속 작성하세요!")
        
        return tips
