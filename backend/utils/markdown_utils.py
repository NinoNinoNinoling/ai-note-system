# backend/utils/markdown_utils.py - 실용적인 마크다운 유틸
"""
마크다운 처리 유틸리티

노트 시스템의 핵심 기능들
"""

import re
import html
from typing import List, Dict, Optional


class MarkdownProcessor:
    """마크다운 처리기"""
    
    def __init__(self):
        # 정규표현식 패턴들
        self.link_pattern = r'\[\[([^\]]+)\]\]'  # [[노트링크]]
        self.tag_pattern = r'#(\w+)'  # #태그
        self.header_pattern = r'^(#{1,6})\s+(.+)$'  # 헤더
        self.bold_pattern = r'\*\*(.*?)\*\*'  # **굵은글씨**
        self.italic_pattern = r'\*(.*?)\*'  # *기울임*
        self.code_pattern = r'`([^`]+)`'  # `코드`
        self.strikethrough_pattern = r'~~(.*?)~~'  # ~~취소선~~
    
    def extract_tags(self, content: str) -> List[str]:
        """노트에서 태그 추출"""
        tags = re.findall(self.tag_pattern, content)
        return list(set(tags))  # 중복 제거
    
    def extract_links(self, content: str) -> List[str]:
        """노트에서 [[링크]] 추출"""
        links = re.findall(self.link_pattern, content)
        return list(set(links))  # 중복 제거
    
    def extract_headers(self, content: str) -> List[Dict]:
        """헤더 추출 (목차 생성용)"""
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
                    'anchor': self._create_anchor(title)
                })
        
        return headers
    
    def _create_anchor(self, title: str) -> str:
        """헤더용 앵커 생성"""
        # 한글, 영문, 숫자만 남기고 하이픈으로 변경
        anchor = re.sub(r'[^\w가-힣]', '-', title.lower())
        anchor = re.sub(r'-+', '-', anchor)  # 연속 하이픈 제거
        return anchor.strip('-')
    
    def to_html(self, content: str, note_id_map: Optional[Dict[str, int]] = None) -> str:
        """마크다운을 HTML로 변환 (기본적인 변환)"""
        html_content = html.escape(content)  # XSS 방지
        
        # 헤더 변환
        html_content = re.sub(
            self.header_pattern,
            lambda m: f'<h{len(m.group(1))}>{m.group(2)}</h{len(m.group(1))}>',
            html_content,
            flags=re.MULTILINE
        )
        
        # 텍스트 스타일
        html_content = re.sub(self.bold_pattern, r'<strong>\1</strong>', html_content)
        html_content = re.sub(self.italic_pattern, r'<em>\1</em>', html_content)
        html_content = re.sub(self.strikethrough_pattern, r'<del>\1</del>', html_content)
        html_content = re.sub(self.code_pattern, r'<code>\1</code>', html_content)
        
        # 노트 링크 변환
        if note_id_map:
            html_content = self._convert_note_links(html_content, note_id_map)
        else:
            # ID 맵이 없으면 기본 링크로 변환
            html_content = re.sub(self.link_pattern, r'<a href="#" class="note-link">\1</a>', html_content)
        
        # 태그 변환
        html_content = re.sub(self.tag_pattern, r'<span class="tag">#\1</span>', html_content)
        
        # 줄바꿈 변환
        html_content = html_content.replace('\n', '<br>')
        
        return html_content
    
    def _convert_note_links(self, content: str, note_id_map: Dict[str, int]) -> str:
        """[[노트링크]]를 실제 URL로 변환"""
        def replace_link(match):
            note_title = match.group(1)
            if note_title in note_id_map:
                note_id = note_id_map[note_title]
                return f'<a href="/notes/{note_id}" class="note-link">{note_title}</a>'
            return f'<a href="#" class="broken-link" title="노트를 찾을 수 없습니다">{note_title}</a>'
        
        return re.sub(self.link_pattern, replace_link, content)
    
    def create_preview(self, content: str, max_length: int = 200) -> str:
        """노트 미리보기 생성"""
        # 마크다운 문법 제거
        text = re.sub(self.header_pattern, r'\2', content, flags=re.MULTILINE)  # 헤더
        text = re.sub(self.bold_pattern, r'\1', text)  # 굵은글씨
        text = re.sub(self.italic_pattern, r'\1', text)  # 기울임
        text = re.sub(self.code_pattern, r'\1', text)  # 코드
        text = re.sub(self.link_pattern, r'\1', text)  # 링크
        text = re.sub(self.tag_pattern, r'#\1', text)  # 태그
        
        # 여러 줄바꿈을 하나로
        text = re.sub(r'\n+', ' ', text)
        
        # 여러 공백을 하나로
        text = re.sub(r'\s+', ' ', text)
        
        # 길이 제한
        text = text.strip()
        if len(text) > max_length:
            text = text[:max_length] + '...'
        
        return text
    
    def highlight_search_terms(self, content: str, search_terms: List[str]) -> str:
        """검색어 하이라이트"""
        for term in search_terms:
            if term and len(term) > 1:  # 1글자 이상만 하이라이트
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                content = pattern.sub(f'<mark>{term}</mark>', content)
        return content
    
    def get_word_count(self, content: str) -> Dict[str, int]:
        """단어 수 통계"""
        # 마크다운 문법 제거
        clean_text = re.sub(self.header_pattern, r'\2', content, flags=re.MULTILINE)
        clean_text = re.sub(self.bold_pattern, r'\1', clean_text)
        clean_text = re.sub(self.italic_pattern, r'\1', clean_text)
        clean_text = re.sub(self.code_pattern, r'\1', clean_text)
        clean_text = re.sub(self.link_pattern, r'\1', clean_text)
        clean_text = re.sub(self.tag_pattern, r'\1', clean_text)
        
        # 통계 계산
        total_chars = len(content)
        korean_chars = len(re.findall(r'[가-힣]', clean_text))
        english_words = len(re.findall(r'[a-zA-Z]+', clean_text))
        lines = len(content.split('\n'))
        
        return {
            'total_characters': total_chars,
            'korean_characters': korean_chars,
            'english_words': english_words,
            'total_lines': lines,
            'paragraphs': len([p for p in content.split('\n\n') if p.strip()])
        }
    
    def suggest_tags_from_content(self, content: str) -> List[str]:
        """내용 기반 태그 제안"""
        suggestions = []
        content_lower = content.lower()
        
        # 기술 키워드
        tech_keywords = {
            'python': ['python', 'flask', 'django'],
            'javascript': ['javascript', 'js', 'vue', 'react', 'node'],
            'web': ['html', 'css', 'web', '웹'],
            'ai': ['ai', 'ml', 'langchain', 'claude', 'openai'],
            'database': ['database', 'sql', 'mysql', 'sqlite', 'db']
        }
        
        for tag, keywords in tech_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                suggestions.append(tag)
        
        # 개념 키워드
        concept_keywords = {
            '학습': ['학습', '공부', 'study', 'learn'],
            '정리': ['정리', '요약', 'summary'],
            '아이디어': ['아이디어', 'idea', '계획', 'plan'],
            '메모': ['메모', 'memo', '기록'],
            '프로젝트': ['프로젝트', 'project', '개발']
        }
        
        for tag, keywords in concept_keywords.items():
            if any(keyword in content for keyword in keywords):
                suggestions.append(tag)
        
        return suggestions[:5]  # 최대 5개까지


class NoteLinker:
    """노트 간 연결 관리"""
    
    def __init__(self):
        self.processor = MarkdownProcessor()
    
    def find_linked_notes(self, content: str) -> List[str]:
        """노트에서 링크된 다른 노트들 찾기"""
        return self.processor.extract_links(content)
    
    def find_backlinks(self, note_title: str, all_notes: List[Dict]) -> List[Dict]:
        """특정 노트를 링크하는 다른 노트들 찾기 (백링크)"""
        backlinks = []
        
        for note in all_notes:
            links = self.processor.extract_links(note['content'])
            if note_title in links:
                backlinks.append({
                    'id': note['id'],
                    'title': note['title'],
                    'preview': self.processor.create_preview(note['content'], 100)
                })
        
        return backlinks
    
    def create_note_graph(self, all_notes: List[Dict]) -> Dict:
        """노트 간 연결 그래프 생성"""
        nodes = []
        edges = []
        
        # 노드 생성
        for note in all_notes:
            nodes.append({
                'id': note['id'],
                'title': note['title'],
                'tags': note.get('tags', []),
                'word_count': len(note['content'])
            })
        
        # 엣지 생성 (링크 관계)
        for note in all_notes:
            links = self.processor.extract_links(note['content'])
            for link in links:
                # 링크된 노트 찾기
                target_note = next((n for n in all_notes if n['title'] == link), None)
                if target_note:
                    edges.append({
                        'source': note['id'],
                        'target': target_note['id'],
                        'type': 'link'
                    })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'stats': {
                'total_notes': len(nodes),
                'total_links': len(edges),
                'orphaned_notes': len([n for n in nodes if not any(e['source'] == n['id'] or e['target'] == n['id'] for e in edges)])
            }
        }


# 전역 인스턴스
markdown_processor = MarkdownProcessor()
note_linker = NoteLinker()


# 편의 함수들
def process_markdown_content(content: str, note_id_map: Optional[Dict[str, int]] = None) -> Dict:
    """마크다운 내용 종합 처리"""
    return {
        'html': markdown_processor.to_html(content, note_id_map),
        'preview': markdown_processor.create_preview(content),
        'tags': markdown_processor.extract_tags(content),
        'links': markdown_processor.extract_links(content),
        'headers': markdown_processor.extract_headers(content),
        'word_count': markdown_processor.get_word_count(content),
        'suggested_tags': markdown_processor.suggest_tags_from_content(content)
    }


def search_in_markdown(content: str, search_terms: List[str]) -> Dict:
    """마크다운에서 검색 및 하이라이트"""
    highlighted = content
    for term in search_terms:
        highlighted = markdown_processor.highlight_search_terms(highlighted, [term])
    
    return {
        'original': content,
        'highlighted': highlighted,
        'preview': markdown_processor.create_preview(highlighted, 300)
    }