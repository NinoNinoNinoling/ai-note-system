# backend/utils/markdown_parser.py
import re
from typing import List, Dict, Set

class MarkdownParser:
    """마크다운 문서 파싱 및 처리 유틸리티"""
    
    def __init__(self):
        # 정규표현식 패턴들
        self.link_pattern = r'\[\[([^\]]+)\]\]'  # [[노트제목]] 패턴
        self.tag_pattern = r'#(\w+)'  # #태그 패턴
        self.header_pattern = r'^(#{1,6})\s+(.+)$'  # 헤더 패턴
        self.code_block_pattern = r'```[\s\S]*?```'  # 코드 블록 패턴
        self.inline_code_pattern = r'`[^`]+`'  # 인라인 코드 패턴
    
    def extract_links(self, content: str) -> List[str]:
        """마크다운에서 [[링크]] 추출"""
        matches = re.findall(self.link_pattern, content)
        return list(set(matches))  # 중복 제거
    
    def extract_tags(self, content: str) -> List[str]:
        """마크다운에서 #태그 추출"""
        # 코드 블록 내의 태그는 제외
        content_without_code = re.sub(self.code_block_pattern, '', content)
        content_without_code = re.sub(self.inline_code_pattern, '', content_without_code)
        
        matches = re.findall(self.tag_pattern, content_without_code)
        return list(set(matches))  # 중복 제거
    
    def extract_headers(self, content: str) -> List[Dict]:
        """마크다운 헤더 추출"""
        headers = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            match = re.match(self.header_pattern, line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                headers.append({
                    'level': level,
                    'title': title,
                    'line': line_num,
                    'anchor': self.create_anchor(title)
                })
        
        return headers
    
    def create_anchor(self, title: str) -> str:
        """헤더 제목으로부터 앵커 생성"""
        # 한글, 영문, 숫자만 남기고 나머지는 하이픈으로 변경
        anchor = re.sub(r'[^\w가-힣]', '-', title.lower())
        anchor = re.sub(r'-+', '-', anchor)  # 연속된 하이픈 제거
        return anchor.strip('-')
    
    def replace_links_with_urls(self, content: str, note_mapping: Dict[str, int]) -> str:
        """[[링크]]를 실제 URL로 변환"""
        def replace_link(match):
            note_title = match.group(1)
            if note_title in note_mapping:
                note_id = note_mapping[note_title]
                return f'[{note_title}](/notes/{note_id})'
            return f'[{note_title}](#broken-link)'  # 깨진 링크 표시
        
        return re.sub(self.link_pattern, replace_link, content)
    
    def highlight_search_terms(self, content: str, search_terms: List[str]) -> str:
        """검색어 하이라이트"""
        for term in search_terms:
            if term:  # 빈 문자열 방지
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                content = pattern.sub(f'**{term}**', content)
        return content
    
    def get_word_count(self, content: str) -> Dict[str, int]:
        """단어 수 통계"""
        # 코드 블록 제거
        content_without_code = re.sub(self.code_block_pattern, '', content)
        content_without_code = re.sub(self.inline_code_pattern, '', content_without_code)
        
        # 마크다운 문법 제거
        content_clean = re.sub(r'[#*`_\[\]()]', ' ', content_without_code)
        
        # 단어 분리 (한글, 영문 모두 고려)
        korean_words = len(re.findall(r'[가-힣]+', content_clean))
        english_words = len(re.findall(r'[a-zA-Z]+', content_clean))
        numbers = len(re.findall(r'\d+', content_clean))
        
        return {
            'total_characters': len(content),
            'korean_words': korean_words,
            'english_words': english_words,
            'numbers': numbers,
            'total_words': korean_words + english_words,
            'paragraphs': len([p for p in content.split('\n\n') if p.strip()])
        }
    
    def create_table_of_contents(self, content: str) -> str:
        """목차 생성"""
        headers = self.extract_headers(content)
        
        if not headers:
            return ""
        
        toc_lines = ["## 목차\n"]
        
        for header in headers:
            indent = "  " * (header['level'] - 1)
            toc_lines.append(f"{indent}- [{header['title']}](#{header['anchor']})")
        
        return "\n".join(toc_lines) + "\n\n"
    
    def extract_summary(self, content: str, max_length: int = 200) -> str:
        """노트 요약 추출 (첫 문단 기준)"""
        # 코드 블록 제거
        content_without_code = re.sub(self.code_block_pattern, '', content)
        
        # 헤더 제거
        content_without_headers = re.sub(self.header_pattern, '', content_without_code, flags=re.MULTILINE)
        
        # 첫 번째 문단 추출
        paragraphs = [p.strip() for p in content_without_headers.split('\n\n') if p.strip()]
        
        if not paragraphs:
            return "내용이 없습니다."
        
        first_paragraph = paragraphs[0]
        
        # 길이 제한
        if len(first_paragraph) > max_length:
            return first_paragraph[:max_length] + "..."
        
        return first_paragraph
    
    def validate_links(self, content: str, existing_notes: Set[str]) -> List[Dict]:
        """링크 유효성 검사"""
        links = self.extract_links(content)
        validation_results = []
        
        for link in links:
            is_valid = link in existing_notes
            validation_results.append({
                'link': link,
                'valid': is_valid,
                'type': 'existing' if is_valid else 'broken'
            })
        
        return validation_results
    
    def suggest_tags(self, content: str) -> List[str]:
        """내용 기반 태그 제안 (간단한 키워드 추출)"""
        # 기본 키워드들
        tech_keywords = [
            'python', 'javascript', 'flask', 'vue', 'react', 'langchain',
            'ai', 'ml', 'database', 'api', 'frontend', 'backend'
        ]
        
        concept_keywords = [
            '학습', '정리', '개념', '예제', '프로젝트', '아이디어', 
            '메모', '할일', '계획', '목표'
        ]
        
        suggested_tags = []
        content_lower = content.lower()
        
        # 기술 키워드 검사
        for keyword in tech_keywords:
            if keyword in content_lower:
                suggested_tags.append(keyword)
        
        # 개념 키워드 검사
        for keyword in concept_keywords:
            if keyword in content:
                suggested_tags.append(keyword)
        
        return suggested_tags[:5]  # 최대 5개까지
    
    def format_note_preview(self, content: str, max_lines: int = 3) -> str:
        """노트 미리보기 형식으로 변환"""
        lines = content.split('\n')
        preview_lines = []
        
        for line in lines[:max_lines]:
            # 헤더 간소화
            line = re.sub(r'^#+\s*', '▶ ', line)
            # 링크 간소화
            line = re.sub(self.link_pattern, r'→\1', line)
            # 태그 강조
            line = re.sub(self.tag_pattern, r'#\1', line)
            
            if line.strip():
                preview_lines.append(line.strip())
        
        result = ' | '.join(preview_lines)
        
        if len(lines) > max_lines:
            result += " ..."
        
        return result

# 전역 인스턴스
markdown_parser = MarkdownParser()