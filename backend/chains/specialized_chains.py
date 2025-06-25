# backend/chains/specialized_chains.py
"""
LangChain Multiple Chains - 프로덕션 전용

전문화된 체인들:
1. SummarizationChain - 노트 요약 
2. AnalysisChain - 노트 분석 및 인사이트
3. RecommendationChain - 관련 노트 추천
4. ImprovementChain - 노트 개선 제안

✅ 테스트 코드 완전 분리됨 (tests/test_chains.py에서 관리)
✅ 프로덕션 최적화 완료
"""

import os
from typing import List, Dict, Optional
from datetime import datetime

try:
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    from langchain.schema import HumanMessage, SystemMessage
    from langchain_anthropic import ChatAnthropic
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from config.settings import Config


class BaseSpecializedChain:
    """전문화된 체인들의 기본 클래스"""
    
    def __init__(self, chain_name: str):
        self.chain_name = chain_name
        self.available = LANGCHAIN_AVAILABLE
        
        if not self.available:
            return
            
        try:
            # Claude 모델 초기화
            self.llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                api_key=Config.ANTHROPIC_API_KEY,
                temperature=0.3
            )
            
        except Exception as e:
            self.available = False
    
    def is_available(self) -> bool:
        """체인 사용 가능 여부"""
        return self.available and hasattr(self, 'llm')
    
    def create_prompt_template(self, template: str) -> PromptTemplate:
        """프롬프트 템플릿 생성"""
        return PromptTemplate(
            input_variables=["content", "context"],
            template=template
        )


class SummarizationChain(BaseSpecializedChain):
    """노트 요약 체인"""
    
    def __init__(self):
        super().__init__("SummarizationChain")
        
        if not self.available:
            return
            
        self.prompt_template = self.create_prompt_template("""
당신은 전문적인 노트 요약 도우미입니다.

주어진 노트를 간결하고 핵심적으로 요약해주세요.

요약 규칙:
1. 핵심 내용만 추출
2. 3-5개의 bullet point로 구성
3. 마크다운 형식 사용
4. 중요한 키워드는 **볼드** 처리

컨텍스트 정보: {context}

요약할 노트:
{content}

요약:
""")
        
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            verbose=False  # 프로덕션에서는 verbose=False
        )
    
    def summarize_note(self, content: str, context: str = "") -> Dict:
        """노트 요약"""
        if not self.is_available():
            return {"error": "SummarizationChain 사용 불가"}
        
        try:
            result = self.chain.run(
                content=content,
                context=context
            )
            
            return {
                "success": True,
                "summary": result.strip(),
                "chain_type": "summarization",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"요약 생성 실패: {str(e)}"
            }
    
    def summarize_multiple_notes(self, notes: List[Dict]) -> Dict:
        """여러 노트 일괄 요약"""
        if not self.is_available():
            return {"error": "SummarizationChain 사용 불가"}
        
        summaries = []
        
        for note in notes:
            summary_result = self.summarize_note(
                content=note.get('content', ''),
                context=f"제목: {note.get('title', '')}"
            )
            
            if summary_result.get('success'):
                summaries.append({
                    "note_id": note.get('id'),
                    "title": note.get('title'),
                    "summary": summary_result['summary']
                })
        
        return {
            "success": True,
            "summaries": summaries,
            "total_notes": len(notes),
            "summarized_notes": len(summaries)
        }


class AnalysisChain(BaseSpecializedChain):
    """노트 분석 체인"""
    
    def __init__(self):
        super().__init__("AnalysisChain")
        
        if not self.available:
            return
            
        self.prompt_template = self.create_prompt_template("""
당신은 전문적인 노트 분석가입니다.

주어진 노트를 깊이 있게 분석하고 인사이트를 제공해주세요.

분석 항목:
1. **주요 주제**: 핵심 토픽 3개
2. **지식 레벨**: 초급/중급/고급
3. **완성도**: 부족한 부분 지적
4. **연관 분야**: 관련된 다른 주제들
5. **학습 포인트**: 추가 학습 방향

컨텍스트 정보: {context}

분석할 노트:
{content}

분석 결과:
""")
        
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            verbose=False
        )
    
    def analyze_note(self, content: str, context: str = "") -> Dict:
        """노트 분석"""
        if not self.is_available():
            return {"error": "AnalysisChain 사용 불가"}
        
        try:
            result = self.chain.run(
                content=content,
                context=context
            )
            
            return {
                "success": True,
                "analysis": result.strip(),
                "chain_type": "analysis",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"분석 생성 실패: {str(e)}"
            }
    
    def get_knowledge_gaps(self, notes: List[Dict]) -> Dict:
        """여러 노트에서 지식 공백 찾기"""
        if not self.is_available():
            return {"error": "AnalysisChain 사용 불가"}
        
        # 모든 노트를 하나의 컨텍스트로 합치기
        combined_content = "\n\n---\n\n".join([
            f"# {note.get('title', '')}\n{note.get('content', '')}"
            for note in notes
        ])
        
        gap_prompt = f"""
다음 노트들을 분석해서 지식 공백과 부족한 부분을 찾아주세요:

{combined_content}

분석해서 다음을 제공해주세요:
1. **부족한 주제들**: 언급되지 않은 중요한 개념들
2. **연결 고리**: 노트들 사이의 연관성 부족
3. **깊이 부족**: 더 자세히 다뤄야 할 부분
4. **추천 학습**: 다음에 공부하면 좋을 주제들
"""
        
        try:
            messages = [
                SystemMessage(content="당신은 학습 전문가입니다."),
                HumanMessage(content=gap_prompt)
            ]
            
            result = self.llm(messages)
            
            return {
                "success": True,
                "knowledge_gaps": result.content,
                "total_notes_analyzed": len(notes)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"지식 공백 분석 실패: {str(e)}"
            }


class RecommendationChain(BaseSpecializedChain):
    """관련 노트 추천 체인"""
    
    def __init__(self):
        super().__init__("RecommendationChain")
        
        if not self.available:
            return
            
        self.prompt_template = self.create_prompt_template("""
당신은 개인화된 학습 추천 전문가입니다.

사용자의 현재 노트를 기반으로 관련 노트나 학습 방향을 추천해주세요.

추천 기준:
1. **관련성**: 현재 노트와 연관된 주제
2. **발전성**: 다음 단계로 학습할 내용
3. **보완성**: 부족한 부분을 채울 내용
4. **실용성**: 실제 활용 가능한 지식

컨텍스트 (기존 노트들): {context}

현재 노트:
{content}

추천 결과:
""")
        
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            verbose=False
        )
    
    def recommend_related_notes(self, current_note: str, existing_notes: List[Dict]) -> Dict:
        """관련 노트 추천"""
        if not self.is_available():
            return {"error": "RecommendationChain 사용 불가"}
        
        # 기존 노트들을 컨텍스트로 구성
        context = "\n".join([
            f"- {note.get('title', '')}: {note.get('content', '')[:100]}..."
            for note in existing_notes[:10]  # 최대 10개만
        ])
        
        try:
            result = self.chain.run(
                content=current_note,
                context=context
            )
            
            return {
                "success": True,
                "recommendations": result.strip(),
                "chain_type": "recommendation",
                "based_on_notes": len(existing_notes),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"추천 생성 실패: {str(e)}"
            }
    
    def suggest_note_topics(self, user_interests: List[str], existing_notes: List[Dict]) -> Dict:
        """새로운 노트 주제 제안"""
        if not self.is_available():
            return {"error": "RecommendationChain 사용 불가"}
        
        interests_text = ", ".join(user_interests)
        existing_topics = [note.get('title', '') for note in existing_notes]
        
        suggestion_prompt = f"""
사용자 관심사: {interests_text}
기존 노트 주제들: {', '.join(existing_topics)}

위 정보를 바탕으로 새로운 노트 주제 5개를 추천해주세요.
각 주제마다 간단한 설명과 왜 유용한지 이유를 포함해주세요.

형식:
## 추천 주제 1: 제목
- 설명: ...
- 유용한 이유: ...
"""
        
        try:
            messages = [
                SystemMessage(content="당신은 학습 컨텐츠 기획 전문가입니다."),
                HumanMessage(content=suggestion_prompt)
            ]
            
            result = self.llm(messages)
            
            return {
                "success": True,
                "topic_suggestions": result.content,
                "user_interests": user_interests,
                "existing_notes_count": len(existing_notes)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"주제 제안 실패: {str(e)}"
            }


class ImprovementChain(BaseSpecializedChain):
    """노트 개선 체인"""
    
    def __init__(self):
        super().__init__("ImprovementChain")
        
        if not self.available:
            return
            
        self.prompt_template = self.create_prompt_template("""
당신은 노트 작성 전문가입니다.

주어진 노트를 개선하는 구체적인 방법을 제안해주세요.

개선 영역:
1. **구조 개선**: 더 나은 정리 방법
2. **내용 보강**: 추가하면 좋을 내용
3. **가독성**: 마크다운 활용 개선
4. **실용성**: 더 유용하게 만드는 방법
5. **연결성**: 다른 개념과의 연결

컨텍스트: {context}

개선할 노트:
{content}

개선 제안:
""")
        
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            verbose=False
        )
    
    def improve_note(self, content: str, context: str = "") -> Dict:
        """노트 개선 제안"""
        if not self.is_available():
            return {"error": "ImprovementChain 사용 불가"}
        
        try:
            result = self.chain.run(
                content=content,
                context=context
            )
            
            return {
                "success": True,
                "improvements": result.strip(),
                "chain_type": "improvement",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"개선 제안 실패: {str(e)}"
            }
    
    def rewrite_note(self, content: str, improvement_style: str = "detailed") -> Dict:
        """노트 다시 작성"""
        if not self.is_available():
            return {"error": "ImprovementChain 사용 불가"}
        
        style_prompts = {
            "detailed": "더 자세하고 구체적으로",
            "concise": "더 간결하고 핵심적으로", 
            "structured": "더 체계적이고 논리적으로",
            "practical": "더 실용적이고 예시 중심으로"
        }
        
        rewrite_prompt = f"""
다음 노트를 {style_prompts.get(improvement_style, "더 좋게")} 다시 작성해주세요:

원본 노트:
{content}

다시 작성된 노트:
"""
        
        try:
            messages = [
                SystemMessage(content="당신은 전문 기술 문서 작성자입니다."),
                HumanMessage(content=rewrite_prompt)
            ]
            
            result = self.llm(messages)
            
            return {
                "success": True,
                "rewritten_note": result.content,
                "improvement_style": improvement_style,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"노트 재작성 실패: {str(e)}"
            }


class ChainManager:
    """Multiple Chains를 관리하는 중앙 클래스"""
    
    def __init__(self):
        self.chains = {}
        self.initialize_chains()
    
    def initialize_chains(self):
        """모든 체인 초기화"""
        try:
            self.chains['summarization'] = SummarizationChain()
            self.chains['analysis'] = AnalysisChain()
            self.chains['recommendation'] = RecommendationChain()
            self.chains['improvement'] = ImprovementChain()
            
        except Exception as e:
            pass  # 프로덕션에서는 조용히 실패
    
    def get_chain(self, chain_type: str):
        """특정 체인 반환"""
        return self.chains.get(chain_type)
    
    def is_available(self, chain_type: str) -> bool:
        """특정 체인 사용 가능 여부"""
        chain = self.get_chain(chain_type)
        return chain and chain.is_available()
    
    def get_available_chains(self) -> List[str]:
        """사용 가능한 체인 목록"""
        return [
            name for name, chain in self.chains.items()
            if chain.is_available()
        ]
    
    def get_chains_info(self) -> Dict:
        """모든 체인 정보"""
        return {
            "total_chains": len(self.chains),
            "available_chains": self.get_available_chains(),
            "chains_status": {
                name: chain.is_available()
                for name, chain in self.chains.items()
            },
            "langchain_available": LANGCHAIN_AVAILABLE
        }


# =========================
# 전역 인스턴스 및 편의 함수
# =========================

# 전역 체인 매니저 인스턴스
chain_manager = ChainManager()


# 편의 함수들
def summarize_note(content: str, context: str = "") -> Dict:
    """노트 요약 (편의 함수)"""
    chain = chain_manager.get_chain('summarization')
    if not chain or not chain.is_available():
        return {"error": "SummarizationChain 사용 불가"}
    return chain.summarize_note(content, context)


def analyze_note(content: str, context: str = "") -> Dict:
    """노트 분석 (편의 함수)"""
    chain = chain_manager.get_chain('analysis')
    if not chain or not chain.is_available():
        return {"error": "AnalysisChain 사용 불가"}
    return chain.analyze_note(content, context)


def recommend_notes(current_note: str, existing_notes: List[Dict]) -> Dict:
    """관련 노트 추천 (편의 함수)"""
    chain = chain_manager.get_chain('recommendation')
    if not chain or not chain.is_available():
        return {"error": "RecommendationChain 사용 불가"}
    return chain.recommend_related_notes(current_note, existing_notes)


def improve_note(content: str, context: str = "") -> Dict:
    """노트 개선 제안 (편의 함수)"""
    chain = chain_manager.get_chain('improvement')
    if not chain or not chain.is_available():
        return {"error": "ImprovementChain 사용 불가"}
    return chain.improve_note(content, context)


# CHAINS_AVAILABLE 설정 (프로덕션용)
CHAINS_AVAILABLE = LANGCHAIN_AVAILABLE and any(
    chain_manager.is_available(chain_type) 
    for chain_type in ['summarization', 'analysis', 'recommendation', 'improvement']
)


# Export 목록
__all__ = [
    'LANGCHAIN_AVAILABLE',
    'CHAINS_AVAILABLE',
    'chain_manager',
    'summarize_note',
    'analyze_note',
    'recommend_notes',
    'improve_note',
    'BaseSpecializedChain',
    'SummarizationChain',
    'AnalysisChain', 
    'RecommendationChain',
    'ImprovementChain',
    'ChainManager'
]